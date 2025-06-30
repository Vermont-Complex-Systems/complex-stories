"""
Configuration module for the coauthorship analysis pipeline
Centralizes all configurable parameters and paths
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(os.getenv('PROJECT_DIR', '.'))
DATA_DIR = BASE_DIR / 'data'
SCRIPT_DIR = BASE_DIR / 'scripts'

# Data subdirectories
DATA_RAW = DATA_DIR / 'raw'
DATA_PREPROCESSED = DATA_DIR / 'preprocessed'
DATA_CLEAN = DATA_DIR / 'clean'
DATA_TRAINING = DATA_DIR / 'training'

# Web framework directories
FRAMEWORK_DIR = BASE_DIR / 'web'
DATA_OBS = FRAMEWORK_DIR / 'data'

# Model directories
MODEL_DIR = SCRIPT_DIR / 'models'
STAN_MODEL_DIR = MODEL_DIR / 'stan'

# Default input files
DEFAULT_RESEARCHERS_PARQUET = DATA_RAW / 'uvm_profs_2023.parquet'
DEFAULT_RESEARCHERS_TSV = DATA_RAW / 'researchers.tsv'

# Database files
DATABASE_FILE = DATA_RAW / 'oa_data_raw.db'

# Output files
PAPER_PARQUET = DATA_OBS / 'paper.parquet'
AUTHOR_PARQUET = DATA_OBS / 'author.parquet'
COAUTHOR_PARQUET = DATA_OBS / 'coauthor.parquet'
TRAINING_DATA_PARQUET = DATA_OBS / 'training_data.parquet'

# Processing parameters
ACCEPTED_WORK_TYPES = ['article', 'preprint', 'book-chapter', 'book', 'report']
MIN_PUBLICATIONS_PER_AUTHOR = 5
MAX_COAUTHORS_PER_PAPER = 100  # For filtering outliers
MIN_AUTHOR_AGE = 0
MAX_AUTHOR_AGE = 70

# API settings
PYALEX_EMAIL = os.getenv('PYALEX_EMAIL', 'example@example.com')
API_RATE_LIMIT = 10  # requests per second