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
def export_paper_parquet(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """Export publications data as parquet for static frontend"""
    
    # Ensure the static data directory exists
    STATIC_DATA_PATH.mkdir(parents=True, exist_ok=True)
    
    with duckdb.get_connection() as conn:
        # Export flattened publications data
        conn.execute(f"""
            COPY (
                SELECT 
                    professor_oa_uid,
                    professor_name,
                    id as work_id,
                    title,
                    publication_year,
                    publication_date,
                    cited_by_count,
                    type as work_type,
                    language,
                    doi,
                    
                    -- Flatten nested structures
                    primary_location.is_oa as is_open_access,
                    primary_location.landing_page_url,
                    primary_location.pdf_url,
                    primary_location.license,
                    primary_location.source.display_name as journal_name,
                    primary_location.source.type as source_type,
                    
                    open_access.oa_status,
                    open_access.oa_url,
                    
                    primary_topic.id as topic_id,
                    primary_topic.display_name as topic_name,
                    primary_topic.score as topic_score,
                    
                    biblio.volume,
                    biblio.issue,
                    biblio.first_page,
                    biblio.last_page,
                    
                    fwci,
                    has_fulltext,
                    fulltext_origin,
                    is_retracted,
                    countries_distinct_count,
                    institutions_distinct_count,
                    locations_count,
                    referenced_works_count,
                    
                    updated_date,
                    created_date
                FROM oa.main.uvm_publications
                ORDER BY cited_by_count DESC
            ) TO '{STATIC_DATA_PATH}/paper.parquet' (FORMAT PARQUET)
        """)
        
        # Get export stats
        stats = conn.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT professor_oa_uid) as unique_professors,
                MIN(publication_year) as earliest_year,
                MAX(publication_year) as latest_year,
                AVG(cited_by_count) as avg_citations
            FROM oa.main.uvm_publications
        """).fetchone()
    
    return dg.MaterializeResult(
        metadata={
            "export_path": str(STATIC_DATA_PATH / "paper.parquet"),
            "total_records": stats[0],
            "unique_professors": stats[1],
            "year_range": f"{stats[2]}-{stats[3]}",
            "avg_citations": round(stats[4], 2) if stats[4] else 0
        }
    )