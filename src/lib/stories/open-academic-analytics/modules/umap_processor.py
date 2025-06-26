import os
import pandas as pd
import numpy as np
import umap
from pathlib import Path
from typing import List, Dict, Tuple
import pickle
import argparse

class UMAPProcessor:
    """
    A class to process paper embeddings and compute UMAP dimensionality reduction.
    """
    
    def __init__(self, input_dir: str = "data/raw/embeddings", 
                 output_dir: str = "data/processed/umap_embeddings",
                 n_components: int = 2, n_neighbors: int = 15, min_dist: float = 0.1,
                 random_state: int = 42, metric: str = "euclidean", 
                 output_name: str = "umap_results", verbose: bool = False):
        """
        Initialize the UMAP processor.
        
        Args:
            input_dir (str): Directory containing embedding parquet files
            output_dir (str): Directory to save UMAP results
            n_components (int): Number of UMAP dimensions (default: 2 for visualization)
            n_neighbors (int): UMAP n_neighbors parameter
            min_dist (float): UMAP min_dist parameter
            random_state (int): Random state for reproducibility
            metric (str): Distance metric for UMAP
            output_name (str): Base name for output files
            verbose (bool): Enable verbose output
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.n_components = n_components
        self.n_neighbors = n_neighbors
        self.min_dist = min_dist
        self.random_state = random_state
        self.metric = metric
        self.output_name = output_name
        self.verbose = verbose
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_embedding_files(self) -> List[Tuple[str, pd.DataFrame]]:
        """
        Load all embedding parquet files from the input directory.
        
        Returns:
            list: List of tuples (filename, dataframe)
        """
        embedding_files = []
        
        if not self.input_dir.exists():
            print(f"Input directory {self.input_dir} does not exist!")
            return embedding_files
        
        parquet_files = list(self.input_dir.glob("*.parquet"))
        
        if not parquet_files:
            print(f"No parquet files found in {self.input_dir}")
            return embedding_files
        
        print(f"Found {len(parquet_files)} embedding files")
        
        for file_path in parquet_files:
            try:
                df = pd.read_parquet(file_path)
                
                # Validate that the file has the expected columns
                if 'embedding' not in df.columns:
                    print(f"Warning: {file_path.name} doesn't have 'embedding' column, skipping")
                    continue
                
                # Filter out rows with null embeddings
                valid_embeddings = df[df['embedding'].notna()]
                if len(valid_embeddings) == 0:
                    print(f"Warning: {file_path.name} has no valid embeddings, skipping")
                    continue
                
                print(f"Loaded {file_path.name}: {len(valid_embeddings)} papers with embeddings")
                embedding_files.append((file_path.stem, valid_embeddings))
                
            except Exception as e:
                print(f"Error loading {file_path.name}: {e}")
        
        return embedding_files
    
    def prepare_embeddings_matrix(self, embedding_files: List[Tuple[str, pd.DataFrame]]) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Combine all embeddings into a single matrix and create metadata dataframe.
        
        Args:
            embedding_files: List of (filename, dataframe) tuples
            
        Returns:
            tuple: (embeddings_matrix, metadata_dataframe)
        """
        all_embeddings = []
        all_metadata = []
        
        for filename, df in embedding_files:
            # Extract ego_aid from filename (assuming format: embeddings_A1234567890.parquet)
            ego_aid = filename.replace('embeddings_', '') if filename.startswith('embeddings_') else filename
            
            for idx, row in df.iterrows():
                if row['embedding'] is not None:
                    all_embeddings.append(row['embedding'])
                    
                    metadata = {
                        'ego_aid': ego_aid,
                        'paper_id': row.get('paper_id', ''),
                        'title': row.get('title', ''),
                        'doi': row.get('doi', ''),
                        'original_file': filename
                    }
                    all_metadata.append(metadata)
        
        if not all_embeddings:
            raise ValueError("No valid embeddings found across all files!")
        
        # Convert to numpy array
        embeddings_matrix = np.vstack(all_embeddings)
        metadata_df = pd.DataFrame(all_metadata)
        
        print(f"Combined embeddings matrix shape: {embeddings_matrix.shape}")
        print(f"Metadata dataframe shape: {metadata_df.shape}")
        
        return embeddings_matrix, metadata_df
    
    def compute_umap(self, embeddings_matrix: np.ndarray) -> Tuple[umap.UMAP, np.ndarray]:
        """
        Compute UMAP dimensionality reduction.
        
        Args:
            embeddings_matrix: Input embeddings matrix
            
        Returns:
            tuple: (fitted_umap_model, umap_embeddings)
        """
        print(f"Computing UMAP with {self.n_components} components...")
        print(f"Parameters: n_neighbors={self.n_neighbors}, min_dist={self.min_dist}, metric={self.metric}")
        
        umap_model = umap.UMAP(
            n_components=self.n_components,
            n_neighbors=self.n_neighbors,
            min_dist=self.min_dist,
            metric=self.metric,
            random_state=self.random_state,
            verbose=self.verbose
        )
        
        umap_embeddings = umap_model.fit_transform(embeddings_matrix)
        
        print(f"UMAP computation complete. Output shape: {umap_embeddings.shape}")
        
        return umap_model, umap_embeddings
    
    def save_results(self, umap_embeddings: np.ndarray, metadata_df: pd.DataFrame, 
                    umap_model: umap.UMAP, suffix: str = ""):
        """
        Save UMAP results to files.
        
        Args:
            umap_embeddings: UMAP transformed embeddings
            metadata_df: Metadata dataframe
            umap_model: Fitted UMAP model
            suffix: Optional suffix for output files
        """
        base_name = f"{self.output_name}{suffix}" if suffix else self.output_name
        
        # Create results dataframe
        results_df = metadata_df.copy()
        
        # Add UMAP coordinates
        for i in range(self.n_components):
            results_df[f'umap_{i+1}'] = umap_embeddings[:, i]
        
        # Save results as parquet
        results_file = self.output_dir / f"{base_name}.parquet"
        results_df.to_parquet(results_file, index=False)
        print(f"Saved UMAP results to {results_file}")
        
        # Save UMAP model for future use
        model_file = self.output_dir / f"{base_name}_model.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump(umap_model, f)
        print(f"Saved UMAP model to {model_file}")
        
        # Save summary statistics
        summary_file = self.output_dir / f"{base_name}_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"UMAP Results Summary\n")
            f.write(f"====================\n\n")
            f.write(f"Total papers processed: {len(results_df)}\n")
            f.write(f"Unique ego_aids: {results_df['ego_aid'].nunique()}\n")
            f.write(f"UMAP dimensions: {self.n_components}\n")
            f.write(f"UMAP parameters:\n")
            f.write(f"  - n_neighbors: {self.n_neighbors}\n")
            f.write(f"  - min_dist: {self.min_dist}\n")
            f.write(f"  - metric: {self.metric}\n")
            f.write(f"  - random_state: {self.random_state}\n\n")
            
            # Ego_aid distribution
            f.write(f"Papers per ego_aid:\n")
            ego_counts = results_df['ego_aid'].value_counts()
            for ego_aid, count in ego_counts.items():
                f.write(f"  {ego_aid}: {count} papers\n")
        
        print(f"Saved summary to {summary_file}")
        
        return results_df
    
    def process_individual_files(self):
        """
        Process each embedding file individually (for smaller datasets or comparison).
        """
        embedding_files = self.load_embedding_files()
        
        if not embedding_files:
            print("No embedding files to process!")
            return
        
        for filename, df in embedding_files:
            print(f"\n{'='*60}")
            print(f"Processing individual file: {filename}")
            
            # Prepare embeddings matrix for this file
            embeddings = []
            for idx, row in df.iterrows():
                if row['embedding'] is not None:
                    embeddings.append(row['embedding'])
            
            if len(embeddings) < 2:
                print(f"Skipping {filename}: need at least 2 embeddings for UMAP")
                continue
            
            embeddings_matrix = np.vstack(embeddings)
            
            # Compute UMAP
            umap_model, umap_embeddings = self.compute_umap(embeddings_matrix)
            
            # Prepare metadata (just for this file)
            metadata_df = df[df['embedding'].notna()].copy()
            metadata_df['ego_aid'] = filename.replace('embeddings_', '') if filename.startswith('embeddings_') else filename
            metadata_df['original_file'] = filename
            
            # Save results
            self.save_results(umap_embeddings, metadata_df, umap_model, suffix=f"_{filename}")
    
    def process_all_combined(self):
        """
        Process all embedding files combined into a single UMAP.
        """
        print("="*60)
        print("Processing all embeddings combined")
        print("="*60)
        
        # Load all embedding files
        embedding_files = self.load_embedding_files()
        
        if not embedding_files:
            print("No embedding files to process!")
            return
        
        # Combine all embeddings
        embeddings_matrix, metadata_df = self.prepare_embeddings_matrix(embedding_files)
        
        # Compute UMAP
        umap_model, umap_embeddings = self.compute_umap(embeddings_matrix)
        
        # Save results
        results_df = self.save_results(umap_embeddings, metadata_df, umap_model)
        
        return results_df

