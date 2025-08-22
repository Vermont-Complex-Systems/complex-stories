import dagster as dg
from dagster_duckdb import DuckDBResource
from pathlib import Path

# Path to your static data directory
STATIC_DATA_PATH = Path("../../../../../static/data") 

@dg.asset(
    kinds={"export"},
    deps=["yearly_collaborations", "coauthor_institutions", "coauthor_cache"], 
)
def coauthor_parquet(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """Export final coauthor collaboration data as parquet for static frontend"""
    
    with duckdb.get_connection() as conn:
        # import duckdb
        # conn=duckdb.connect("/tmp/oa.duckdb")
        conn.execute(f"""
            COPY (
            WITH base_data AS (
                SELECT 
                    yc.*,
                    -- Pre-calculate ego and coauthor first publication years (clean coalescing)
                    COALESCE(prof.first_pub_year, cc_uvm.first_pub_year) as ego_first_pub_year,
                    cc_external.first_pub_year as coauthor_first_pub_year,
                    
                    -- Include other fields from joins
                    prof.first_pub_year as prof_first_pub_year_raw,
                    prof.department as ego_department,
                    ci_uvm.primary_institution,
                    ci_external.primary_institution as coauthor_institution
                    
                FROM oa.transform.yearly_collaborations yc
                LEFT JOIN oa.raw.uvm_profs_2023 prof 
                    ON yc.ego_author_id = prof.ego_author_id
                LEFT JOIN oa.cache.coauthor_cache cc_external
                    ON yc.coauthor_id = cc_external.id
                
                LEFT JOIN oa.cache.coauthor_cache cc_uvm 
                    ON yc.ego_author_id = cc_uvm.id
                
                LEFT JOIN oa.transform.coauthor_institutions ci_uvm 
                    ON yc.ego_author_id = ci_uvm.id
                    AND yc.publication_year = ci_uvm.publication_year
                
                LEFT JOIN oa.transform.coauthor_institutions ci_external 
                    ON yc.coauthor_id = ci_external.id
                    AND yc.publication_year = ci_external.publication_year
            ),

            age_calculations AS (
                SELECT 
                    *,
                    CASE 
                        WHEN ego_first_pub_year IS NOT NULL 
                        THEN (publication_year - ego_first_pub_year)
                        ELSE NULL 
                    END as ego_age,
                    
                    CASE 
                        WHEN coauthor_first_pub_year IS NOT NULL 
                        THEN (publication_year - coauthor_first_pub_year)
                        ELSE NULL 
                    END as coauthor_age
                    
                FROM base_data
            )
         SELECT 
                -- UVM professor information  
                ego_author_id,
                ego_display_name,
                ego_department,
                publication_year,
                nb_coauthors,
                
                -- Publication info with jitter
                publication_date + INTERVAL (FLOOR(RANDOM() * 28) + 1) DAYS as publication_date,
                
                -- Ego author information
                ego_first_pub_year,
                ego_age,
                
                -- Coauthor information
                coauthor_id,
                coauthor_display_name,
                coauthor_age,
                coauthor_first_pub_year,
                
                -- Let pandas calculate age_diff later
                (ego_age - coauthor_age) as age_diff,
                
                CASE 
                    WHEN ego_age IS NOT NULL AND coauthor_age IS NOT NULL THEN
                        CASE 
                            WHEN (ego_age - coauthor_age) > 7 THEN 'younger'
                            WHEN (ego_age - coauthor_age) < -7 THEN 'older'
                            ELSE 'same'
                        END
                    ELSE 'unknown'
                END as age_category,
                        
                -- Collaboration metrics
                yearly_collabo,
                SUM(yearly_collabo) OVER (
                    PARTITION BY ego_author_id, coauthor_id 
                    ORDER BY publication_year 
                    ROWS UNBOUNDED PRECEDING
                ) as all_times_collabo,
                
                -- Institution information
                primary_institution,
                coauthor_institution,
                
                CASE 
                    WHEN primary_institution IS NOT NULL 
                        AND coauthor_institution IS NOT NULL
                        AND primary_institution = coauthor_institution
                        THEN primary_institution
                        ELSE NULL 
                END as shared_institutions

            FROM age_calculations
            ORDER BY publication_year
        ) TO '{STATIC_DATA_PATH}/coauthor.parquet' (FORMAT PARQUET)
        """)

        return dg.MaterializeResult(
            metadata={
                "export_path": str(STATIC_DATA_PATH / "coauthor.parquet"),
            }
    )


