import pandas as pd
import numpy as np

import dagster as dg
from dagster import MaterializeResult, MetadataValue

from config import config
import umap


def load_embedding_files(input_dir):
    """
    Load all embedding .npz files from the input directory.
    
    Returns:
        list: List of tuples (filename, data_dict)
    """
    embedding_files = []
    
    if not input_dir.exists():
        print(f"Input directory {input_dir} does not exist!")
        return embedding_files
    
    npz_files = list(input_dir.glob("*.npz"))
    
    if not npz_files:
        print(f"No .npz files found in {input_dir}")
        return embedding_files
    
    print(f"Found {len(npz_files)} embedding files")
    
    for file_path in npz_files:
        try:
            # Load the .npz file
            data = np.load(file_path, allow_pickle=True)
            
            # Validate that the file has the expected arrays
            if 'embeddings' not in data:
                print(f"Warning: {file_path.name} doesn't have 'embeddings' array, skipping")
                continue
            
            embeddings = data['embeddings']
            if len(embeddings) == 0:
                print(f"Warning: {file_path.name} has no embeddings, skipping")
                continue
            
            print(f"Loaded {file_path.name}: {len(embeddings)} embeddings with shape {embeddings.shape}")
            
            # Create a data dictionary
            file_data = {
                'embeddings': embeddings,
                'paper_ids': data.get('paper_ids', np.array([''] * len(embeddings))),
                'titles': data.get('titles', np.array([''] * len(embeddings))),
                'dois': data.get('dois', np.array([''] * len(embeddings)))
            }
            
            embedding_files.append((file_path.stem, file_data))
            
        except Exception as e:
            print(f"Error loading {file_path.name}: {e}")
    
    return embedding_files


def prepare_embeddings_matrix(embedding_files):
    """
    Combine all embeddings into a single matrix and create metadata dataframe.
    
    Args:
        embedding_files: List of (filename, data_dict) tuples
        
    Returns:
        tuple: (embeddings_matrix, metadata_dataframe)
    """
    all_embeddings = []
    all_metadata = []
    
    for filename, data in embedding_files:
        # Extract ego_aid from filename
        ego_aid = filename
        
        embeddings = data['embeddings']
        paper_ids = data['paper_ids']
        titles = data['titles']
        dois = data['dois']
        
        for i in range(len(embeddings)):
            all_embeddings.append(embeddings[i])
            
            metadata = {
                'ego_aid': ego_aid,
                'paper_id': paper_ids[i] if i < len(paper_ids) else '',
                'title': titles[i] if i < len(titles) else '',
                'doi': dois[i] if i < len(dois) else ''
            }
            all_metadata.append(metadata)
    
    if not all_embeddings:
        raise ValueError("No valid embeddings found across all files!")
    
    # Convert to numpy array (already in correct format)
    embeddings_matrix = np.vstack(all_embeddings)
    metadata_df = pd.DataFrame(all_metadata)
    
    print(f"Combined embeddings matrix shape: {embeddings_matrix.shape}")
    print(f"Metadata dataframe shape: {metadata_df.shape}")
    
    return embeddings_matrix, metadata_df


@dg.asset(
    deps=["embeddings"],
    group_name="model",
    description="🌐 Model fitting",
)
def umap_embeddings():
    input_dir = config.embeddings_path
    output_file = config.data_processed_path / config.embeddings_file
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    embedding_files = load_embedding_files(input_dir)
    
    if not embedding_files:
        raise ValueError(f"No embedding files found in {input_dir}")
    
    umap_params = config.UMAP_CONFIG
    print(f"UMAP parameters: {umap_params}")
    
    embeddings_matrix, metadata_df = prepare_embeddings_matrix(embedding_files)

    # Convert float values to int for parameters that expect integers
    umap_model = umap.UMAP(
        n_components=int(umap_params['n_components']),
        n_neighbors=int(umap_params['n_neighbors']),
        min_dist=float(umap_params['min_dist']),
        metric=umap_params['metric'],
        random_state=int(umap_params['random_state']),
    )
    
    print("Fitting UMAP model...")
    umap_embeddings_result = umap_model.fit_transform(embeddings_matrix)
    
    # Create results dataframe
    results_df = metadata_df.copy()
    
    # Add UMAP coordinates
    n_components = int(umap_params['n_components'])
    for i in range(n_components):
        results_df[f'umap_{i+1}'] = umap_embeddings_result[:, i]
    
    print(f"Saving results to {output_file}")
    results_df.to_parquet(output_file)

    return MaterializeResult(
        metadata={
            "input_dir": MetadataValue.path(str(input_dir)),
            "output_file": MetadataValue.path(str(output_file)),
            "num_embeddings": len(results_df),
            "embedding_dimension": embeddings_matrix.shape[1],
            "umap_components": n_components,
        }
    )