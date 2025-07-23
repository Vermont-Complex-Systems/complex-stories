import dagster as dg
from dagster_duckdb import DuckDBResource
from pathlib import Path

# Path to your static data directory
STATIC_DATA_PATH = Path("../../../../../static/data") 

@dg.asset(
    kinds={"export"},
    deps=["paper_parquet", "coauthor_cache"], 
    key=["exports", "coauthor_parquet"]
)
def coauthor_parquet(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """Export publications data as parquet for static frontend"""
    
    # Ensure the static data directory exists
    STATIC_DATA_PATH.mkdir(parents=True, exist_ok=True)
    paper_parquet_path = STATIC_DATA_PATH / "paper.parquet"
    
    with duckdb.get_connection() as conn:
        # Export flattened publications data with author info
        # Match full OpenAlex URLs in authorships with professor IDs by adding URL prefix
        conn.execute(f"""
            COPY (
                -- Use the paper parquet as the source of truth
                WITH paper_data AS (
                    SELECT DISTINCT 
                        work_id,
                        professor_oa_uid,
                        name,
                        publication_year,
                        publication_date,
                        nb_coauthors
                    FROM read_parquet('{paper_parquet_path}')
                ),
                
                -- Get all coauthors for these filtered papers
                collaboration_pairs AS (
                    SELECT 
                        pd.work_id,
                        pd.publication_year,
                        pd.publication_date,
                        pd.nb_coauthors,
                        pd.professor_oa_uid as uvm_professor_id,
                        pd.name,
                        auth.author_oa_id as coauthor_id,
                        auth.author_display_name as coauthor_name,
                        auth.institutions as coauth_institutions_json
                    FROM paper_data pd
                    JOIN oa.main.authorships auth ON pd.work_id = auth.work_id
                    WHERE auth.author_oa_id != pd.professor_oa_uid
                ),

                -- Extract and count institution affiliations for each coauthor
                coauthor_institutions AS (
                    SELECT 
                        coauthor_id,
                        coauthor_name,
                        CASE 
                            WHEN coauth_institutions_json IS NOT NULL 
                                AND coauth_institutions_json != '[]' 
                                AND JSON_ARRAY_LENGTH(coauth_institutions_json) > 0
                            THEN JSON_EXTRACT_STRING(coauth_institutions_json, '$[0].display_name')
                            ELSE 'Unknown'
                        END as institution_name,
                        COUNT(*) as institution_count
                    FROM collaboration_pairs
                    GROUP BY 
                        coauthor_id, coauthor_name,
                        CASE 
                            WHEN coauth_institutions_json IS NOT NULL 
                                AND coauth_institutions_json != '[]' 
                                AND JSON_ARRAY_LENGTH(coauth_institutions_json) > 0
                            THEN JSON_EXTRACT_STRING(coauth_institutions_json, '$[0].display_name')
                            ELSE 'Unknown'
                        END
                ),

                -- Get the most common (primary) institution for each coauthor
                coauthor_primary_institution AS (
                    SELECT 
                        coauthor_id,
                        coauthor_name,
                        institution_name as primary_institution
                    FROM (
                        SELECT 
                            coauthor_id,
                            coauthor_name,
                            institution_name,
                            ROW_NUMBER() OVER (
                                PARTITION BY coauthor_id 
                                ORDER BY institution_count DESC, institution_name ASC
                            ) as rn
                        FROM coauthor_institutions
                    ) ranked
                    WHERE rn = 1
                ),

                -- Yearly collaboration counts with nb_coauthors
                yearly_collaborations AS (
                    SELECT 
                        uvm_professor_id,
                        name,
                        coauthor_id,
                        coauthor_name,
                        publication_year,
                        MIN(publication_date) as publication_date,
                        COUNT(*) as yearly_collabo,
                        MAX(nb_coauthors) as nb_coauthors  -- Add this here
                    FROM collaboration_pairs
                    GROUP BY 
                        uvm_professor_id, name,
                        coauthor_id, coauthor_name,
                        publication_year
                )

                -- Final output
                SELECT 
                    -- Publication info with jitter
                    yc.publication_year,
                    yc.publication_date + INTERVAL (FLOOR(RANDOM() * 28) + 1) DAYS as publication_date,
                    
                    -- Add coauthor count
                    yc.nb_coauthors,
                    
                    -- UVM professor info
                    yc.uvm_professor_id as aid,
                    yc.name,
                    COALESCE(prof.host_dept, 'Unknown') as institution,
                    
                    -- Age calculations for UVM professor
                    (yc.publication_year - prof.first_pub_year) as author_age,
                    prof.first_pub_year,
                    NULL as last_pub_year,
                    
                    -- Collaboration metrics
                    yc.yearly_collabo,
                    SUM(yc.yearly_collabo) OVER (
                        PARTITION BY yc.uvm_professor_id, yc.coauthor_id 
                        ORDER BY yc.publication_year 
                        ROWS UNBOUNDED PRECEDING
                    ) as all_times_collabo,
                    
                    -- Institution overlap (placeholder)
                    NULL as shared_institutions,
                    
                    -- Coauthor info
                    yc.coauthor_id as coauth_aid,
                    yc.coauthor_name as coauth_name,
                    COALESCE(cpi.primary_institution, 'Unknown') as coauth_institution,
                    
                    -- Coauthor age calculations
                    CASE 
                        WHEN cc.first_publication_year IS NOT NULL 
                        THEN (yc.publication_year - cc.first_publication_year)
                        ELSE NULL 
                    END as coauth_age,
                    cc.first_publication_year as coauth_min_year,
                    
                    -- Age difference
                    CASE 
                        WHEN cc.first_publication_year IS NOT NULL AND prof.first_pub_year IS NOT NULL
                        THEN (yc.publication_year - prof.first_pub_year) - (yc.publication_year - cc.first_publication_year)
                        ELSE NULL 
                    END as age_diff,
                    
                    -- Age category
                    CASE 
                        WHEN cc.first_publication_year IS NOT NULL AND prof.first_pub_year IS NOT NULL THEN
                            CASE 
                                WHEN (yc.publication_year - prof.first_pub_year) - (yc.publication_year - cc.first_publication_year) > 7 THEN 'younger'
                                WHEN (yc.publication_year - prof.first_pub_year) - (yc.publication_year - cc.first_publication_year) < -7 THEN 'older'
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
                    LOWER(TRIM(COALESCE(prof.host_dept, 'unknown'))) as institution_normalized,
                    LOWER(TRIM(COALESCE(cpi.primary_institution, 'unknown'))) as coauth_institution_normalized,
                    NULL as shared_institutions_normalized,
                    NULL as age_std
                    
                FROM yearly_collaborations yc
                LEFT JOIN oa.main.uvm_profs_2023 prof 
                    ON yc.uvm_professor_id = 'https://openalex.org/' || prof.oa_uid
                LEFT JOIN oa.main.coauthor_cache cc 
                    ON yc.coauthor_id = cc.author_oa_id
                LEFT JOIN coauthor_primary_institution cpi 
                    ON yc.coauthor_id = cpi.coauthor_id
                ORDER BY 
                    yc.name, 
                    yc.coauthor_name,
                    yc.publication_year
            ) TO '{STATIC_DATA_PATH}/coauthor.parquet' (FORMAT PARQUET)
        """)
        
        # Get export stats
        stats = conn.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT a.author_oa_id) as unique_professors,
                COUNT(DISTINCT p.id) as unique_publications,
                MIN(p.publication_year) as earliest_year,
                MAX(p.publication_year) as latest_year,
                AVG(p.cited_by_count) as avg_citations
            FROM oa.main.publications p
            JOIN oa.main.authorships a ON p.id = a.work_id
            WHERE a.author_oa_id IN (
                SELECT 'https://openalex.org/' || oa_uid FROM oa.main.uvm_profs_2023
            )
        """).fetchone()
    
    return dg.MaterializeResult(
        metadata={
            "export_path": str(STATIC_DATA_PATH / "coauthor.parquet"),
            "total_records": stats[0],
            "unique_professors": stats[1],
            "unique_publications": stats[2],
            "year_range": f"{stats[3]}-{stats[4]}" if stats[3] else "None",
            "avg_citations": round(stats[5], 2) if stats[5] else 0
        }
    )

# @dg.asset_check(
#     asset=export_coauthor_parquet,
#     description="Check for data quality issues in coauthor data",
# )
# def coauthor_data_quality_check(duckdb: DuckDBResource) -> dg.AssetCheckResult:
#     """Check for suspicious age differences using the exported parquet data"""
    
#     parquet_path = STATIC_DATA_PATH / "coauthor.parquet"
    
#     with duckdb.get_connection() as conn:
#         # Read the exported parquet file directly
#         stats = conn.execute(f"""
#             SELECT 
#                 COUNT(*) as total_records,
#                 COUNT(CASE WHEN age_diff IS NOT NULL THEN 1 END) as with_age_data,
                
