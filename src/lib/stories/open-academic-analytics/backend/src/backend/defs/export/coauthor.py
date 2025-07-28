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
    
    # Ensure the static data directory exists
    STATIC_DATA_PATH.mkdir(parents=True, exist_ok=True)
    
    with duckdb.get_connection() as conn:
        # Export the final joined data
        conn.execute(f"""
            COPY (
                WITH uvm_calc AS (
                    SELECT 
                        a.author_oa_id,
                        MIN(p.publication_year) as calculated_first_year
                    FROM oa.main.authorships a
                    JOIN oa.main.publications p ON a.work_id = p.id
                    WHERE a.author_oa_id IN (SELECT 'https://openalex.org/' || oa_uid FROM oa.main.uvm_profs_2023)
                    GROUP BY a.author_oa_id
                )
                SELECT 
                    -- Publication info with jitter
                    yc.publication_year,
                    yc.publication_date + INTERVAL (FLOOR(RANDOM() * 28) + 1) DAYS as publication_date,
                    
                    -- Add coauthor count
                    yc.nb_coauthors,
                    
                    -- UVM professor info
                    yc.uvm_professor_id as aid,
                    yc.uvm_professor_name as name,
                    COALESCE(ci_uvm.primary_institution, 'Unknown') as institution,
                    
                    -- Age calculations for UVM professor (using calculated fallback)
                    (yc.publication_year - COALESCE(prof.first_pub_year, uvm_calc.calculated_first_year)) as author_age,
                    COALESCE(prof.first_pub_year, uvm_calc.calculated_first_year) as first_pub_year,
                    NULL as last_pub_year,
                    
                    -- Collaboration metrics
                    yc.yearly_collabo,
                    SUM(yc.yearly_collabo) OVER (
                        PARTITION BY yc.uvm_professor_id, yc.coauthor_id 
                        ORDER BY yc.publication_year 
                        ROWS UNBOUNDED PRECEDING
                    ) as all_times_collabo,
                    
                    -- Institution overlap
                    CASE 
                        WHEN ci_uvm.primary_institution IS NOT NULL 
                            AND ci.primary_institution IS NOT NULL
                            AND ci_uvm.primary_institution = ci.primary_institution
                        THEN ci_uvm.primary_institution
                        ELSE NULL 
                    END as shared_institutions,
                    
                    -- Coauthor info
                    yc.coauthor_id as coauth_aid,
                    yc.coauthor_name as coauth_name,
                    COALESCE(ci.primary_institution, 'Unknown') as coauth_institution,
                    
                    -- Coauthor age calculations
                    CASE 
                        WHEN cc.first_publication_year IS NOT NULL 
                        THEN (yc.publication_year - cc.first_publication_year)
                        ELSE NULL 
                    END as coauth_age,
                    cc.first_publication_year as coauth_min_year,
                    
                    -- Age difference
                    CASE 
                        WHEN cc.first_publication_year IS NOT NULL AND COALESCE(prof.first_pub_year, uvm_calc.calculated_first_year) IS NOT NULL
                        THEN (yc.publication_year - COALESCE(prof.first_pub_year, uvm_calc.calculated_first_year)) - (yc.publication_year - cc.first_publication_year)
                        ELSE NULL 
                    END as age_diff,
                    
                    -- Age category
                    CASE 
                        WHEN cc.first_publication_year IS NOT NULL AND COALESCE(prof.first_pub_year, uvm_calc.calculated_first_year) IS NOT NULL THEN
                            CASE 
                                WHEN (yc.publication_year - COALESCE(prof.first_pub_year, uvm_calc.calculated_first_year)) - (yc.publication_year - cc.first_publication_year) > 7 THEN 'younger'
                                WHEN (yc.publication_year - COALESCE(prof.first_pub_year, uvm_calc.calculated_first_year)) - (yc.publication_year - cc.first_publication_year) < -7 THEN 'older'
                                ELSE 'same'
                            END
                        ELSE 'unknown'
                    END as age_category,
                    
                    -- Collaboration intensity
                    CASE 
                        WHEN SUM(yc.yearly_collabo) OVER (
                            PARTITION BY yc.uvm_professor_id, yc.coauthor_id 
                            ORDER BY yc.publication_year 
                            ROWS UNBOUNDED PRECEDING
                        ) > 0 
                        THEN CAST(yc.yearly_collabo AS FLOAT) / SUM(yc.yearly_collabo) OVER (
                            PARTITION BY yc.uvm_professor_id, yc.coauthor_id 
                            ORDER BY yc.publication_year 
                            ROWS UNBOUNDED PRECEDING
                        )
                        ELSE 0
                    END as collaboration_intensity,
                    
                    -- Normalized institution names
                    LOWER(TRIM(COALESCE(ci_uvm.primary_institution, 'unknown'))) as institution_normalized,
                    LOWER(TRIM(COALESCE(ci.primary_institution, 'unknown'))) as coauth_institution_normalized,
                    CASE 
                        WHEN ci_uvm.primary_institution IS NOT NULL 
                            AND ci.primary_institution IS NOT NULL
                            AND ci_uvm.primary_institution = ci.primary_institution
                        THEN LOWER(TRIM(ci_uvm.primary_institution))
                        ELSE NULL 
                    END as shared_institutions_normalized,
                    NULL as age_std
                    
                FROM oa.main.yearly_collaborations yc
                LEFT JOIN oa.main.coauthor_cache cc 
                    ON yc.coauthor_id = cc.author_oa_id
                LEFT JOIN oa.main.coauthor_institutions ci 
                    ON yc.coauthor_id = ci.coauthor_id 
                    AND yc.publication_year = ci.publication_year
                LEFT JOIN oa.main.coauthor_institutions ci_uvm
                    ON yc.uvm_professor_id = ci_uvm.coauthor_id 
                    AND yc.publication_year = ci_uvm.publication_year
                LEFT JOIN uvm_calc
                    ON yc.uvm_professor_id = uvm_calc.author_oa_id
                ORDER BY 
                    yc.uvm_professor_name, 
                    yc.coauthor_name,
                    yc.publication_year
            ) TO '{STATIC_DATA_PATH}/coauthor.parquet' (FORMAT PARQUET)
        """)
        
        # Get export stats
        export_stats = conn.execute(f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT aid) as unique_professors,
                COUNT(DISTINCT coauth_aid) as unique_coauthors,
                MIN(publication_year) as earliest_year,
                MAX(publication_year) as latest_year,
                AVG(yearly_collabo) as avg_yearly_collaborations,
                COUNT(CASE WHEN age_diff IS NOT NULL THEN 1 END) as records_with_age_data
            FROM read_parquet('{STATIC_DATA_PATH}/coauthor.parquet')
        """).fetchone()
        
        # Check data quality
        quality_stats = conn.execute(f"""
            SELECT 
                COUNT(CASE WHEN coauth_institution = 'Unknown' THEN 1 END) as unknown_institutions,
                COUNT(CASE WHEN author_age < 0 THEN 1 END) as negative_uvm_ages,
                COUNT(CASE WHEN coauth_age < 0 THEN 1 END) as negative_coauth_ages,
                COUNT(CASE WHEN ABS(age_diff) > 50 THEN 1 END) as extreme_age_differences
            FROM read_parquet('{STATIC_DATA_PATH}/coauthor.parquet')
        """).fetchone()
    
    return dg.MaterializeResult(
        metadata={
            "export_path": str(STATIC_DATA_PATH / "coauthor.parquet"),
            "total_records": export_stats[0],
            "unique_professors": export_stats[1],
            "unique_coauthors": export_stats[2],
            "year_range": f"{export_stats[3]}-{export_stats[4]}" if export_stats[3] else "None",
            "avg_yearly_collaborations": round(export_stats[5], 2) if export_stats[5] else 0,
            "records_with_age_data": export_stats[6],
            "age_data_percentage": round((export_stats[6] / export_stats[0]) * 100, 1) if export_stats[0] > 0 else 0,
            
            # Data quality metrics
            "unknown_institutions": quality_stats[0],
            "negative_uvm_ages": quality_stats[1],
            "negative_coauth_ages": quality_stats[2],
            "extreme_age_differences": quality_stats[3]
        }
    )


@dg.asset_check(
    asset=coauthor_parquet,
    description="Basic check that export worked",
)
def coauthor_export_check(duckdb: DuckDBResource) -> dg.AssetCheckResult:
    """Simple check that the export has data"""
    
    parquet_path = STATIC_DATA_PATH / "coauthor.parquet"
    
    with duckdb.get_connection() as conn:
        # Just check basic stats
        stats = conn.execute(f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT aid) as unique_professors,
                COUNT(DISTINCT coauth_aid) as unique_coauthors
            FROM read_parquet('{parquet_path}')
        """).fetchone()
    
    total_records, unique_professors, unique_coauthors = stats
    
    return dg.AssetCheckResult(
        passed=total_records > 0,
        metadata={
            "total_records": total_records,
            "unique_professors": unique_professors,
            "unique_coauthors": unique_coauthors
        }
    )