import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path

import dagster as dg
from dagster import MaterializeResult, MetadataValue
from dagster_duckdb import DuckDBResource
from backend.defs.resources import SemanticScholarResource

def create_embedding_table(conn) -> None:
    """Create the publications and authorships tables"""
    
    # Publications table - one record per unique work
    conn.execute("""
            CREATE TABLE IF NOT EXISTS oa.main.embeddings (
                doi VARCHAR PRIMARY KEY,
                paper_id VARCHAR,
                title VARCHAR,
                abstract VARCHAR,
                fields_of_study VARCHAR,
                s2_fields_of_study VARCHAR,
                embedding FLOAT[],
                status VARCHAR DEFAULT 'success',
                created_at TIMESTAMP DEFAULT NOW(),
                last_retry_at TIMESTAMP
        )
    """)
    

def extract_field_categories(field_list):
    """Extract category values from a list of field dictionaries."""
    if not field_list:
        return ''
    return '; '.join(field.get('category', '') for field in field_list if isinstance(field, dict))


@dg.asset(
    deps=["academic_publications"],
    group_name="import", 
    description="🌐 Get paper embeddings from Semantic Scholar API with DuckDB caching",
)
def embeddings(
    s2_client: SemanticScholarResource,
    duckdb: DuckDBResource
    ) -> dg.MaterializeResult:
    """Process DOIs with smart DuckDB-based caching to minimize API calls."""
    
    with duckdb.get_connection() as conn:
        print("🚀 Starting embeddings collection with DuckDB caching...")
        create_embedding_table(conn) # embedding table
        
        papers_with_dois = conn.execute("""
                        SELECT DISTINCT p.id, p.doi, a.author_oa_id, p.title
                        FROM oa.main.publications p
                        LEFT JOIN oa.main.authorships a ON p.id = a.work_id
                        WHERE 
                            a.author_oa_id IN (SELECT 'https://openalex.org/' || oa_uid FROM oa.main.uvm_profs_2023)
                            AND doi IS NOT NULL
                                 """).df()
        
        print(f"📊 Found {len(papers_with_dois)} papers with DOIs")
        
        # # Load existing embeddings into DuckDB from master cache
        # existing_embeddings_file = config.embeddings_path / "all_embeddings.parquet"
        
        # if existing_embeddings_file.exists():
        #     print("📥 Loading existing embeddings from master cache...")
        #     existing_df = pd.read_parquet(existing_embeddings_file)
        #     conn.execute("INSERT INTO embeddings SELECT * FROM existing_df ON CONFLICT DO NOTHING")
        #     print(f"  ✅ Loaded {len(existing_df)} existing records")
            
        #     # Show cache stats
        #     cache_stats = conn.execute("""
        #         SELECT status, COUNT(*) as count
        #         FROM embeddings 
        #         GROUP BY status
        #     """).df()
        #     for _, row in cache_stats.iterrows():
        #         print(f"    {row['status']}: {row['count']} DOIs")
        # else:
        #     print("📭 No existing embeddings found - starting fresh")
        
        # Find DOIs we need to process
        all_dois = papers_with_dois['doi'].unique().tolist()
        # all_dois_df = pd.DataFrame({'doi': all_dois})
        
        # if config.retry_failed_dois:
        #     print("🔄 Config enabled: will retry previously failed DOIs")
        #     # Get DOIs that have no record OR failed status
        #     missing_dois_df = conn.execute("""
        #         SELECT a.doi
        #         FROM all_dois_df a
        #         LEFT JOIN embeddings e ON a.doi = e.doi
        #         WHERE e.doi IS NULL OR e.status = 'failed'
        #     """).df()
        # else:
        #     print("⏭️  Config disabled retry - only processing truly missing DOIs")
        #     # Only get DOIs with no record at all
        #     missing_dois_df = conn.execute("""
        #         SELECT a.doi
        #         FROM all_dois_df a
        #         LEFT JOIN embeddings e ON a.doi = e.doi
        #         WHERE e.doi IS NULL
        #     """).df()
        
        # missing_dois = missing_dois_df['doi'].tolist() if len(missing_dois_df) > 0 else []
        missing_dois = all_dois
        
        # Get stats for reporting
        # total_cached = conn.execute("""
        #     SELECT COUNT(*) as count FROM embeddings e
        #     JOIN all_dois_df a ON e.doi = a.doi
        #     WHERE e.status = 'success'
        # """).fetchone()[0]
        
        # retry_count = 0
        # if config.retry_failed_dois:
        #     retry_count = conn.execute("""
        #         SELECT COUNT(*) as count FROM embeddings e
        #         JOIN all_dois_df a ON e.doi = a.doi
        #         WHERE e.status = 'failed'
        #     """).fetchone()[0]
        
        # print(f"🎯 API Strategy:")
        # print(f"  ✅ {total_cached} DOIs successfully cached ({total_cached/len(all_dois)*100:.1f}%)")
        # if retry_count > 0:
        #     print(f"  🔄 {retry_count} failed DOIs to retry")
        # print(f"  🌐 {len(missing_dois)} total DOIs need API calls")
        
        # Initialize s2_client and fetch missing embeddings
        new_embeddings = []
        api_calls_made = 0
        
        if missing_dois:
            print(f"\n🔄 Fetching {len(missing_dois)} missing embeddings...")
            
            # Determine batch size
            batch_size = min(500, len(missing_dois))
            
            try:
                # Single batch API call for all missing DOIs
                api_results = s2_client.get_multiple_embeddings(missing_dois, batch_size=batch_size)
                api_calls_made = 1
                
                # Convert to database format
                for item in api_results:
                    if item.get('embedding') is not None:
                        new_embeddings.append({
                            'doi': item['doi'],
                            'paper_id': item.get('paper_id', item['doi']),
                            'title': item.get('title', ''),
                            'abstract': item.get('abstract', ''),
                            'fields_of_study': '; '.join(item.get('fieldsOfStudy', [])),
                            's2_fields_of_study': extract_field_categories(item.get('s2FieldsOfStudy')),
                            'embedding': item['embedding'],
                            'created_at': datetime.now()
                        })
                
                print(f"  ✅ Successfully fetched {len(new_embeddings)}/{len(missing_dois)} embeddings")
                
            except Exception as e:
                print(f"  ❌ Error fetching embeddings: {e}")
        
        # Save results to DuckDB (both successes and failures)
        if missing_dois:
            # Track which DOIs succeeded and failed
            fetched_dois = set(emb['doi'] for emb in new_embeddings) if new_embeddings else set()
            failed_dois = [doi for doi in missing_dois if doi not in fetched_dois]
            
            # Save successful embeddings
            if new_embeddings:
                # Add status and timestamp columns to match table schema
                new_df = pd.DataFrame(new_embeddings)
                new_df['status'] = 'success'
                new_df['last_retry_at'] = datetime.now()
                
                # Ensure column order matches table schema
                new_df = new_df[['doi', 'paper_id', 'title', 'abstract', 'fields_of_study', 
                               's2_fields_of_study', 'embedding', 'status', 'created_at', 'last_retry_at']]
                
                conn.execute("""
                    INSERT INTO embeddings 
                    (doi, paper_id, title, abstract, fields_of_study, s2_fields_of_study, 
                     embedding, status, created_at, last_retry_at)
                    SELECT * FROM new_df 
                    ON CONFLICT (doi) DO UPDATE SET 
                        embedding = EXCLUDED.embedding, 
                        status = 'success', 
                        last_retry_at = NOW()
                """)
                print(f"  💾 Saved {len(new_embeddings)} successful embeddings")
            
            # Save failed DOIs (so we don't keep retrying them unless explicitly enabled)
            if failed_dois:
                failed_df = pd.DataFrame([{
                    'doi': doi,
                    'paper_id': doi,
                    'title': '',
                    'abstract': '',
                    'fields_of_study': '',
                    's2_fields_of_study': '',
                    'embedding': None,
                    'status': 'failed',
                    'created_at': datetime.now(),
                    'last_retry_at': datetime.now(),
                } for doi in failed_dois])
                
                # Insert failed records
                for _, row in failed_df.iterrows():
                    conn.execute("""
                        INSERT INTO embeddings 
                        (doi, paper_id, title, abstract, fields_of_study, s2_fields_of_study, 
                         embedding, status, created_at, last_retry_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT (doi) DO UPDATE SET 
                            status = 'failed', 
                            last_retry_at = NOW()
                    """, (
                        row['doi'], row['paper_id'], row['title'], row['abstract'],
                        row['fields_of_study'], row['s2_fields_of_study'], row['embedding'],
                        row['status'], row['created_at'], row['last_retry_at']
                    ))
                
                print(f"  📝 Marked {len(failed_dois)} DOIs as failed (won't retry unless config enabled)")
        
        # Get final stats
        final_stats = conn.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                COUNT(*) as total
            FROM embeddings e
            JOIN all_dois_df a ON e.doi = a.doi
        """).fetchone()
        
        successful_count, failed_count, total_count = final_stats
                
        # Export master parquet file (includes both successful and failed records)
        # all_embeddings_df = conn.execute("SELECT * FROM embeddings").df()
        # config.embeddings_path.mkdir(parents=True, exist_ok=True)
        # all_embeddings_df.to_parquet(existing_embeddings_file)
        
        print(f"\n🎉 PROCESSING COMPLETE!")
        print(f"  ✅ Successful embeddings: {successful_count}")
        print(f"  ❌ Failed DOIs: {failed_count}")
        print(f"  🌐 API calls made: {api_calls_made}")
        # print(f"  💾 Master cache: {existing_embeddings_file}")
        
        success_rate = successful_count / total_count if total_count > 0 else 0
        
        return MaterializeResult(
            metadata={
                "successful_embeddings": MetadataValue.int(successful_count),
                "failed_dois": MetadataValue.int(failed_count),
                "success_rate": MetadataValue.float(success_rate),
                "api_calls_made": MetadataValue.int(api_calls_made),
                "output_directory": MetadataValue.path(str(config.embeddings_path)),
                "master_cache": MetadataValue.path(str(existing_embeddings_file)),
                "features": MetadataValue.md(
                    "• **Unified caching**: Single parquet file tracks both successes and failures  \n"
                    "• **Smart retry logic**: Configurable retry of previously failed DOIs  \n"
                    "• **Status tracking**: 'success' or 'failed' status for each DOI  \n"
                    "• **Automatic deduplication**: DOI-based primary key prevents duplicates  \n"
                    "• **Selective export**: Only successful embeddings in researcher files"
                ),
                "config_notes": MetadataValue.md(
                    f"`retry_failed_dois = {getattr(config, 'retry_failed_dois', False)}`. "
                    "When True, retries previously failed DOIs. When False, skips them for speed."
                )
            }
        )


def save_embeddings_as_npz(embeddings_data, output_file):
    """Save embeddings and metadata as .npz file."""
    if not embeddings_data:
        return
    
    # Filter valid embeddings
    valid_items = [item for item in embeddings_data if item.get('embedding') is not None]
    if not valid_items:
        return
    
    # Convert to numpy arrays
    data = {
        'embeddings': np.array([item['embedding'] for item in valid_items], dtype=np.float32),
        'paper_ids': np.array([item.get('paper_id', '') for item in valid_items], dtype=object),
        'titles': np.array([item.get('title', '') for item in valid_items], dtype=object),
        'abstract': np.array([item.get('abstract', '') for item in valid_items], dtype=object),
        'dois': np.array([item.get('doi', '') for item in valid_items], dtype=object),
        'fieldsOfStudy': np.array([
            '; '.join(item.get('fieldsOfStudy', [])) if item.get('fieldsOfStudy') else ''
            for item in valid_items
        ], dtype=object),
        's2FieldsOfStudy': np.array([
            item.get('s2FieldsOfStudy', '') for item in valid_items
        ], dtype=object)
    }
    
    # Save to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output_file, **data)
    
    print(f"  💾 {output_file.name}: {len(valid_items)} embeddings")