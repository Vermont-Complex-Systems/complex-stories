import dagster as dg
from dagster_duckdb import DuckDBResource
from pathlib import Path

# Path to your static data directory
STATIC_DATA_PATH = Path("../../../../../static/data") 

@dg.asset(
    kinds={"export"},
    deps=["yearly_collaborations", "coauthor_institutions", "coauthor_cache"], 
    key=["exports", "coauthor_parquet"]
)
def coauthor_parquet(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """Export final coauthor collaboration data as parquet for static frontend"""
    
    with duckdb.get_connection() as conn:
        conn.execute(f"""
            COPY (
            WITH base_data AS (
                SELECT 
                    yc.*,
                    -- Pre-calculate ego and coauthor first publication years
                    COALESCE(prof.first_pub_year, cc.first_publication_year) as ego_first_pub_year,
                    cc.first_publication_year as coauth_first_pub_year,
                    
                    -- Include other joined data you need
                    prof.first_pub_year as prof_first_pub_year_raw,
                    ci_uvm.primary_institution,
                    ci_external.primary_institution as coauth_institution
                    
                FROM oa.main.yearly_collaborations yc
                LEFT JOIN oa.main.uvm_profs_2023 prof 
                    ON replace(yc.uvm_professor_id, 'https://openalex.org/', '') = prof.oa_uid
                LEFT JOIN oa.main.coauthor_cache cc 
                    ON yc.coauthor_id = cc.author_oa_id
                LEFT JOIN oa.main.coauthor_institutions ci_uvm 
                    ON yc.uvm_professor_id = replace(ci_uvm.coauthor_id , 'https://openalex.org/', '')
                    AND yc.publication_year = ci_uvm.publication_year
                LEFT JOIN oa.main.coauthor_institutions ci_external 
                    ON yc.coauthor_id = ci_external.coauthor_id
                    AND yc.publication_year = ci_external.publication_year
            )

            SELECT 
                -- UVM profs information
                uvm_professor_id as aid, 
                uvm_professor_name as name, 
                publication_year, 
                nb_coauthors, 
                coauthor_id,
                
                -- Clean age calculations using pre-computed values
                ego_first_pub_year,
                coauth_first_pub_year,
                
                -- Age calculations (much cleaner now!)
                CASE 
                    WHEN ego_first_pub_year IS NOT NULL 
                    THEN (publication_year - ego_first_pub_year)
                    ELSE NULL 
                END as ego_age,
                
                CASE 
                    WHEN coauth_first_pub_year IS NOT NULL 
                    THEN (publication_year - coauth_first_pub_year)
                    ELSE NULL 
                END as coauth_age,
                
                -- Age difference (simple and clear)
                CASE 
                    WHEN ego_first_pub_year IS NOT NULL AND coauth_first_pub_year IS NOT NULL
                    THEN (coauth_first_pub_year - ego_first_pub_year)
                    ELSE NULL 
                END as age_difference,
                
                -- Age category (clean calculation using the logic from your original query)
                CASE 
                    WHEN ego_first_pub_year IS NOT NULL AND coauth_first_pub_year IS NOT NULL THEN
                        CASE 
                            WHEN (publication_year - ego_first_pub_year) - (publication_year - coauth_first_pub_year) > 7 THEN 'younger'
                            WHEN (publication_year - ego_first_pub_year) - (publication_year - coauth_first_pub_year) < -7 THEN 'older'
                            ELSE 'same'
                        END
                    ELSE 'unknown'
                END as age_category,
                
                -- Publication info with jitter
                publication_date + INTERVAL (FLOOR(RANDOM() * 28) + 1) DAYS as publication_date,
                
                -- Collaboration metrics
                yearly_collabo,
                SUM(yearly_collabo) OVER (
                    PARTITION BY uvm_professor_id, coauthor_id 
                    ORDER BY publication_year 
                    ROWS UNBOUNDED PRECEDING
                ) as all_times_collabo,
                
                -- Institution info
                primary_institution as institution,
                coauth_institution,
                
                CASE 
                    WHEN primary_institution IS NOT NULL 
                        AND coauth_institution IS NOT NULL
                        AND primary_institution = coauth_institution
                        THEN primary_institution
                        ELSE NULL 
                END as shared_institutions

            FROM base_data
            ) TO '{STATIC_DATA_PATH}/coauthor.parquet' (FORMAT PARQUET)
        """)

        return dg.MaterializeResult(
        metadata={
            "export_path": str(STATIC_DATA_PATH / "coauthor.parquet"),
        }
    )


