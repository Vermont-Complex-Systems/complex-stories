import dagster as dg
from backend.defs.resources import OpenAlexResource
from dagster_duckdb import DuckDBResource
from typing import List, Tuple, Optional

def create_coauthor_cache_table(conn) -> None:
    """Create table to cache coauthor first publication years"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS oa.main.coauthor_cache (
            author_oa_id VARCHAR PRIMARY KEY,
            author_display_name VARCHAR,
            first_publication_year INTEGER,
            last_publication_year INTEGER,
            total_publications INTEGER,
            last_fetched_date TIMESTAMP,
            fetch_successful BOOLEAN DEFAULT FALSE
        )
    """)

def get_external_coauthors_to_process(conn, limit: int = 20) -> List[Tuple[str, str]]:
    """Get external coauthors who haven't been processed yet"""
    
    result = conn.execute("""
        SELECT DISTINCT 
            a.author_oa_id,
            a.author_display_name
        FROM oa.main.authorships a
        WHERE a.author_oa_id NOT IN (
            SELECT 'https://openalex.org/' || oa_uid 
            FROM oa.main.uvm_profs_2023
        )
        AND a.author_oa_id NOT IN (
            SELECT author_oa_id 
            FROM oa.main.coauthor_cache
        )
        ORDER BY a.author_display_name
        LIMIT ?
    """, [limit]).fetchall()
    
    return [(row[0], row[1]) for row in result]

def fetch_author_publication_range(oa_client: OpenAlexResource, author_id: str) -> Tuple[Optional[int], Optional[int], int]:
    """Get first/last pub year in a single API call using group_by"""
    try:
        clean_id = author_id.replace('https://openalex.org/', '')
        
        # Single API call using group_by to get year statistics
        response = oa_client.request("works", {
            "filter": f"author.id:{clean_id}",
            "group_by": "publication_year",
            "per_page": 200 
        }).json()
        
        results = response.get('group_by', [])
        meta = response.get('meta', {})
        total_count = meta.get('count', 0)
        
        if not results:
            return None, None, total_count
        
        # Extract all years and find min/max
        years = [item['key'] for item in results if item['key'] is not None]
        
        if not years:
            return None, None, total_count
            
        first_year = min(years)
        last_year = max(years)
        
        return first_year, last_year, total_count
        
    except Exception as e:
        dg.get_dagster_logger().error(f"Failed to fetch publication range for {author_id}: {str(e)}")
        return None, None, 0
    
