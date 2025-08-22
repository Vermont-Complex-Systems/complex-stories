"""Grab all UVM 2023 faculties publications from OpenAlex"""

import dagster as dg
from backend.defs.resources import OpenAlexResource
from dagster_duckdb import DuckDBResource
from typing import Dict, List, Tuple, Optional
import json


def create_publications_tables(conn) -> None:
    """Create the publications and authorships tables"""
    
    # Publications table - one record per unique work
    conn.execute("""
        CREATE TABLE IF NOT EXISTS oa.raw.publications (
            id VARCHAR PRIMARY KEY,
            doi VARCHAR,
            title VARCHAR,
            display_name VARCHAR,
            publication_year INTEGER,
            publication_date DATE,
            language VARCHAR,
            type VARCHAR,
            type_crossref VARCHAR,
            
            -- Metrics
            cited_by_count INTEGER,
            fwci DOUBLE,
            has_fulltext BOOLEAN,
            fulltext_origin VARCHAR,
            is_retracted BOOLEAN,
            is_paratext BOOLEAN,
            
            -- Nested structures as STRUCTs
            ids STRUCT(
                openalex VARCHAR,
                doi VARCHAR,
                mag VARCHAR,
                pmid VARCHAR,
                pmcid VARCHAR
            ),
            
            primary_location STRUCT(
                is_oa BOOLEAN,
                landing_page_url VARCHAR,
                pdf_url VARCHAR,
                source STRUCT(
                    id VARCHAR,
                    display_name VARCHAR,
                    type VARCHAR
                ),
                license VARCHAR,
                version VARCHAR,
                is_accepted BOOLEAN,
                is_published BOOLEAN
            ),
            
            open_access STRUCT(
                is_oa BOOLEAN,
                oa_status VARCHAR,
                oa_url VARCHAR,
                any_repository_has_fulltext BOOLEAN
            ),
            
            primary_topic STRUCT(
                id VARCHAR,
                display_name VARCHAR,
                score DOUBLE
            ),
            
            biblio STRUCT(
                volume VARCHAR,
                issue VARCHAR,
                first_page VARCHAR,
                last_page VARCHAR
            ),
            
            -- Arrays as VARCHAR for now
            concepts VARCHAR,
            topics VARCHAR,
            keywords VARCHAR,
            mesh VARCHAR,
            referenced_works VARCHAR,
            related_works VARCHAR,
            
            -- Counts
            countries_distinct_count INTEGER,
            institutions_distinct_count INTEGER,
            locations_count INTEGER,
            referenced_works_count INTEGER,
            
            -- Metadata
            updated_date TIMESTAMP,
            created_date DATE
        )
    """)
    
def create_authorships_table(conn) -> None:
    """Authorships table - many records per work (one per author)"""

    conn.execute("""
        CREATE TABLE IF NOT EXISTS oa.raw.authorships (
            work_id VARCHAR,
            author_id VARCHAR,
            author_display_name VARCHAR,
            author_position VARCHAR,  -- first, middle, last
            institutions VARCHAR,     -- JSON array of author's institutions for this work
            raw_affiliation_strings VARCHAR,
            is_corresponding BOOLEAN,
            
            PRIMARY KEY (work_id, author_id)
        )
    """)

def create_uvm_profs_sync_status_table(conn) -> None:
    """Authorships table - many records per work (one per author)"""

    conn.execute("""
            CREATE TABLE IF NOT EXISTS oa.cache.uvm_profs_sync_status (
                ego_author_id VARCHAR PRIMARY KEY,
                last_synced_date TIMESTAMP,
                paper_count INTEGER,
                needs_update BOOLEAN DEFAULT TRUE
            )
        """)

def get_uvm_profs_to_update(conn) -> List[str]:
    """Get list of uvm_profs who need updating, prioritizing those never synced"""
    result = conn.execute("""
        SELECT ego_author_id
        FROM oa.cache.uvm_profs_sync_status
        WHERE needs_update = TRUE 
           OR last_synced_date IS NULL
           OR last_synced_date < (NOW() - INTERVAL '30 days')
        ORDER BY 
            CASE WHEN last_synced_date IS NULL THEN 0 ELSE 1 END,
            last_synced_date ASC
    """).fetchall()
    
    return [row[0] for row in result]

def get_latest_publication_date(conn, ego_author_id: str) -> Optional[str]:
    """Get the latest publication date for a professor from authorships"""
    result = conn.execute("""
        SELECT MAX(p.publication_date) 
        FROM oa.raw.publications p
        JOIN oa.raw.authorships a ON p.id = a.work_id
        WHERE a.author_id = ?
    """, [ego_author_id]).fetchone()
    
    return result[0] if result and result[0] else None