def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Process paper embeddings and compute UMAP dimensionality reduction",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Input/Output directories
    parser.add_argument(
        "--input-dir", "-i",
        type=str,
        default="data/raw/embeddings",
        help="Directory containing embedding parquet files"
    )
    
    parser.add_argument(
        "--output-dir", "-o", 
        type=str,
        default="data/processed/umap_embeddings",
        help="Directory to save UMAP results"
    )
    
    # UMAP parameters
    parser.add_argument(
        "--n-components", "-d",
        type=int,
        default=2,
        help="Number of UMAP dimensions (2 for visualization, 3+ for analysis)"
    )
    
    parser.add_argument(
        "--n-neighbors", "-n",
        type=int,
        default=15,
        help="UMAP n_neighbors parameter (higher = more global structure)"
    )
    
    parser.add_argument(
        "--min-dist", "-m",
        type=float,
        default=0.1,
        help="UMAP min_dist parameter (lower = tighter clusters)"
    )
    
    parser.add_argument(
        "--random-state", "-r",
        type=int,
        default=42,
        help="Random state for reproducibility"
    )
    
    # Processing options
    parser.add_argument(
        "--individual",
        action="store_true",
        help="Process each embedding file individually (in addition to combined)"
    )
    
    parser.add_argument(
        "--output-name",
        type=str,
        default="umap_results",
        help="Base name for output files"
    )
    
    parser.add_argument(
        "--metric",
        type=str,
        default="euclidean",
        choices=["euclidean", "manhattan", "chebyshev", "minkowski", "cosine", "correlation"],
        help="Distance metric for UMAP"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()

def main():
    """
    Main function to process embeddings and compute UMAP.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Initialize processor with command line arguments
    processor = UMAPProcessor(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        n_components=args.n_components,
        n_neighbors=args.n_neighbors,
        min_dist=args.min_dist,
        random_state=args.random_state,
        metric=args.metric,
        output_name=args.output_name,
        verbose=args.verbose
    )
    
    print("UMAP Embeddings Processor")
    print("="*40)
    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"UMAP parameters: n_components={args.n_components}, n_neighbors={args.n_neighbors}, min_dist={args.min_dist}")
    print(f"Distance metric: {args.metric}")
    print()
    
    # Process all embeddings combined (main processing)
    results_df = processor.process_all_combined()
    
    if results_df is not None:
        print(f"\n✓ Successfully processed {len(results_df)} papers")
        print(f"✓ Output saved to {processor.output_dir}")
        print(f"✓ Unique researchers: {results_df['ego_aid'].nunique()}")
        
        # Show sample results
        if args.verbose:
            print("\nSample UMAP coordinates:")
            sample_df = results_df[['ego_aid', 'title', 'umap_1', 'umap_2']].head()
            for idx, row in sample_df.iterrows():
                coords = [f"{row[f'umap_{i+1}']:.3f}" for i in range(args.n_components)]
                coords_str = "(" + ", ".join(coords) + ")"
                print(f"  {row['ego_aid']}: {coords_str} - {row['title'][:50]}...")
    
    # Process individual files if requested
    if args.individual:
        print(f"\n{'='*60}")
        print("Processing individual files...")
        processor.process_individual_files()

if __name__ == "__main__":
    print("UMAP Embeddings Processor")
    print("Installation requirements:")
    print("pip install pandas numpy umap-learn pyarrow")
    print()
    
    main()