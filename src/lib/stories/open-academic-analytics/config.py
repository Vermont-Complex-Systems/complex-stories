"""
Simplified config.py - keeping exact same interface but removing unused complexity
"""
import os
from pathlib import Path
from dagster import Config
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class PipelineConfig(Config):
    """Main configuration class - same interface as before"""
    
    # Paths
    base_dir: str = "."
    data_raw_dir: str = "data/raw"
    embedding_dir: str = "data/raw/embeddings"
    data_clean_dir: str = "data/clean"
    data_processed_dir: str = "data/processed"
    data_export_dir: str = "../../../../static/data/open-academic-analytics"
    
    stan_model_dir: Path = "assets/fit/stan"
    
    @property
    def data_raw_path(self) -> Path:
        return Path(self.base_dir) / self.data_raw_dir
    
    @property
    def embeddings_path(self) -> Path:
        return Path(self.base_dir) / self.embedding_dir
    
    @property
    def data_clean_path(self) -> Path:
        return Path(self.base_dir) / self.data_clean_dir
    
    @property
    def data_processed_path(self) -> Path:
        return Path(self.base_dir) / self.data_processed_dir
    
    @property
    def data_export_path(self) -> Path:
        return Path(self.base_dir) / self.data_export_dir
    
    @property
    def data_processed_path(self) -> Path:
        return Path(self.base_dir) / self.data_processed_dir
    
    # Backward compatibility properties for assets that expect uppercase names
    @property
    def DATA_RAW_DIR(self) -> Path:
        return self.data_raw_path
    
    @property
    def DATA_PROCESSED_DIR(self) -> Path:
        return self.data_processed_path
    
    @property
    def TRAINING_DATA_OUTPUT_FILE(self) -> str:
        return self.training_data_file
    
    @property
    def PAPER_OUTPUT_FILE(self) -> str:
        return self.paper_output_file
    
    @property
    def AUTHOR_OUTPUT_FILE(self) -> str:
        return self.author_output_file
    
    @property
    def COAUTHOR_OUTPUT_FILE(self) -> str:
        return self.coauthor_output_file
    
    @property
    def TARGET_RESEARCHER(self) -> Optional[str]:
        return self.target_researcher
    
    @property
    def FORCE_UPDATE(self) -> bool:
        return self.force_update
    
    @property
    def RETRY_FAILED_DOIS(self) -> bool:
        return self.retry_failed_dois
    
    @property
    def ACCEPTED_WORK_TYPES(self) -> List[str]:
        return self.accepted_work_types
    
    @property
    def FILTER_TITLE_PATTERNS(self) -> List[str]:
        return self.filter_title_patterns
    
    @property
    def COLLAB_TYPES(self) -> Dict[str, str]:
        return self.collab_types
    
    @property
    def AGE_BUCKETS(self) -> Dict[str, List[float]]:
        return self.age_buckets
    
    @property
    def UMAP_CONFIG(self) -> Dict[str, float]:
        return self.umap_config
    
    # Development settings
    target_researcher: Optional[str] = None
    force_update: bool = False
    update_age: bool = False
    enable_debug: bool = True
    progress_report_interval: int = 10
    retry_failed_dois: bool = False

    # API settings
    pyalex_email: str = os.getenv("PYALEX_EMAIL", "jonathanstonge7@gmail.com")
    
    # Data settings
    min_valid_year: int = 1950
    max_valid_year: int = 2024
    
    # File names
    uvm_profs_2023_file: str = "uvm_profs_2023.parquet"
    departments_file: str = "uvm_departments.parquet"
    embeddings_file: str = 'embeddings.parquet'
    
    paper_output_file: str = "paper.parquet"
    author_output_file: str = "author.parquet"
    coauthor_output_file: str = "coauthor.parquet"
    training_data_file: str = 'training_data.parquet'
    
    # Data filtering
    accepted_work_types: List[str] = ['article', 'preprint', 'book-chapter', 'book', 'report']
    filter_title_patterns: List[str] = [
        "^Table", "Appendix", "Issue Cover", "This Week in Science",
        "^Figure ", "^Data for ", "^Author Correction: ", "supporting information",
        "^supplementary material", "^list of contributors"
    ]
    filter_doi_patterns: List[str] = ["supplement", "zenodo"]
    
    # Age standardization
    age_std_prefix: str = "1"
    age_padding_width: int = 3
    month_range: List[int] = [1, 12]
    day_range: List[int] = [1, 28]
    
    # Collaboration analysis
    collab_types: Dict[str, str] = {
        'NEW': 'new_collab',
        'NEW_THROUGH_MUTUAL': 'new_collab_of_collab', 
        'EXISTING': 'existing_collab'
    }
    
    age_buckets: Dict[str, List[float]] = {
        'much_younger': [float('-inf'), -15],
        'younger': [-15, -7],
        'same_age': [-7, 7],
        'older': [7, 15],
        'much_older': [15, float('inf')]
    }
    
    # Validation columns (keeping what's actually used)
    required_author_columns: List[str] = ['aid', 'author_age']
    required_coauthor_columns: List[str] = ['aid', 'name', 'author_age', 'coauth_age', 'age_diff', 'pub_date']

    # umap config
    umap_config:  Dict[str, float]  = {
        'n_components': 2,
        'n_neighbors': 15,
        'min_dist': 0.1,
        'random_state': 42,
        'individual': True,
        'metric': 'euclidean' #["euclidean", "manhattan", "chebyshev", "minkowski", "cosine", "correlation"],
    }

# Create default config instance (this is what your assets import)
DEFAULT_CONFIG = PipelineConfig()

# For backward compatibility with existing imports
config = DEFAULT_CONFIG