def get_corrected_first_pub_year(conn, ego_author_id: str) -> Optional[int]:
    """Get the corrected first publication year for a UVM professor"""
    result = conn.execute("""
        SELECT first_pub_year 
        FROM oa.raw.uvm_profs_2023 
        WHERE 'https://openalex.org/' || ego_author_id = ?
    """, [ego_author_id]).fetchone()
    
    return result[0] if result and result[0] else None

def extract_publication_data(work: Dict) -> Tuple:
    """Extract publication data (without author-specific info)"""
    ids = work.get('ids', {})
    primary_location = work.get('primary_location', {})
    open_access = work.get('open_access', {})
    primary_topic = work.get('primary_topic', {})
    biblio = work.get('biblio', {})
    
    return (
        # Core fields (9)
        work.get('id'),
        work.get('doi'),
        work.get('title'),
        work.get('display_name'),
        work.get('publication_year'),
        work.get('publication_date'),
        work.get('language'),
        work.get('type'),
        work.get('type_crossref'),
        
        # Metrics (6)
        work.get('cited_by_count'),
        work.get('fwci'),
        work.get('has_fulltext'),
        work.get('fulltext_origin'),
        work.get('is_retracted'),
        work.get('is_paratext'),
        
        # STRUCTs (5)
        {
            'openalex': ids.get('openalex'),
            'doi': ids.get('doi'),
            'mag': ids.get('mag'),
            'pmid': ids.get('pmid'),
            'pmcid': ids.get('pmcid')
        } if ids else None,
        
        {
            'is_oa': primary_location.get('is_oa'),
            'landing_page_url': primary_location.get('landing_page_url'),
            'pdf_url': primary_location.get('pdf_url'),
            'source': primary_location.get('source'),
            'license': primary_location.get('license'),
            'version': primary_location.get('version'),
            'is_accepted': primary_location.get('is_accepted'),
            'is_published': primary_location.get('is_published')
        } if primary_location else None,
        
        {
            'is_oa': open_access.get('is_oa'),
            'oa_status': open_access.get('oa_status'),
            'oa_url': open_access.get('oa_url'),
            'any_repository_has_fulltext': open_access.get('any_repository_has_fulltext')
        } if open_access else None,
        
        {
            'id': primary_topic.get('id'),
            'display_name': primary_topic.get('display_name'),
            'score': primary_topic.get('score')
        } if primary_topic else None,
        
        {
            'volume': biblio.get('volume'),
            'issue': biblio.get('issue'),
            'first_page': biblio.get('first_page'),
            'last_page': biblio.get('last_page')
        } if biblio else None,
        
        # Arrays as JSON strings (6)
        str(work.get('concepts', [])),
        str(work.get('topics', [])),
        str(work.get('keywords', [])),
        str(work.get('mesh', [])),
        str(work.get('referenced_works', [])),
        str(work.get('related_works', [])),
        
        # Counts (4)
        work.get('countries_distinct_count'),
        work.get('institutions_distinct_count'),
        work.get('locations_count'),
        work.get('referenced_works_count'),
        
        # Metadata (2)
        work.get('updated_date'),
        work.get('created_date')
    )
    # Total: 9 + 6 + 5 + 6 + 4 + 2 = 32 fields

