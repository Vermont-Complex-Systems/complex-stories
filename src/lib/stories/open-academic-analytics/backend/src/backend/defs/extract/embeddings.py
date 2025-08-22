import pandas as pd
from datetime import datetime

import dagster as dg
from dagster import MaterializeResult, MetadataValue
from dagster_duckdb import DuckDBResource
from backend.defs.resources import SemanticScholarResource


def create_embedding_table(conn) -> None:
    """Create the embeddings table if it doesn't exist"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS oa.raw.embeddings (
            doi VARCHAR PRIMARY KEY,
            paperId VARCHAR,
            title VARCHAR,
            abstract VARCHAR,
            fieldsOfStudy VARCHAR,
            s2FieldsOfStudy	 VARCHAR,
            embedding FLOAT[],
            status VARCHAR DEFAULT 'success',
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)


def extract_field_categories(field_list):
    """Extract category values from field dictionaries"""
    if not field_list or not isinstance(field_list, list):
        return ''
    return '; '.join(
        field.get('category', '') 
        for field in field_list 
        if isinstance(field, dict)
    )


@dg.asset(
    description="🌐 Get paper embeddings from Semantic Scholar API",
    deps=["uvm_publications"],  
)
def embeddings(
    s2_client: SemanticScholarResource,
    duckdb: DuckDBResource
) -> dg.MaterializeResult:
    """Fetch embeddings for UVM publications that don't have them yet"""
    
    with duckdb.get_connection() as conn:
        print("🚀 Starting embeddings collection...")
        create_embedding_table(conn)
        
        # Find DOIs that need embeddings
        missing_dois = conn.execute("""
            SELECT DISTINCT p.doi 
            FROM oa.raw.publications p 
            LEFT JOIN oa.raw.authorships a ON p.id = a.work_id 
            LEFT JOIN oa.raw.embeddings e ON p.doi = e.doi 
            WHERE a.author_id IN (
                SELECT ego_author_id FROM oa.raw.uvm_profs_2023
            ) 
            -- For now, we just ignore those papers who know has failed
            AND p.doi IS NOT NULL  AND (e.status != 'failed' AND e.status != 'success')
        """).df()
        
        # Clean null DOIs
        missing_dois = missing_dois.dropna(subset=['doi'])
        dois_to_fetch = missing_dois['doi'].tolist()
        
        if not dois_to_fetch:
            print("✅ All DOIs already have embeddings")
            return MaterializeResult(
                metadata={"message": MetadataValue.text("No new embeddings needed")}
            )
        
        print(f"🔄 Fetching embeddings for {len(dois_to_fetch)} DOIs...")
        
        # Fetch embeddings from API
        s2_client = s2_client.get_client()
        api_results = s2_client.get_multiple_embeddings(dois_to_fetch, batch_size=500)
        
        if len(api_results) == 0:
            dg.get_dagster_logger().info("All papers have failed!")
            return dg.MaterializeResult(
                metadata={"successful_embeddings": 0, "reason": "unknown"}
        )
        
        # Process results
        successful_embeddings = []
        failed_dois = []
        
        
        for result in api_results:
            if result and result.get('embedding'):
                successful_embeddings.append({
                    'doi': result['doi'],
                    'paperId': result.get('paperId', ''),
                    'title': result.get('title', ''),
                    'abstract': result.get('abstract', ''),
                    'fieldsOfStudy': '; '.join(result.get('fieldsOfStudy', []) or []),
                    's2FieldsOfStudy	': extract_field_categories(
                        result.get('s2FieldsOfStudy', [])
                    ),
                    'embedding': result['embedding'],
                    'status': 'success',
                    'created_at': datetime.now()
                })
        
        # Track failed DOIs
        successful_dois = {emb['doi'] for emb in successful_embeddings}
        failed_dois = [doi for doi in dois_to_fetch if doi not in successful_dois]
        
        # Save successful embeddings
        if successful_embeddings:
            df = pd.DataFrame(successful_embeddings)
            conn.execute("""
                INSERT INTO oa.raw.embeddings 
                SELECT * FROM df
            """)
            print(f"💾 Saved {len(successful_embeddings)} embeddings")
        
        # Save failed records
        if failed_dois:
            failed_df = pd.DataFrame([
                {
                    'doi': doi,
                    'paperId': '',
                    'title': '',
                    'abstract': '',
                    'fieldsOfStudy': '',
                    's2FieldsOfStudy	': '',
                    'embedding': None,
                    'status': 'failed',
                    'created_at': datetime.now()
                }
                for doi in failed_dois
            ])
            conn.execute("""
                INSERT INTO oa.raw.embeddings 
                SELECT * FROM failed_df
            """)
            print(f"📝 Marked {len(failed_dois)} DOIs as failed")
        
        # Final stats
        total_processed = len(successful_embeddings) + len(failed_dois)
        success_rate = len(successful_embeddings) / total_processed if total_processed > 0 else 0
        
        print(f"🎉 Complete! {len(successful_embeddings)}/{total_processed} successful")
        
        return MaterializeResult(
            metadata={
                "successful_embeddings": MetadataValue.int(len(successful_embeddings)),
                "failed_dois": MetadataValue.int(len(failed_dois)),
                "success_rate": MetadataValue.float(success_rate),
                "total_processed": MetadataValue.int(total_processed)
            }
        )