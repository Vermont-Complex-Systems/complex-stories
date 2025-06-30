"""
config.py

Centralized configuration for the academic analytics pipeline.
All hardcoded values and environment-specific settings go here.
"""

import os
from pathlib import Path
from dagster import Config
from typing import List, Dict, Optional

# Load environment variables from .env file
from dotenv import load_dotenv

# Load .env file if it exists
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded environment variables from {env_path}")
else:
    print("ℹ️  No .env file found, using environment variables only")


class PipelineConfig(Config):
    """Main configuration class for the academic analytics pipeline"""
    
    # ========================================
    # DIRECTORY PATHS
    # ========================================
    base_dir: str = "."
    data_raw_dir: str = "data/raw"
    data_processed_dir: str = "../../../../static/data/open-academic-analytics"  # static
    
    @property
    def data_raw_path(self) -> Path:
        return Path(self.base_dir) / self.data_raw_dir
    
    @property
    def data_processed_path(self) -> Path:
        return Path(self.base_dir) / self.data_processed_dir
    
    @property
    def database_path(self) -> str:
        return str(self.data_raw_path / "oa_data_raw.db")
    
    # ========================================
    # DEVELOPMENT & PROCESSING SETTINGS
    # ========================================
    
    # Development mode settings
    development_mode: bool = True
    max_researchers: int = 1
    target_researcher: Optional[str] = "A5008985646"  # Updated from your .env
    force_update: bool = False
    enable_debug: bool = True
    
    # Processing settings
    progress_report_interval: int = 10
    batch_size: int = 1000
    min_valid_year: int = 1950
    max_valid_year: int = 2024
    
    # ========================================
    # API CONFIGURATION
    # ========================================
    
    # OpenAlex API settings - FIXED: Use os.getenv() instead of env_path
    pyalex_email: str = os.getenv("PYALEX_EMAIL", "jonathanstonge7@gmail.com")
    api_rate_limit: float = 10.0
    max_api_retries: int = 3
    api_timeout: float = 30.0
    
    # Semantic Scholar API settings  
    s2orc_token: str = os.getenv("S2ORC_TOKEN", "")
    s2_batch_size: int = 500
    s2_rate_limit: float = 1.0
    
    # ========================================
    # DATA FILTERING CONFIGURATION
    # ========================================
    
    # Paper filtering
    accepted_work_types: List[str] = [
        'article', 
        'preprint', 
        'book-chapter', 
        'book', 
        'report'
    ]
    
    filter_title_patterns: List[str] = [
        "^Table", 
        "Appendix", 
        "Issue Cover", 
        "This Week in Science",
        "^Figure ", 
        "^Data for ", 
        "^Author Correction: ", 
        "supporting information",
        "^supplementary material", 
        "^list of contributors"
    ]
    
    filter_doi_patterns: List[str] = [
        "supplement", 
        "zenodo"
    ]
    
    # ========================================
    # AGE STANDARDIZATION SETTINGS
    # ========================================
    age_std_prefix: str = "1"
    age_padding_width: int = 3
    month_range: List[int] = [1, 12]  # FIXED: Changed from tuple to List[int]
    day_range: List[int] = [1, 28]    # FIXED: Changed from tuple to List[int]
    
    # ========================================
    # COLLABORATION ANALYSIS SETTINGS
    # ========================================
    collab_types: Dict[str, str] = {
        'NEW': 'new_collab',
        'NEW_THROUGH_MUTUAL': 'new_collab_of_collab', 
        'EXISTING': 'existing_collab'
    }
    
    age_buckets: Dict[str, List[float]] = {  # FIXED: Changed tuple to List[float]
        'much_younger': [float('-inf'), -15],
        'younger': [-15, -7],
        'same_age': [-7, 7],
        'older': [7, 15],
        'much_older': [15, float('inf')]
    }
    
    # ========================================
    # FILE NAMES
    # ========================================
    researchers_input_file: str = "uvm_profs_2023.parquet"
    researchers_tsv_file: str = "researchers.tsv"
    paper_output_file: str = "paper.parquet"
    author_output_file: str = "author.parquet"
    coauthor_output_file: str = "coauthor.parquet"
    
    # ========================================
    # VALIDATION SETTINGS
    # ========================================
    required_paper_columns: List[str] = ['ego_aid', 'title', 'pub_year', 'authors']
    required_author_columns: List[str] = ['aid', 'author_age']
    required_coauthor_columns: List[str] = [
        'aid', 'name', 'author_age', 'coauth_age', 'age_diff', 'pub_date'
    ]
    
    # Data quality thresholds
    max_coauthors_per_paper: int = 100
    min_author_age: int = 0
    max_author_age: int = 70
    max_suspicious_collabs_per_year: int = 50


