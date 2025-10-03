"""
Cache all publication ranges of all coauthors of UVM 2023 faculties to calculate relative age.
This takes a while but there is no way around it as far as we can tell.
"""

import dagster as dg
from shared.clients.openalex import OpenAlexClient
from dagster_duckdb import DuckDBResource
from open_academic_analytics.defs.resources import OpenAlexResource
from typing import List, Tuple, Optional

def create_coauthor_cache_table(conn) -> None:
    """Create table to cache coauthor first publication years"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS oa.cache.coauthor_cache (
            id VARCHAR PRIMARY KEY,
            display_name VARCHAR,
            first_pub_year INTEGER,
            last_pub_year INTEGER,
            last_fetched_date TIMESTAMP,
            fetch_successful BOOLEAN DEFAULT FALSE
        )
    """)

def get_external_coauthors_to_process(conn) -> List[Tuple[str, str]]:
    """Get external coauthors who haven't been processed yet"""
    
    result = conn.execute("""
    -- Find external coauthors who need their publication ranges cached
    SELECT DISTINCT
        a.author_id,           -- OpenAlex author ID (e.g., 'https://openalex.org/A12345')
        a.author_display_name  -- Author's display name for logging
    FROM oa.raw.authorships a      -- All author-paper relationships
    LEFT JOIN oa.cache.coauthor_cache c
        ON a.author_id = c.id      -- Check if already cached
    WHERE a.author_id NOT IN (
        -- Exclude UVM professors (we don't need to cache their data)
        SELECT ego_author_id
        FROM oa.raw.uvm_profs_2023
        WHERE ego_author_id IS NOT NULL
    )  -- Only get external (non-UVM) coauthors who collaborate with UVM profs
    AND (c.id IS NULL OR c.fetch_successful = FALSE) -- Only skips successful
    ORDER BY a.author_display_name
    """).fetchall()
    
    return [(row[0], row[1]) for row in result]

def fetch_author_publication_range(oa_client: OpenAlexClient, author_id: str) -> Tuple[Optional[int], Optional[int]]:
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

        if not results:
            return None, None

        # Extract all years and convert to integers, filtering out invalid values
        years = []
        skipped_values = []

        dg.get_dagster_logger().info(f"Processing {len(results)} group_by results for {author_id}")

        for item in results:
            key = item.get('key')
            count = item.get('count', 0)

            if key is not None:
                try:
                    # Convert to int, skip if it's not a valid year
                    year = int(key)
                    if 1900 <= year <= 2030:  # Reasonable year range
                        years.append(year)
                        dg.get_dagster_logger().debug(f"Valid year: {year} ({count} publications)")
                    else:
                        skipped_values.append(f"{key} (out of range, {count} pubs)")
                        dg.get_dagster_logger().warning(f"Year out of range: {key} ({count} publications)")
                except (ValueError, TypeError):
                    # Skip invalid year values (like timestamps)
                    skipped_values.append(f"{key} (invalid format, {count} pubs)")
                    dg.get_dagster_logger().warning(f"Invalid year format: {key} ({count} publications)")
            else:
                skipped_values.append(f"null key ({count} pubs)")
                dg.get_dagster_logger().warning(f"Null year key with {count} publications")

        # Log summary
        if skipped_values:
            dg.get_dagster_logger().warning(f"Skipped {len(skipped_values)} invalid year values: {skipped_values}")

        dg.get_dagster_logger().info(f"Found {len(years)} valid years for {author_id}")

        if not years:
            dg.get_dagster_logger().warning(f"No valid years found for {author_id} after filtering")
            return None, None

        first_year = min(years)
        last_year = max(years)

        return first_year, last_year

    except Exception as e:
        dg.get_dagster_logger().error(f"Failed to fetch publication range for {author_id}: {str(e)}")
        return None, None
   
@dg.asset(
    kinds={"openalex"},
    deps=["uvm_publications"],
)
def coauthor_cache(
    oa_resource: OpenAlexResource,
    duckdb: DuckDBResource
) -> dg.MaterializeResult:
    """Build cache of external coauthor first publication years"""
    
    oa_client = oa_resource.get_client()

    with duckdb.get_connection() as conn:
        
        create_coauthor_cache_table(conn)
        
        # Get total counts for context
        total_external = conn.execute("""
            SELECT COUNT(DISTINCT a.author_id) as total_external_authors
            FROM oa.raw.authorships a
            WHERE a.author_id NOT IN (
                SELECT ego_author_id
                FROM oa.raw.uvm_profs_2023
                WHERE ego_author_id IS NOT NULL
            )  -- External (non-UVM) coauthors only
        """).fetchone()[0]
        
        already_cached = conn.execute("""
            SELECT COUNT(*) FROM oa.cache.coauthor_cache
        """).fetchone()[0]
        
        coauthors_to_process = get_external_coauthors_to_process(conn)
        
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
                
                # Fetch complete publication data for this author. This is trickier than it seems.
                first_year, last_year = fetch_author_publication_range(oa_client, author_id)
                
                fetch_successful = first_year is not None
                
                # Store in cache (using same connection)
                conn.execute("""
                    INSERT OR IGNORE INTO oa.cache.coauthor_cache 
                    (id, display_name, first_pub_year, 
                     last_pub_year, last_fetched_date, fetch_successful)
                    VALUES (?, ?, ?, ?, NOW(), ?)
                """, [
                    author_id, author_name, first_year, last_year, fetch_successful
                ])
                
                if fetch_successful:
                    successful_fetches += 1
                    dg.get_dagster_logger().info(
                        f"✅ {author_name}: {first_year}-{last_year}"
                    )
                else:
                    failed_fetches += 1
                    dg.get_dagster_logger().warning(f"❌ {author_name}: No publication data found")
                    
            except Exception as e:
                failed_fetches += 1
                dg.get_dagster_logger().error(f"❌ Error processing {author_name}: {str(e)}")
                
                # Still record the attempt (using same connection)
                conn.execute("""
                    INSERT OR IGNORE INTO oa.cache.coauthor_cache 
                    (id, display_name, last_fetched_date, fetch_successful)
                    VALUES (?, ?, NOW(), FALSE)
                """, [author_id, author_name])
        
        # Final stats (using same connection)
        final_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_cached,
                COUNT(CASE WHEN fetch_successful = TRUE THEN 1 END) as successful_cached
            FROM oa.cache.coauthor_cache
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
    asset=coauthor_cache,
    description="Check coauthor cache progress",
)
def coauthor_cache_progress_check(duckdb: DuckDBResource) -> dg.AssetCheckResult:
    """Check the progress of building coauthor cache"""
    
    with duckdb.get_connection() as conn:
        # Get external coauthors count
        total_external = conn.execute("""
            SELECT COUNT(DISTINCT a.author_id) as total_external_coauthors
            FROM oa.raw.authorships a
            WHERE a.author_id NOT IN (
                SELECT ego_author_id
                FROM oa.raw.uvm_profs_2023
                WHERE ego_author_id IS NOT NULL
            )  -- External (non-UVM) coauthors only
        """).fetchone()[0]
        
        cached_stats = conn.execute("""
            SELECT 
                COUNT(*) as cached_count,
                COUNT(CASE WHEN fetch_successful = TRUE THEN 1 END) as successful_count
            FROM oa.cache.coauthor_cache
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