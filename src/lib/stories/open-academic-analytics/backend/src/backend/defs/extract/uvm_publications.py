import dagster as dg
from backend.defs.resources import OpenAlexResource
from dagster_duckdb import DuckDBResource
from typing import Any, Dict, List, Tuple, Optional
import json


def create_publications_tables(conn) -> None:
    """Create the publications and authorships tables"""
    
    # Publications table - one record per unique work
    conn.execute("""
        CREATE TABLE IF NOT EXISTS oa.main.publications (
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
    
    # Authorships table - many records per work (one per author)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS oa.main.authorships (
            work_id VARCHAR,
            author_oa_id VARCHAR,
            author_display_name VARCHAR,
            author_position VARCHAR,  -- first, middle, last
            institutions VARCHAR,     -- JSON array of author's institutions for this work
            raw_affiliation_strings VARCHAR,
            is_corresponding BOOLEAN,
            
            PRIMARY KEY (work_id, author_oa_id)
        )
    """)

def get_professors_to_update(conn) -> List[Tuple[str, str]]:
    """Get list of professors who need updating, prioritizing those never synced"""
    result = conn.execute("""
        SELECT s.oa_uid, p.oa_display_name
        FROM oa.main.professor_sync_status s
        JOIN oa.main.uvm_profs_2023 p ON s.oa_uid = p.oa_uid
        WHERE s.needs_update = TRUE 
           OR s.last_synced_date IS NULL
           OR s.last_synced_date < (NOW() - INTERVAL '30 days')
        ORDER BY 
            CASE WHEN s.last_synced_date IS NULL THEN 0 ELSE 1 END,
            s.last_synced_date ASC
    """).fetchall()
    
    return [(row[0], row[1]) for row in result]

def get_latest_publication_date(conn, oa_uid: str) -> Optional[str]:
    """Get the latest publication date for a professor from authorships"""
    result = conn.execute("""
        SELECT MAX(p.publication_date) 
        FROM oa.main.publications p
        JOIN oa.main.authorships a ON p.id = a.work_id
        WHERE a.author_oa_id = ?
    """, [oa_uid]).fetchone()
    
    return result[0] if result and result[0] else None

def get_corrected_first_pub_year(conn, oa_uid: str) -> Optional[int]:
    """Get the corrected first publication year for a UVM professor"""
    result = conn.execute("""
        SELECT first_pub_year 
        FROM oa.main.uvm_profs_2023 
        WHERE 'https://openalex.org/' || oa_uid = ?
    """, [oa_uid]).fetchone()
    
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
        INSERT OR IGNORE INTO oa.main.publications VALUES 
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
                INSERT OR IGNORE INTO oa.main.authorships VALUES (?, ?, ?, ?, ?, ?, ?)
            """, authorship_data)
            
            authorships_inserted += 1
    
    return authorships_inserted

def update_professor_sync_status(conn, oa_uid: str) -> None:
    """Update the sync status for a professor."""
    conn.execute("""
        UPDATE oa.main.professor_sync_status 
        SET 
            last_synced_date = NOW(),
            paper_count = (
                SELECT COUNT(*) FROM oa.main.authorships 
                WHERE author_oa_id = ?
            ),
            needs_update = FALSE
        WHERE oa_uid = ?
    """, [oa_uid, oa_uid])

def determine_fetch_start_date(oa_uid: str, display_name: str, conn) -> Optional[str]:
    """
    Determine the earliest date to start fetching publications for a professor.
    
    Strategy:
    1. If we have a corrected first publication year, that's our absolute earliest bound
    2. If we already have publications, we can start from the latest one we have
    3. Choose the later of these two dates to avoid unnecessary re-fetching
    4. Return None if we should fetch all publications (first time sync, no corrections)
    """
    latest_existing = get_latest_publication_date(conn, oa_uid)
    corrected_first_year = get_corrected_first_pub_year(conn, oa_uid)
    
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
    
    dg.get_dagster_logger().info(f"{display_name}: {reason} → start_date: {start_date}")
    
    return start_date

@dg.asset(
    description="📚 Fetch all academic papers for 2023 UVM faculties from OpenAlex database.",
    kinds={"openalex"}, 
    key=["target", "main", "uvm_publications"],
    deps=["uvm_profs_2023", "professor_sync_status"],  
)
def uvm_publications(
    oa_client: OpenAlexResource, 
    duckdb: DuckDBResource
) -> dg.MaterializeResult:
    """Fetch publication data for UVM professors with proper normalization"""
    
    with duckdb.get_connection() as conn:
        create_publications_tables(conn) # OA schema in duckdb
        professors_to_update = get_professors_to_update(conn) # did we query that prof in the last 30days?
    
    dg.get_dagster_logger().info(f"Processing {len(professors_to_update)} professors")
    
    if not professors_to_update:
        dg.get_dagster_logger().info("All professors are up to date!")
        return dg.MaterializeResult(
            metadata={"professors_processed": 0, "reason": "all_up_to_date"}
        )
    
    total_works_processed = 0
    total_authorships_added = 0
    
    for oa_uid, display_name in professors_to_update:
        try:
            # Check current data for this professor
            with duckdb.get_connection() as conn:
                current_count = conn.execute("""
                    SELECT COUNT(*) FROM oa.main.authorships 
                    WHERE author_oa_id = ?
                """, [oa_uid]).fetchone()[0]
                
                latest_date = get_latest_publication_date(conn, oa_uid)
                corrected_first_year = get_corrected_first_pub_year(conn, oa_uid)
                
                dg.get_dagster_logger().info(
                    f"{display_name}: currently has {current_count} authorships, "
                    f"latest: {latest_date}, corrected first year: {corrected_first_year}"
                )
            
            # Build the filter for OpenAlex API
            filter_parts = [f"author.id:{oa_uid}"]

            start_date = determine_fetch_start_date(oa_uid, display_name, conn)
            if start_date:
                filter_parts.append(f"from_publication_date:{start_date}")

            filter_string = ",".join(filter_parts)
            works = oa_client.get_all_works(filter=filter_string)
            
            dg.get_dagster_logger().info(f"Found {len(works)} works for {display_name}")
            
            if works:
                # Process each work
                with duckdb.get_connection() as conn:
                    for work in works:
                        authorships_added = process_and_insert_work(work, conn, corrected_first_year)
                        total_authorships_added += authorships_added
                    
                    update_professor_sync_status(conn, oa_uid)
                
                total_works_processed += len(works)
            else:
                # Still update sync status even if no new works
                with duckdb.get_connection() as conn:
                    update_professor_sync_status(conn, oa_uid)
            
            dg.get_dagster_logger().info(f"Processed {display_name}: {len(works)} works")
                
        except Exception as e:
            dg.get_dagster_logger().error(f"Error fetching publications for {display_name}: {str(e)}")
    
    # Get final statistics
    with duckdb.get_connection() as conn:
        final_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_publications,
                COUNT(*) as total_authorships,
                COUNT(DISTINCT author_oa_id) as professors_with_data
            FROM oa.main.publications p
            JOIN oa.main.authorships a ON p.id = a.work_id
        """).fetchone()
    
    return dg.MaterializeResult(
        metadata={
            "professors_processed": len(professors_to_update),
            "works_processed": total_works_processed,
            "total_publications": final_stats[0],
            "total_authorships": final_stats[1],
            "professors_with_data": final_stats[2]
        }
    )


