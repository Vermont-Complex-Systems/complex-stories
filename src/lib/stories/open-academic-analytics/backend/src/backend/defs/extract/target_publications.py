import dagster as dg
from backend.defs.resources import OpenAlexResource
from dagster_duckdb import DuckDBResource
from typing import Any

@dg.asset(
    kinds={"openalex"}, 
    key=["target", "main", "uvm_publications"],
    deps=["uvm_profs_2023"],
)
def uvm_publications(
    oa_client: OpenAlexResource, 
    duckdb: DuckDBResource
) -> dg.MaterializeResult:
    """Fetch all publication data for UVM professors using proper OpenAlex schema"""
    
    # Get the list of oa_uids from our professors table
    with duckdb.get_connection() as conn:
        # First, create the table with proper OpenAlex schema
        conn.execute("""
            CREATE OR REPLACE TABLE oa.main.uvm_publications (
                professor_oa_uid VARCHAR,
                professor_name VARCHAR,
                
                -- Core OpenAlex fields
                id VARCHAR,
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
                
                -- Arrays as VARCHAR for now (can parse later)
                authorships VARCHAR,  -- JSON array
                concepts VARCHAR,     -- JSON array
                topics VARCHAR,       -- JSON array
                keywords VARCHAR,     -- JSON array
                mesh VARCHAR,         -- JSON array
                referenced_works VARCHAR,  -- JSON array
                related_works VARCHAR,     -- JSON array
                
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
        
        result = conn.execute("""
            SELECT oa_uid, oa_display_name 
            FROM oa.main.uvm_profs_2023 
            WHERE oa_uid IS NOT NULL
            LIMIT 5  -- Start with 5 professors
        """).fetchall()
        
        professors = [(row[0], row[1]) for row in result]
    
    dg.get_dagster_logger().info(f"Processing {len(professors)} professors")
    
    total_publications = 0
    
    # Process each professor
    for oa_uid, display_name in professors:
        dg.get_dagster_logger().info(f"Fetching publications for {display_name} ({oa_uid})")
        
        try:
            response_data = oa_client.get_works(filter=f"author.id:{oa_uid}", per_page=200)
            works = response_data.get('results', [])
            
            dg.get_dagster_logger().info(f"Found {len(works)} publications for {display_name}")
            
            if works:
                # Prepare data for insertion
                publication_data = []
                for work in works:
                    # Extract nested structures safely
                    ids = work.get('ids', {})
                    primary_location = work.get('primary_location', {})
                    open_access = work.get('open_access', {})
                    primary_topic = work.get('primary_topic', {})
                    biblio = work.get('biblio', {})
                    
                    publication_data.append((
                        oa_uid,
                        display_name,
                        work.get('id'),
                        work.get('doi'),
                        work.get('title'),
                        work.get('display_name'),
                        work.get('publication_year'),
                        work.get('publication_date'),
                        work.get('language'),
                        work.get('type'),
                        work.get('type_crossref'),
                        work.get('cited_by_count'),
                        work.get('fwci'),
                        work.get('has_fulltext'),
                        work.get('fulltext_origin'),
                        work.get('is_retracted'),
                        work.get('is_paratext'),
                        
                        # STRUCT for ids
                        {
                            'openalex': ids.get('openalex'),
                            'doi': ids.get('doi'),
                            'mag': ids.get('mag'),
                            'pmid': ids.get('pmid'),
                            'pmcid': ids.get('pmcid')
                        } if ids else None,
                        
                        # STRUCT for primary_location
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
                        
                        # STRUCT for open_access
                        {
                            'is_oa': open_access.get('is_oa'),
                            'oa_status': open_access.get('oa_status'),
                            'oa_url': open_access.get('oa_url'),
                            'any_repository_has_fulltext': open_access.get('any_repository_has_fulltext')
                        } if open_access else None,
                        
                        # STRUCT for primary_topic
                        {
                            'id': primary_topic.get('id'),
                            'display_name': primary_topic.get('display_name'),
                            'score': primary_topic.get('score')
                        } if primary_topic else None,
                        
                        # STRUCT for biblio
                        {
                            'volume': biblio.get('volume'),
                            'issue': biblio.get('issue'),
                            'first_page': biblio.get('first_page'),
                            'last_page': biblio.get('last_page')
                        } if biblio else None,
                        
                        # Arrays as JSON strings for now
                        str(work.get('authorships', [])),
                        str(work.get('concepts', [])),
                        str(work.get('topics', [])),
                        str(work.get('keywords', [])),
                        str(work.get('mesh', [])),
                        str(work.get('referenced_works', [])),
                        str(work.get('related_works', [])),
                        
                        work.get('countries_distinct_count'),
                        work.get('institutions_distinct_count'),
                        work.get('locations_count'),
                        work.get('referenced_works_count'),
                        work.get('updated_date'),
                        work.get('created_date')
                    ))
                
                # Insert the data
                with duckdb.get_connection() as conn:
                    conn.executemany("""
                        INSERT INTO oa.main.uvm_publications VALUES 
                        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, publication_data)
                
                total_publications += len(works)
                
        except Exception as e:
            dg.get_dagster_logger().error(f"Error fetching publications for {display_name}: {str(e)}")
    
    # Get final count
    with duckdb.get_connection() as conn:
        final_count = conn.execute(
            "SELECT COUNT(*) FROM oa.main.uvm_publications"
        ).fetchone()[0]
    
    return dg.MaterializeResult(
        metadata={
            "professors_processed": len(professors),
            "total_publications": final_count
        }
    )

@dg.asset_check(
    asset=uvm_publications,
    description="Check OpenAlex publication data structure",
)
def publications_structure_check(duckdb: DuckDBResource) -> dg.AssetCheckResult:
    """Check that we have proper structured data"""
    
    with duckdb.get_connection() as conn:
        # Test STRUCT access
        result = conn.execute("""
            SELECT 
                COUNT(*) as total_pubs,
                COUNT(DISTINCT professor_oa_uid) as unique_professors,
                COUNT(CASE WHEN primary_location.is_oa = true THEN 1 END) as open_access_count,
                AVG(cited_by_count) as avg_citations,
                COUNT(CASE WHEN primary_topic.id IS NOT NULL THEN 1 END) as with_topics
            FROM oa.main.uvm_publications
        """).fetchone()
        
        total_pubs, unique_profs, oa_count, avg_cites, with_topics = result
    
    return dg.AssetCheckResult(
        passed=total_pubs > 0,
        metadata={
            "total_publications": total_pubs,
            "unique_professors": unique_profs,
            "open_access_publications": oa_count,
            "average_citations": round(avg_cites, 2) if avg_cites else 0,
            "publications_with_topics": with_topics
        }
    )