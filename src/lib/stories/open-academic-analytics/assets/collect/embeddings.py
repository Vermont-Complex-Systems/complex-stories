import pandas as pd
import numpy as np

import dagster as dg
from dagster_duckdb import DuckDBResource
from dagster import MaterializeResult, MetadataValue

from config import config

from shared.clients.semantic_scholar_api_client import SemanticScholarEmbeddings
from shared.database.database_adapter import DatabaseExporterAdapter

def save_embeddings_as_npz(embeddings_data, output_file):
    """
    Save embeddings and metadata as .npz file.
    
    Args:
        embeddings_data: List of dicts with embedding info
        output_file: Path to save the .npz file
    """
    if not embeddings_data:
        print("No embeddings to save")
        return
    
    # Separate embeddings from metadata
    embeddings = []
    paper_ids = []
    titles = []
    dois = []
    
    for item in embeddings_data:
        if item['embedding'] is not None:
            embeddings.append(item['embedding'])
            paper_ids.append(item.get('paper_id', ''))
            titles.append(item.get('title', ''))
            dois.append(item.get('doi', ''))
    
    # Convert to numpy arrays
    embeddings_array = np.array(embeddings, dtype=np.float32)
    paper_ids_array = np.array(paper_ids, dtype=object)
    titles_array = np.array(titles, dtype=object)
    dois_array = np.array(dois, dtype=object)
    
    # Save everything in one .npz file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_file,
        embeddings=embeddings_array,
        paper_ids=paper_ids_array,
        titles=titles_array,
        dois=dois_array
    )
    
    print(f"Saved {len(embeddings)} embeddings to {output_file}")

@dg.asset(
    deps=["academic_publications"],
    group_name="import",
    description="🌐 Get paper embeddings from Semantic Scholar API",
)
def embeddings(duckdb: DuckDBResource):
    """
    Main function to process DOIs from database for all ego_aids and save embeddings.
    """
    # Get all papers with DOIs from database
    input_file = config.data_raw_path / config.paper_output_file
    
    with duckdb.get_connection() as conn:
        print("Fetching all papers with DOIs from database...")
        df_pap = pd.read_parquet(input_file)

        print(f"✅ Connected to database")
        conn.execute("CREATE TABLE paper AS SELECT * FROM df_pap")

        db_exporter = DatabaseExporterAdapter(conn)    

        all_papers_df = db_exporter.con.execute(
            "SELECT ego_aid, doi, title FROM df_pap WHERE doi IS NOT NULL"
        ).fetch_df()
        
        print(f"Found {len(all_papers_df)} total papers with DOIs")
        
        # Group by ego_aid
        ego_aid_groups = all_papers_df.groupby('ego_aid')
        print(f"Found {len(ego_aid_groups)} unique ego_aids")
        
        # Initialize the client (works without API key, but slower rate limits)
        api_key = None  # Set to your API key string if you have one for faster processing
        client = SemanticScholarEmbeddings(api_key=api_key)
        
        if api_key:
            print("Using API key - processing up to 500 papers per batch")
        else:
            print("No API key - processing up to 500 papers per batch with slower rate limits")
        
        # Process each ego_aid
        for ego_aid, group_df in ego_aid_groups:
            print(f"\n{'='*60}")
            print(f"Processing ego_aid: {ego_aid}")
            print(f"Papers with DOIs: {len(group_df)}")
            
            # Get DOIs for this ego_aid
            dois = group_df['doi'].tolist()
            
            # Show examples of DOIs before processing
            if len(dois) > 0:
                print(f"Example raw DOI: {dois[0]}")
                print(f"Example cleaned DOI: {client.clean_doi(dois[0])}")
            
            # Get embeddings for this ego_aid's papers using batch API
            print(f"=== Processing Paper Embeddings for {ego_aid} (Batch Mode) ===")
            all_embeddings = client.get_multiple_embeddings(dois, batch_size=500)
            
            # Display results for this ego_aid
            print(f"\nResults for ego_aid {ego_aid}:")
            success_rate = (len(all_embeddings) / len(dois)) * 100 if len(dois) > 0 else 0
            print(f"✓ Successfully retrieved {len(all_embeddings)}/{len(dois)} embeddings ({success_rate:.1f}%)")
            
            # Show sample results
            for i, emb in enumerate(all_embeddings[:3]):  # Show first 3
                print(f"  {i+1}. {emb['title'][:50]}...")
                print(f"     DOI: {emb['doi']}")
                print(f"     Embedding dimension: {len(emb['embedding']) if emb['embedding'] else 'N/A'}")
            
            if len(all_embeddings) > 3:
                print(f"  ... and {len(all_embeddings) - 3} more embeddings")
            
            # Save embeddings as .npz file for this ego_aid
            if all_embeddings:
                output_file = config.embeddings_path / f"{ego_aid}.npz"
                save_embeddings_as_npz(all_embeddings, output_file)
            else:
                print(f"No embeddings found for ego_aid {ego_aid}")
        
        print(f"\n{'='*60}")
        print("PROCESSING COMPLETE!")
        print(f"Processed {len(ego_aid_groups)} ego_aids")
        print("Check individual .npz files for each ego_aid's embeddings")

    return MaterializeResult(
            metadata={
                "input_file": MetadataValue.path(str(input_file)),
                "output_file": MetadataValue.path(str(config.embeddings_path)),
            }
        )