import pandas as pd
import numpy as np

import dagster as dg
from dagster import MaterializeResult, MetadataValue
from dagster_duckdb import DuckDBResource

from config import config
import umap


def load_all_embeddings_from_duckdb(duckdb_connection):
    """
    Load all successful embeddings directly from DuckDB.
    
    Args:
        duckdb_connection: DuckDB connection
        
    Returns:
        pandas.DataFrame: Combined embeddings with metadata
    """
    # Load the master parquet cache into DuckDB
    existing_embeddings_file = config.embeddings_path / "all_embeddings.parquet"
    
    if not existing_embeddings_file.exists():
        raise ValueError(f"No embeddings cache found at {existing_embeddings_file}")
    
    print("📥 Loading embeddings from master cache...")
    existing_df = pd.read_parquet(existing_embeddings_file)
    duckdb_connection.execute("CREATE TEMPORARY TABLE temp_embeddings AS SELECT * FROM existing_df")
    
    # Get all successful embeddings with paper metadata
    embeddings_df = duckdb_connection.execute("""
        SELECT 
            paper_id,
            title,
            abstract,
            doi,
            fields_of_study as fieldsOfStudy,
            s2_fields_of_study as s2FieldsOfStudy,
            embedding,
            created_at
        FROM temp_embeddings 
        WHERE status = 'success' 
        AND embedding IS NOT NULL
        ORDER BY created_at
    """).df()
    
    if len(embeddings_df) == 0:
        raise ValueError("No successful embeddings found in cache!")
    
    print(f"✅ Loaded {len(embeddings_df)} successful embeddings from cache")
    
    # Get ego_aid mapping from papers
    papers_file = config.data_raw_path / config.paper_output_file
    if papers_file.exists():
        papers_df = pd.read_parquet(papers_file)[['doi', 'ego_aid']]
        
        # Join to get ego_aid for each embedding
        embeddings_df = embeddings_df.merge(
            papers_df, 
            on='doi', 
            how='left'
        )
        
        print(f"📊 Mapped {embeddings_df['ego_aid'].notna().sum()}/{len(embeddings_df)} embeddings to researchers")
    else:
        print("⚠️  No papers file found - ego_aid will be missing")
        embeddings_df['ego_aid'] = 'unknown'
    
    # Show summary stats
    print(f"📈 Dataset summary:")
    print(f"  Total embeddings: {len(embeddings_df)}")
    print(f"  Unique researchers: {embeddings_df['ego_aid'].nunique()}")
    print(f"  Embedding dimension: {len(embeddings_df['embedding'].iloc[0]) if len(embeddings_df) > 0 else 'N/A'}")
    
    return embeddings_df


def apply_umap_reduction(embeddings_df, umap_params):
    """
    Apply UMAP dimensionality reduction to embeddings.
    
    Args:
        embeddings_df: DataFrame with 'embedding' column
        umap_params: Dictionary of UMAP parameters
        
    Returns:
        pandas.DataFrame: Original data with UMAP coordinates added
    """
    # Extract embeddings matrix
    embeddings_matrix = np.vstack(embeddings_df['embedding'].values)
    
    print(f"🔢 Embeddings matrix shape: {embeddings_matrix.shape}")
    print(f"⚙️  UMAP parameters: {umap_params}")
    
    # Initialize UMAP model
    umap_model = umap.UMAP(
        n_components=int(umap_params['n_components']),
        n_neighbors=int(umap_params['n_neighbors']),
        min_dist=float(umap_params['min_dist']),
        metric=umap_params['metric'],
        random_state=int(umap_params['random_state']),
    )
    
    print("🧮 Fitting UMAP model...")
    umap_result = umap_model.fit_transform(embeddings_matrix)
    
    # Create results DataFrame (copy without embeddings to save space)
    results_df = embeddings_df.drop('embedding', axis=1).copy()
    
    # Add UMAP coordinates
    n_components = int(umap_params['n_components'])
    for i in range(n_components):
        results_df[f'umap_{i+1}'] = umap_result[:, i]
    
    print(f"✨ UMAP reduction complete: {embeddings_matrix.shape[1]}D -> {n_components}D")
    
    return results_df


@dg.asset(
    deps=["embeddings"],
    group_name="model",
    description="🌐 Apply UMAP dimensionality reduction to embeddings from DuckDB cache",
)
def umap_embeddings(duckdb: DuckDBResource):
    """Apply UMAP dimensionality reduction to all embeddings using DuckDB cache."""
    output_file = config.data_processed_path / config.embeddings_file
    
    with duckdb.get_connection() as conn:
        # Load all embeddings from DuckDB cache
        embeddings_df = load_all_embeddings_from_duckdb(conn)
        
        # Apply UMAP reduction
        umap_params = config.UMAP_CONFIG
        results_df = apply_umap_reduction(embeddings_df, umap_params)
        
        # Save results
        output_file.parent.mkdir(parents=True, exist_ok=True)
        results_df.to_parquet(output_file, index=False)
        
        print(f"💾 Saved UMAP results to {output_file}")
        print(f"📊 Final dataset shape: {results_df.shape}")
        
        # Show sample of results
        print(f"\n🔍 Sample results:")
        umap_cols = [col for col in results_df.columns if col.startswith('umap_')]
        sample_cols = ['ego_aid', 'title', 'fieldsOfStudy', 's2FieldsOfStudy'] + umap_cols
        available_cols = [col for col in sample_cols if col in results_df.columns]
        print(results_df[available_cols].head(3))

        return MaterializeResult(
            metadata={
                "input_source": MetadataValue.text("DuckDB unified cache"),
                "output_file": MetadataValue.path(str(output_file)),
                "total_embeddings": MetadataValue.int(len(results_df)),
                "unique_researchers": MetadataValue.int(results_df['ego_aid'].nunique()),
                "embedding_dimension": MetadataValue.int(len(embeddings_df['embedding'].iloc[0]) if len(embeddings_df) > 0 else 0),
                "umap_components": MetadataValue.int(int(umap_params['n_components'])),
                "features": MetadataValue.md(
                    "• **DuckDB source**: Reads from unified embeddings cache  \n"
                    "• **Status filtering**: Only processes successful embeddings  \n"
                    "• **Auto ego_aid mapping**: Links embeddings to researchers via papers  \n"
                    "• **Memory efficient**: Drops embedding vectors after UMAP  \n"
                    "• **Comprehensive metadata**: Preserves all paper metadata"
                ),
                "umap_config": MetadataValue.md(
                    f"n_components: {umap_params['n_components']}, "
                    f"n_neighbors: {umap_params['n_neighbors']}, "
                    f"min_dist: {umap_params['min_dist']}, "
                    f"metric: {umap_params['metric']}"
                )
            }
        )