#                 -- Extreme age differences (might indicate data issues)
#                 COUNT(CASE WHEN ABS(age_diff) > 30 THEN 1 END) as extreme_age_diff,
#                 COUNT(CASE WHEN ABS(age_diff) > 50 THEN 1 END) as very_extreme_age_diff,
                
#                 -- Negative academic ages (impossible)
#                 COUNT(CASE WHEN author_age < 0 THEN 1 END) as negative_uvm_age,
#                 COUNT(CASE WHEN coauth_age < 0 THEN 1 END) as negative_coauth_age,
                
#                 -- Very long careers (might indicate data issues)
#                 COUNT(CASE WHEN author_age > 60 THEN 1 END) as very_long_uvm_career,
#                 COUNT(CASE WHEN coauth_age > 60 THEN 1 END) as very_long_coauth_career,
                
#                 -- Age statistics
#                 AVG(ABS(age_diff)) as avg_abs_age_diff,
#                 MIN(age_diff) as min_age_diff,
#                 MAX(age_diff) as max_age_diff
                
#             FROM read_parquet('{parquet_path}')
#             WHERE age_diff IS NOT NULL
#         """).fetchone()
        
#         # Get examples of extreme cases
#         extreme_examples = conn.execute(f"""
#             SELECT 
#                 name,
#                 coauth_name,
#                 first_pub_year,
#                 coauth_min_year,
#                 age_diff
#             FROM read_parquet('{parquet_path}')
#             WHERE ABS(age_diff) > 30
#             ORDER BY ABS(age_diff) DESC
#             LIMIT 5
#         """).fetchall()
    
