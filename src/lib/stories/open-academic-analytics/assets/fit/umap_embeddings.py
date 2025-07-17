import pandas as pd
import numpy as np
from pathlib import Path

import dagster as dg
from dagster import MaterializeResult, MetadataValue

from config import config
import umap


def load_embeddings_as_dataframe(npz_file_path):
    """Load a single .npz file and return as DataFrame with ego_aid."""
    try:
        data = np.load(npz_file_path, allow_pickle=True)
        
        # Validate embeddings exist and aren't empty
        if 'embeddings' not in data or len(data['embeddings']) == 0:
            print(f"Warning: {npz_file_path.name} has no valid embeddings, skipping")
            return None
        
        embeddings = data['embeddings']
        ego_aid = npz_file_path.stem  # filename without extension
        
        # Create DataFrame with all available fields
        df = pd.DataFrame({
            'ego_aid': ego_aid,
            'paper_id': data.get('paper_ids', [''] * len(embeddings)),
            'title': data.get('titles', [''] * len(embeddings)),
            'abstract': data.get('abstract', [''] * len(embeddings)),
            'doi': data.get('dois', [''] * len(embeddings)),
            'fieldsOfStudy': data.get('fieldsOfStudy', [''] * len(embeddings)),
            's2FieldsOfStudy': data.get('s2FieldsOfStudy', [''] * len(embeddings)),
            'embedding': list(embeddings)  # Store as list of arrays
        })
        
        print(f"Loaded {npz_file_path.name}: {len(embeddings)} embeddings, shape {embeddings.shape}")
        return df
        
    except Exception as e:
        print(f"Error loading {npz_file_path.name}: {e}")
        return None


def load_all_embeddings(input_dir):
    """
    Load all .npz files from directory and combine into single DataFrame.
    
    Args:
        input_dir: Path to directory containing .npz files
        
    Returns:
        pandas.DataFrame: Combined embeddings with metadata
    """
    input_dir = Path(input_dir)
    
    if not input_dir.exists():
        raise ValueError(f"Input directory {input_dir} does not exist!")
    
    npz_files = list(input_dir.glob("*.npz"))
    
    if not npz_files:
        raise ValueError(f"No .npz files found in {input_dir}")
    
    print(f"Found {len(npz_files)} embedding files")
    
    # Load all files and combine
    dfs = []
    for npz_file in npz_files:
        df = load_embeddings_as_dataframe(npz_file)
        if df is not None:
            dfs.append(df)
    
    if not dfs:
        raise ValueError("No valid embedding files could be loaded!")
    
    # Combine all DataFrames
    combined_df = pd.concat(dfs, ignore_index=True)
    
    print(f"Combined dataset: {len(combined_df)} total embeddings")
    print(f"Unique ego_aids: {combined_df['ego_aid'].nunique()}")
    
    return combined_df


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
    
    print(f"Embeddings matrix shape: {embeddings_matrix.shape}")
    print(f"UMAP parameters: {umap_params}")
    
    # Initialize UMAP model
    umap_model = umap.UMAP(
        n_components=int(umap_params['n_components']),
        n_neighbors=int(umap_params['n_neighbors']),
        min_dist=float(umap_params['min_dist']),
        metric=umap_params['metric'],
        random_state=int(umap_params['random_state']),
    )
    
    print("Fitting UMAP model...")
    umap_result = umap_model.fit_transform(embeddings_matrix)
    
    # Create results DataFrame (copy without embeddings to save space)
    results_df = embeddings_df.drop('embedding', axis=1).copy()
    
    # Add UMAP coordinates
    n_components = int(umap_params['n_components'])
    for i in range(n_components):
        results_df[f'umap_{i+1}'] = umap_result[:, i]
    
    print(f"UMAP reduction complete: {embeddings_matrix.shape[1]}D -> {n_components}D")
    
    return results_df


@dg.asset(
    deps=["embeddings"],
    group_name="model",
    description="🌐 Apply UMAP dimensionality reduction to embeddings",
)
def umap_embeddings():
    """Apply UMAP dimensionality reduction to all embeddings and save results."""
    input_dir = config.embeddings_path
    output_file = config.data_processed_path / config.embeddings_file
    
    # Load all embeddings
    embeddings_df = load_all_embeddings(input_dir)
    
    # Apply UMAP reduction
    umap_params = config.UMAP_CONFIG
    results_df = apply_umap_reduction(embeddings_df, umap_params)
    
    # Save results
    output_file.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_parquet(output_file, index=False)
    
    print(f"Saved UMAP results to {output_file}")
    print(f"Final dataset shape: {results_df.shape}")
    
    # Show sample of results
    print("\nSample of results:")
    umap_cols = [col for col in results_df.columns if col.startswith('umap_')]
    sample_cols = ['ego_aid', 'title', 'abstract', 'fieldsOfStudy', 's2FieldsOfStudy'] + umap_cols
    print(results_df[sample_cols].head())

    return MaterializeResult(
        metadata={
            "input_dir": MetadataValue.path(str(input_dir)),
            "output_file": MetadataValue.path(str(output_file)),
            "num_embeddings": len(results_df),
            "num_ego_aids": results_df['ego_aid'].nunique(),
            "embedding_dimension": len(embeddings_df['embedding'].iloc[0]),
            "umap_components": int(umap_params['n_components']),
            "umap_neighbors": int(umap_params['n_neighbors']),
            "umap_min_dist": float(umap_params['min_dist']),
        }
    )