@dg.asset(
    kinds={"duckdb"},
    key=["target", "main", "professor_sync_status"],
    deps=["uvm_profs_2023"]
)
def professor_sync_status(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """Track when each professor was last synced with OpenAlex"""
    
    with duckdb.get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS oa.main.professor_sync_status (
                oa_uid VARCHAR PRIMARY KEY,
                last_synced_date TIMESTAMP,
                paper_count INTEGER,
                needs_update BOOLEAN DEFAULT TRUE
            )
        """)
        
        conn.execute("""
            INSERT OR IGNORE INTO oa.main.professor_sync_status (oa_uid)
            SELECT DISTINCT oa_uid 
            FROM oa.main.uvm_profs_2023 
            WHERE oa_uid IS NOT NULL
        """)
        
        stats = conn.execute("""
            SELECT 
                COUNT(*) as total_professors,
                COUNT(CASE WHEN needs_update = TRUE OR last_synced_date IS NULL THEN 1 END) as need_update
            FROM oa.main.professor_sync_status
        """).fetchone()
    
    return dg.MaterializeResult(
        metadata={
            "total_professors": stats[0],
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
            FROM oa.main.publications
        """).fetchone()
        
        auth_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_authorships,
                COUNT(DISTINCT author_oa_id) as unique_authors,
                COUNT(DISTINCT work_id) as works_with_authors
            FROM oa.main.authorships
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
    asset=professor_sync_status,
    description="Check professor sync status",
)
def sync_status_check(duckdb: DuckDBResource) -> dg.AssetCheckResult:
    """Check how many professors need syncing"""
    
    with duckdb.get_connection() as conn:
        stats = conn.execute("""
            SELECT 
                COUNT(*) as total_professors,
                COUNT(CASE WHEN needs_update = TRUE OR last_synced_date IS NULL THEN 1 END) as need_update,
                COUNT(CASE WHEN last_synced_date IS NOT NULL THEN 1 END) as have_been_synced
            FROM oa.main.professor_sync_status
        """).fetchone()
    
    total, need_update, synced = stats
    
    return dg.AssetCheckResult(
        passed=total > 0,
        metadata={
            "total_professors": total,
            "need_update": need_update,
            "already_synced": synced,
            "sync_percentage": round((synced / total) * 100, 1) if total > 0 else 0
        }
    )