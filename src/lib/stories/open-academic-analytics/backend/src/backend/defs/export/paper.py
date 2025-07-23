import dagster as dg
from dagster_duckdb import DuckDBResource
from pathlib import Path

# Path to your static data directory
STATIC_DATA_PATH = Path("../../../../../static/data") 

@dg.asset(
    kinds={"export"},
    deps=["uvm_publications"],
    key=["exports", "paper_parquet"]
)
def paper_parquet(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """Export publications data as parquet for static frontend"""
    
    # Ensure the static data directory exists
    STATIC_DATA_PATH.mkdir(parents=True, exist_ok=True)
    
    with duckdb.get_connection() as conn:
        # Export flattened publications data with author info
        # Match full OpenAlex URLs in authorships with professor IDs by adding URL prefix
        conn.execute(f"""
            COPY (
                SELECT 
                    a.author_oa_id as professor_oa_uid,
                    a.author_display_name as name,
                    p.id as work_id,
                    p.title,
                    p.publication_year,
                    p.publication_date,
                    p.cited_by_count,
                    p.type as work_type,
                    p.language,
                    p.doi,
                    
                    -- Add coauthor count
                    auth_counts.nb_coauthors,
            
                    -- Author-specific info
                    a.author_position,
                    a.is_corresponding,
                    
                    -- Flatten nested structures
                    p.primary_location.is_oa as is_open_access,
                    p.primary_location.landing_page_url,
                    p.primary_location.pdf_url,
                    p.primary_location.license,
                    p.primary_location.source.display_name as journal_name,
                    p.primary_location.source.type as source_type,
                    
                    p.open_access.oa_status,
                    p.open_access.oa_url,
                    
                    p.primary_topic.id as topic_id,
                    p.primary_topic.display_name as topic_name,
                    p.primary_topic.score as topic_score,
                    
                    p.biblio.volume,
                    p.biblio.issue,
                    p.biblio.first_page,
                    p.biblio.last_page,
                    
                    p.fwci,
                    p.has_fulltext,
                    p.fulltext_origin,
                    p.is_retracted,
                    p.countries_distinct_count,
                    p.institutions_distinct_count,
                    p.locations_count,
                    p.referenced_works_count,
                    
                    p.updated_date,
                    p.created_date
                FROM oa.main.publications p
                JOIN oa.main.authorships a ON p.id = a.work_id
                JOIN (
                    -- Count all authors per paper
                    SELECT 
                        work_id,
                        COUNT(*) - 1 as nb_coauthors  -- Subtract 1 to exclude the UVM professor themselves
                    FROM oa.main.authorships
                    GROUP BY work_id
                ) auth_counts ON p.id = auth_counts.work_id
                WHERE a.author_oa_id IN (
                    SELECT 'https://openalex.org/' || oa_uid FROM oa.main.uvm_profs_2023
                )
                    AND p.doi IS NOT NULL
                    AND p.type IN ('article', 'preprint', 'book-chapter', 'book', 'report')
                    AND auth_counts.nb_coauthors < 25
                ORDER BY p.cited_by_count DESC, p.id, a.author_display_name
            ) TO '{STATIC_DATA_PATH}/paper.parquet' (FORMAT PARQUET)
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
            "export_path": str(STATIC_DATA_PATH / "paper.parquet"),
            "total_records": stats[0],
            "unique_professors": stats[1],
            "unique_publications": stats[2],
            "year_range": f"{stats[3]}-{stats[4]}" if stats[3] else "None",
            "avg_citations": round(stats[5], 2) if stats[5] else 0
        }
    )