def process_and_insert_work(work: Dict, conn, corrected_first_year: Optional[int] = None) -> int:
    """Process a work and insert publication + all authorships"""
    work_id = work.get('id')
    if not work_id:
        return 0
    
    # Filter out papers before corrected first year
    if corrected_first_year and work.get('publication_year'):
        if work.get('publication_year') < corrected_first_year:
            return 0  # Skip this paper entirely
    
    # Insert the publication (32 parameters to match the 32 fields)
    publication_data = extract_publication_data(work)
    
    conn.execute("""
        INSERT OR IGNORE INTO oa.raw.publications VALUES 
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, publication_data)
    
    # Process all authorships
    authorships = work.get('authorships', [])
    authorships_inserted = 0
    
    for authorship in authorships:
        author = authorship.get('author', {})
        author_id = author.get('id')
        
        if author_id:  # Only insert if we have an author ID
            authorship_data = (
                work_id,
                author_id,
                author.get('display_name'),
                authorship.get('author_position'),
                json.dumps(authorship.get('institutions', [])),
                json.dumps(authorship.get('raw_affiliation_strings', [])),
                authorship.get('is_corresponding', False)
            )
            
            conn.execute("""
                INSERT OR IGNORE INTO oa.raw.authorships VALUES (?, ?, ?, ?, ?, ?, ?)
            """, authorship_data)
            
            authorships_inserted += 1
    
    return authorships_inserted

def update_uvm_profs_sync_status(conn, ego_author_id: str) -> None:
    """Update the sync status for a professor."""
    conn.execute("""
        UPDATE oa.cache.uvm_profs_sync_status 
        SET 
            last_synced_date = NOW(),
            paper_count = (
                SELECT COUNT(*) FROM oa.raw.authorships 
                WHERE author_id = ?
            ),
            needs_update = FALSE
        WHERE ego_author_id = ?
    """, [ego_author_id, ego_author_id])

def determine_fetch_start_date(ego_author_id: str, conn) -> Optional[str]:
    """
    Determine the earliest date to start fetching publications for a professor.
    
    Strategy:
    1. If we have a corrected first publication year, that's our absolute earliest bound
    2. If we already have publications, we can start from the latest one we have
    3. Choose the later of these two dates to avoid unnecessary re-fetching
    4. Return None if we should fetch all publications (first time sync, no corrections)
    """
    latest_existing = get_latest_publication_date(conn, ego_author_id)
    corrected_first_year = get_corrected_first_pub_year(conn, ego_author_id)
    
    # Convert corrected year to date string if it exists
    corrected_earliest = f"{corrected_first_year}-01-01" if corrected_first_year else None
    
    # Decision logic
    if latest_existing and corrected_earliest:
        # We have both - use whichever is later to avoid gaps
        start_date = max(latest_existing, corrected_earliest)
        reason = f"latest existing ({latest_existing}) vs corrected earliest ({corrected_earliest})"
    elif latest_existing:
        # Only have existing data - continue from there
        start_date = latest_existing
        reason = f"continuing from latest existing publication"
    elif corrected_earliest:
        # Only have correction data - start from corrected year
        start_date = corrected_earliest
        reason = f"starting from corrected first year ({corrected_first_year})"
    else:
        # No existing data or corrections - fetch everything
        start_date = None
        reason = "fetching all publications (first sync, no corrections)"
    
    dg.get_dagster_logger().info(f"{ego_author_id}: {reason} → start_date: {start_date}")
    
    return start_date

@dg.asset(
    description="📚 Fetch all academic papers for 2023 UVM faculties from OpenAlex database.",
    kinds={"openalex"}, 
    deps=["uvm_profs_2023", "uvm_profs_sync_status"],  
)
def uvm_publications(
    oa_resource: OpenAlexResource, 
    duckdb: DuckDBResource
) -> dg.MaterializeResult:
    """Fetch publication data for uvm_profs with proper normalization"""
    
    oa_client = oa_resource.get_client()
    
    with duckdb.get_connection() as conn:
        # Initialize tables and get professors to update
        create_publications_tables(conn)
        create_authorships_table(conn)
        uvm_profs_to_update = get_uvm_profs_to_update(conn)
        
        dg.get_dagster_logger().info(f"Processing {len(uvm_profs_to_update)} uvm_profs")
        
        if not uvm_profs_to_update:
            dg.get_dagster_logger().info("All uvm_profs are up to date!")
            return dg.MaterializeResult(
                metadata={"uvm_profs_processed": 0, "reason": "all_up_to_date"}
            )
        
        total_works_processed = 0
        total_authorships_added = 0
        
        for ego_author_id in uvm_profs_to_update:
            try:
                # Check current data for this professor
                current_count = conn.execute("""
                    SELECT COUNT(*) FROM oa.raw.authorships 
                    WHERE author_id = ?
                """, [ego_author_id]).fetchone()[0]
                
                latest_date = get_latest_publication_date(conn, ego_author_id)
                corrected_first_year = get_corrected_first_pub_year(conn, ego_author_id)
                
                dg.get_dagster_logger().info(
                    f"{ego_author_id}: currently has {current_count} authorships, "
                    f"latest: {latest_date}, corrected first year: {corrected_first_year}"
                )
                
                # Build the filter for OpenAlex API
                filter_parts = [f"author.id:{ego_author_id}"]

                start_date = determine_fetch_start_date(ego_author_id, conn)
                if start_date:
                    filter_parts.append(f"from_publication_date:{start_date}")

                filter_string = ",".join(filter_parts)
                
                # Make API call
                response_data = oa_client.get_works(filter=filter_string)
                works = response_data.get('results', [])
                
                dg.get_dagster_logger().info(f"Found {len(works)} works for {ego_author_id}")
                
                if works:
                    # Process each work
                    for work in works:
                        authorships_added = process_and_insert_work(work, conn, corrected_first_year)
                        total_authorships_added += authorships_added
                    
                    total_works_processed += len(works)
                
                # Update sync status (whether we found works or not)
                update_uvm_profs_sync_status(conn, ego_author_id)
                
                dg.get_dagster_logger().info(f"Processed {ego_author_id}: {len(works)} works")
                    
            except Exception as e:
                dg.get_dagster_logger().error(f"Error fetching publications for {ego_author_id}: {str(e)}")
        
        # Get final statistics
        final_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_publications,
                COUNT(*) as total_authorships,
                COUNT(DISTINCT author_id) as uvm_profs_with_data
            FROM oa.raw.publications p
            JOIN oa.raw.authorships a ON p.id = a.work_id
        """).fetchone()
    
    return dg.MaterializeResult(
        metadata={
            "uvm_profs_processed": len(uvm_profs_to_update),
            "works_processed": total_works_processed,
            "total_publications": final_stats[0],
            "total_authorships": final_stats[1],
            "uvm_profs_with_data": final_stats[2]
        }
    )


