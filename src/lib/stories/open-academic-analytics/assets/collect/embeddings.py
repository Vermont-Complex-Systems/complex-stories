import pandas as pd
import numpy as np

import dagster as dg
from dagster import MaterializeResult, MetadataValue

from config import config
from shared.clients.semantic_scholar_api_client import SemanticScholarEmbeddings


def extract_field_categories(field_list):
    """Extract category values from a list of field dictionaries."""
    if not field_list:
        return ''
    return '; '.join(field.get('category', '') for field in field_list if isinstance(field, dict))

def save_embeddings_as_npz(embeddings_data, output_file):
    """Save embeddings and metadata as .npz file."""
    if not embeddings_data:
        print("No embeddings to save")
        return
    
    # Filter out items without embeddings and extract data
    valid_items = [item for item in embeddings_data if item.get('embedding') is not None]
    
    if not valid_items:
        print("No valid embeddings to save")
        return
    
    # Extract all fields in one go
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
            extract_field_categories(item.get('s2FieldsOfStudy'))
            for item in valid_items
        ], dtype=object)
    }
    
    # Save to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output_file, **data)
    
    print(f"Saved {len(valid_items)} embeddings to {output_file}")


@dg.asset(
    deps=["academic_publications"],
    group_name="import",
    description="🌐 Get paper embeddings from Semantic Scholar API",
)
def embeddings():
    """Process DOIs from database for all ego_aids and save embeddings."""
    input_file = config.data_raw_path / config.paper_output_file
    
    print("Loading papers from parquet file...")
    df_pap = pd.read_parquet(input_file)
    
    # Filter papers with DOIs and select needed columns
    all_papers_df = df_pap[df_pap['doi'].notna()][['ego_aid', 'doi', 'title']]
    
    print(f"Found {len(all_papers_df)} total papers with DOIs")
    
    # Group by ego_aid
    ego_aid_groups = all_papers_df.groupby('ego_aid')
    print(f"Found {len(ego_aid_groups)} unique ego_aids")
    
    # Initialize client
    api_key = None  # Set to your API key string if you have one
    client = SemanticScholarEmbeddings(api_key=api_key)
    
    rate_limit_msg = "with slower rate limits" if not api_key else ""
    print(f"Processing up to 500 papers per batch {rate_limit_msg}")
    
    # Process each ego_aid
    for ego_aid, group_df in ego_aid_groups:

        output_file = config.embeddings_path / f"{ego_aid}.npz"
        
        # for now just skip if file exists
        if output_file.exists():
            continue

        print(f"\n{'='*60}")
        print(f"Processing ego_aid: {ego_aid}")
        print(f"Papers with DOIs: {len(group_df)}")
        
        dois = group_df['doi'].tolist()
        
        # Get embeddings
        print(f"=== Processing Paper Embeddings for {ego_aid} (Batch Mode) ===")
        all_embeddings = client.get_multiple_embeddings(dois, batch_size=500)
        
        # Display results
        success_rate = (len(all_embeddings) / len(dois)) * 100 if dois else 0
        print(f"✓ Successfully retrieved {len(all_embeddings)}/{len(dois)} embeddings ({success_rate:.1f}%)")
        
        # Show sample results
        for i, emb in enumerate(all_embeddings[:3]):
            print(f"  {i+1}. {emb['title'][:50]}...")
            print(f"     DOI: {emb['doi']}")
            print(f"     Embedding dimension: {len(emb['embedding']) if emb['embedding'] else 'N/A'}")
        
        if len(all_embeddings) > 3:
            print(f"  ... and {len(all_embeddings) - 3} more embeddings")
        
        
        # Save embeddings
        if all_embeddings:
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