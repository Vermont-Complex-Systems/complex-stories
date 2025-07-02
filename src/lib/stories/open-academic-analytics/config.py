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
    data_processed_dir: str = "../../../../static/data/open-academic-analytics"
    
    @property
    def data_raw_path(self) -> Path:
        return Path(self.base_dir) / self.data_raw_dir
    
    @property
    def data_processed_path(self) -> Path:
        return Path(self.base_dir) / self.data_processed_dir
    
    @property
    def database_path(self) -> str:
        return str(self.data_raw_path / "oa_data_raw.db")
    
    # Backward compatibility properties for assets that expect uppercase names
    @property
    def DATA_RAW_DIR(self) -> Path:
        return self.data_raw_path
    
    @property
    def DATA_PROCESSED_DIR(self) -> Path:
        return self.data_processed_path
    
    @property
    def RESEARCHERS_INPUT_FILE(self) -> str:
        return self.researchers_input_file
    
    @property
    def RESEARCHERS_TSV_FILE(self) -> str:
        return self.researchers_tsv_file
    
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
    def MAX_RESEARCHERS(self) -> Optional[int]:
        return self.max_researchers
    
    @property
    def FORCE_UPDATE(self) -> bool:
        return self.force_update
    
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
    
    # Development settings (reading from .env)
    development_mode: bool = True
    max_researchers: Optional[int] = int(os.getenv("MAX_RESEARCHERS", "1")) if os.getenv("MAX_RESEARCHERS") else None
    target_researcher: Optional[str] = os.getenv("TARGET_RESEARCHER")
    force_update: bool = os.getenv("FORCE_UPDATE", "false").lower() == "true"
    enable_debug: bool = True
    progress_report_interval: int = 10
    
    # API settings
    pyalex_email: str = os.getenv("PYALEX_EMAIL", "jonathanstonge7@gmail.com")
    
    # Data settings
    min_valid_year: int = 1950
    max_valid_year: int = 2024
    
    # File names
    researchers_input_file: str = "uvm_profs_2023.parquet"
    researchers_tsv_file: str = "researchers.tsv"
    paper_output_file: str = "paper.parquet"
    author_output_file: str = "author.parquet"
    coauthor_output_file: str = "coauthor.parquet"
    
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


# Simple helper for database path
def get_database_path() -> str:
    return os.getenv("DATABASE_PATH", "data/raw/oa_data_raw.db")

# Create default config instance (this is what your assets import)
DEFAULT_CONFIG = PipelineConfig()

# For backward compatibility with existing imports
config = DEFAULT_CONFIG