@dg.asset(
    kinds={"openalex"},
    key=["target", "main", "coauthor_cache"],
    deps=["uvm_publications"],
)
def build_coauthor_cache(
    oa_client: OpenAlexResource,
    duckdb: DuckDBResource
) -> dg.MaterializeResult:
    """Build cache of external coauthor first publication years"""
    
    with duckdb.get_connection() as conn:
        create_coauthor_cache_table(conn)
        
        # Get total counts for context
        total_external = conn.execute("""
            SELECT COUNT(DISTINCT a.author_oa_id) as total_external_authors
            FROM oa.main.authorships a
            WHERE a.author_oa_id NOT IN (
                SELECT 'https://openalex.org/' || oa_uid 
                FROM oa.main.uvm_profs_2023
            )
        """).fetchone()[0]
        
        already_cached = conn.execute("""
            SELECT COUNT(*) FROM oa.main.coauthor_cache
        """).fetchone()[0]
        
        coauthors_to_process = get_external_coauthors_to_process(conn, limit=1000)
    
    dg.get_dagster_logger().info(
        f"External coauthors: {total_external} total, {already_cached} already cached, "
        f"{len(coauthors_to_process)} to process this run"
    )
    
    if not coauthors_to_process:
        return dg.MaterializeResult(
            metadata={
                "coauthors_processed": 0,
                "total_external_authors": total_external,
                "already_cached": already_cached,
                "remaining": 0,
                "reason": "all_complete"
            }
        )
    
    successful_fetches = 0
    failed_fetches = 0
    
    for author_id, author_name in coauthors_to_process:
        try:
            dg.get_dagster_logger().info(f"Processing {author_name}...")
            
            # Fetch complete publication data for this author
            first_year, last_year, total_pubs = fetch_author_publication_range(oa_client, author_id, conn)
            
            fetch_successful = first_year is not None
            
            # Store in cache
            with duckdb.get_connection() as conn:
                conn.execute("""
                    INSERT INTO oa.main.coauthor_cache 
                    (author_oa_id, author_display_name, first_publication_year, 
                     last_publication_year, total_publications, last_fetched_date, fetch_successful)
                    VALUES (?, ?, ?, ?, ?, NOW(), ?)
                """, [
                    author_id, author_name, first_year, last_year, total_pubs, fetch_successful
                ])
            
            if fetch_successful:
                successful_fetches += 1
                dg.get_dagster_logger().info(
                    f"✅ {author_name}: {first_year}-{last_year} ({total_pubs} publications)"
                )
            else:
                failed_fetches += 1
                dg.get_dagster_logger().warning(f"❌ {author_name}: No publication data found")
                
        except Exception as e:
            failed_fetches += 1
            dg.get_dagster_logger().error(f"❌ Error processing {author_name}: {str(e)}")
            
            # Still record the attempt
            with duckdb.get_connection() as conn:
                conn.execute("""
                    INSERT INTO oa.main.coauthor_cache 
                    (author_oa_id, author_display_name, last_fetched_date, fetch_successful)
                    VALUES (?, ?, NOW(), FALSE)
                """, [author_id, author_name])
    
    # Final stats
    with duckdb.get_connection() as conn:
        final_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_cached,
                COUNT(CASE WHEN fetch_successful = TRUE THEN 1 END) as successful_cached
            FROM oa.main.coauthor_cache
        """).fetchone()
        
        remaining = total_external - final_stats[0]
    
    return dg.MaterializeResult(
        metadata={
            "coauthors_processed": len(coauthors_to_process),
            "successful_fetches": successful_fetches,
            "failed_fetches": failed_fetches,
            "total_cached": final_stats[0],
            "successful_cached": final_stats[1],
            "total_external_authors": total_external,
            "remaining_to_process": remaining,
            "completion_percentage": round((final_stats[0] / total_external * 100), 1) if total_external > 0 else 0
        }
    )

@dg.asset_check(
    asset=build_coauthor_cache,
    description="Check coauthor cache progress",
)
def coauthor_cache_progress_check(duckdb: DuckDBResource) -> dg.AssetCheckResult:
    """Check the progress of building coauthor cache"""
    
    with duckdb.get_connection() as conn:
        # Simpler query without complex subquery
        total_external = conn.execute("""
            SELECT COUNT(DISTINCT a.author_oa_id) as total_external_coauthors
            FROM oa.main.authorships a
            WHERE a.author_oa_id NOT IN (
                SELECT 'https://openalex.org/' || oa_uid 
                FROM oa.main.uvm_profs_2023
            )
        """).fetchone()[0]
        
        cached_stats = conn.execute("""
            SELECT 
                COUNT(*) as cached_count,
                COUNT(CASE WHEN fetch_successful = TRUE THEN 1 END) as successful_count
            FROM oa.main.coauthor_cache
        """).fetchone()
        
        cached_count, successful_count = cached_stats
        completion_pct = (cached_count / total_external * 100) if total_external > 0 else 0
        success_rate = (successful_count / cached_count * 100) if cached_count > 0 else 0
    
    return dg.AssetCheckResult(
        passed=True,  # Always pass, just tracking progress
        metadata={
            "total_external_coauthors": total_external,
            "cached_count": cached_count,
            "successful_count": successful_count,
            "completion_percentage": round(completion_pct, 1),
            "success_rate": round(success_rate, 1),
            "remaining": total_external - cached_count
        }
    )