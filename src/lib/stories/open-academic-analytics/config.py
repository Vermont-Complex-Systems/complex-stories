"""
Simple configuration for academic analytics pipeline
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Simple configuration - no fancy classes needed
class Config:
    # Paths
    BASE_DIR = Path(".")
    DATA_RAW_DIR = BASE_DIR / "data/raw"
    DATA_PROCESSED_DIR = Path("../../../../static/data/open-academic-analytics")
    DATABASE_PATH = DATA_RAW_DIR / "oa_data_raw.db"
    
    # API settings
    PYALEX_EMAIL = os.getenv("PYALEX_EMAIL", "jonathanstonge7@gmail.com")
    
    # Development settings
    TARGET_RESEARCHER = os.getenv("TARGET_RESEARCHER", "A5010744577")
    MAX_RESEARCHERS = int(os.getenv("MAX_RESEARCHERS", "1"))
    FORCE_UPDATE = os.getenv("FORCE_UPDATE", "false").lower() == "true"
    
    # File names
    RESEARCHERS_INPUT_FILE = "uvm_profs_2023.parquet"
    RESEARCHERS_TSV_FILE = "researchers.tsv"
    PAPER_OUTPUT_FILE = "paper.parquet"
    AUTHOR_OUTPUT_FILE = "author.parquet"
    COAUTHOR_OUTPUT_FILE = "coauthor.parquet"
    
    # Data filtering
    ACCEPTED_WORK_TYPES = ['article', 'preprint', 'book-chapter', 'book', 'report']
    FILTER_TITLE_PATTERNS = [
        "^Table", "Appendix", "Issue Cover", "This Week in Science",
        "^Figure ", "^Data for ", "^Author Correction: ", "supporting information",
        "^supplementary material", "^list of contributors"
    ]
    
    # Age buckets for collaboration analysis
    AGE_BUCKETS = {
        'much_younger': [-float('inf'), -15],
        'younger': [-15, -7],
        'same_age': [-7, 7],
        'older': [7, 15],
        'much_older': [15, float('inf')]
    }
    
    # Collaboration types
    COLLAB_TYPES = {
        'NEW': 'new_collab',
        'NEW_THROUGH_MUTUAL': 'new_collab_of_collab', 
        'EXISTING': 'existing_collab'
    }

# Create global config instance
config = Config()

# Ensure directories exist
config.DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
config.DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)