@dg.asset(
    kinds={"duckdb"},
    deps=["uvm_profs_2023"]
)
def uvm_profs_sync_status(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """Track when each professor was last synced with OpenAlex"""
    
    with duckdb.get_connection() as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS oa.cache")

        create_uvm_profs_sync_status_table(conn)
        
        conn.execute("""
            INSERT OR IGNORE INTO oa.cache.uvm_profs_sync_status (ego_author_id)
            SELECT DISTINCT ego_author_id 
            FROM oa.raw.uvm_profs_2023
            WHERE ego_author_id IS NOT NULL
        """)
        
        stats = conn.execute("""
            SELECT 
                COUNT(*) as total_uvm_profs,
                COUNT(CASE WHEN needs_update = TRUE OR last_synced_date IS NULL THEN 1 END) as need_update
            FROM oa.cache.uvm_profs_sync_status
        """).fetchone()
    
    return dg.MaterializeResult(
        metadata={
            "total_uvm_profs": stats[0],
            "needs_update": stats[1]
        }
    )


# Updated asset checks for the new schema
@dg.asset_check(
    asset=uvm_publications,
    description="Check publications and authorships data structure",
)
def publications_structure_check(duckdb: DuckDBResource) -> dg.AssetCheckResult:
    """Check that we have proper normalized data"""
    
    with duckdb.get_connection() as conn:
        pub_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_publications,
                COUNT(CASE WHEN primary_location.is_oa = true THEN 1 END) as open_access_count,
                AVG(cited_by_count) as avg_citations
            FROM oa.raw.publications
        """).fetchone()
        
        auth_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_authorships,
                COUNT(DISTINCT author_id) as unique_authors,
                COUNT(DISTINCT work_id) as works_with_authors
            FROM oa.raw.authorships
        """).fetchone()
    
    return dg.AssetCheckResult(
        passed=pub_stats[0] > 0 and auth_stats[0] > 0,
        metadata={
            "total_publications": pub_stats[0],
            "open_access_publications": pub_stats[1],
            "average_citations": round(pub_stats[2], 2) if pub_stats[2] else 0,
            "total_authorships": auth_stats[0],
            "unique_authors": auth_stats[1],
            "works_with_authors": auth_stats[2]
        }
    )


@dg.asset_check(
    asset=uvm_profs_sync_status,
    description="Check professor sync status",
)
def sync_status_check(duckdb: DuckDBResource) -> dg.AssetCheckResult:
    """Check how many uvm_profs need syncing"""
    
    with duckdb.get_connection() as conn:
        stats = conn.execute("""
            SELECT 
                COUNT(*) as total_uvm_profs,
                COUNT(CASE WHEN needs_update = TRUE OR last_synced_date IS NULL THEN 1 END) as need_update,
                COUNT(CASE WHEN last_synced_date IS NOT NULL THEN 1 END) as have_been_synced
            FROM oa.cache.uvm_profs_sync_status
        """).fetchone()
    
    total, need_update, synced = stats
    
    return dg.AssetCheckResult(
        passed=total > 0,
        metadata={
            "total_uvm_profs": total,
            "need_update": need_update,
            "already_synced": synced,
            "sync_percentage": round((synced / total) * 100, 1) if total > 0 else 0
        }
    )