class EnvironmentConfig:
    """Environment-specific configuration that doesn't need to be in Dagster Config"""
    
    @staticmethod
    def get_env() -> str:
        """Get current environment (dev, staging, prod)"""
        return os.getenv("DAGSTER_ENV", "dev")
    
    @staticmethod
    def is_development() -> bool:
        """Check if running in development mode"""
        return EnvironmentConfig.get_env() == "dev"
    
    @staticmethod
    def is_production() -> bool:
        """Check if running in production mode"""
        return EnvironmentConfig.get_env() == "prod"
    
    @staticmethod
    def get_database_path() -> str:
        """Get database path based on environment"""
        env = EnvironmentConfig.get_env()
        if env == "test":
            return "data/test/oa_data_test.db"
        elif env == "prod":
            return os.getenv("PROD_DATABASE_PATH", "data/prod/oa_data_prod.db")
        else:
            return os.getenv("DATABASE_PATH", "data/raw/oa_data_raw.db")  # FIXED: Use .env value
    
    @staticmethod
    def get_log_level() -> str:
        """Get logging level based on environment"""
        return os.getenv("LOG_LEVEL", "DEBUG")  # FIXED: Use .env value


# Helper functions for common config access patterns
def get_dev_config() -> dict:
    """Get development-specific configuration overrides"""
    return {
        "development_mode": True,
        "max_researchers": int(os.getenv("MAX_RESEARCHERS", "1")),  # FIXED: Use .env value
        "target_researcher": os.getenv("TARGET_RESEARCHER", "A5008985646"),  # FIXED: Use .env value
        "force_update": os.getenv("FORCE_UPDATE", "false").lower() == "true",  # FIXED: Use .env value
        "enable_debug": True
    }

def get_prod_config() -> dict:
    """Get production-specific configuration overrides"""
    return {
        "development_mode": False,
        "max_researchers": None,  # Process all researchers
        "target_researcher": None,
        "force_update": False,
        "enable_debug": False,
        "progress_report_interval": 50  # Less frequent logging in prod
    }

def get_config_for_env(env: str = None) -> dict:
    """Get configuration based on environment"""
    if env is None:
        env = EnvironmentConfig.get_env()
    
    if env == "prod":
        return get_prod_config()
    else:
        return get_dev_config()


# Constants that can be imported directly
DEFAULT_CONFIG = PipelineConfig()

# Quick access to common paths
DATA_RAW = DEFAULT_CONFIG.data_raw_path
DATA_PROCESSED = DEFAULT_CONFIG.data_processed_path
DATABASE_PATH = DEFAULT_CONFIG.database_path

# Quick access to common settings
DEV_CONFIG = get_dev_config()
PROD_CONFIG = get_prod_config()

# Print loaded configuration for debugging
if __name__ == "__main__":
    print("🔧 Configuration loaded:")
    print(f"  Email: {DEFAULT_CONFIG.pyalex_email}")
    print(f"  Environment: {EnvironmentConfig.get_env()}")
    print(f"  Development mode: {EnvironmentConfig.is_development()}")
    print(f"  Target researcher: {DEV_CONFIG.get('target_researcher')}")
    print(f"  Database path: {EnvironmentConfig.get_database_path()}")