#     # Unpack stats
#     (total_records, with_age_data, extreme_age_diff, very_extreme_age_diff,
#      negative_uvm_age, negative_coauth_age, very_long_uvm_career, 
#      very_long_coauth_career, avg_abs_age_diff, min_age_diff, max_age_diff) = stats
    
#     # Determine if there are major issues
#     has_major_issues = (
#         very_extreme_age_diff > 0 or
#         negative_uvm_age > 0 or
#         negative_coauth_age > 0
#     )
    
#     return dg.AssetCheckResult(
#         passed=not has_major_issues,
#         metadata={
#             "total_records": total_records,
#             "with_age_data": with_age_data,
#             "extreme_age_differences_30plus": extreme_age_diff,
#             "very_extreme_age_differences_50plus": very_extreme_age_diff,
#             "negative_uvm_academic_ages": negative_uvm_age,
#             "negative_coauthor_academic_ages": negative_coauth_age,
#             "avg_absolute_age_difference": round(avg_abs_age_diff, 1) if avg_abs_age_diff else 0,
#             "min_age_difference": min_age_diff,
#             "max_age_difference": max_age_diff,
#             "extreme_examples": [
#                 f"{ex[0]} vs {ex[1]}: {ex[4]} years ({ex[2]} vs {ex[3]})" 
#                 for ex in extreme_examples
#             ] if extreme_examples else []
#         }
#     )