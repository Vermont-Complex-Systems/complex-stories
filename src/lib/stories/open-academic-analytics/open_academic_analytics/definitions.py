"""
Updated definitions.py with DuckDB resource defined inline
"""
from dagster import Definitions, load_assets_from_modules
from dagster_duckdb import DuckDBResource
from pathlib import Path

# Import all your asset modules
from open_academic_analytics import (
    timeline_paper_assets, 
    paper_preprocessing_assets, 
    timeline_coauthor_assets, 
    author_preprocessing_assets, 
    coauthor_preprocessing_assets
)

# Ensure database directory exists
DATABASE_PATH = "data/raw/oa_data_raw.db"
Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)

# Load all assets from modules
all_assets = load_assets_from_modules([
    timeline_paper_assets, 
    paper_preprocessing_assets, 
    timeline_coauthor_assets, 
    author_preprocessing_assets, 
    coauthor_preprocessing_assets
])

# Define everything in one place
defs = Definitions(
    assets=all_assets,
    resources={
        "duckdb": DuckDBResource(database=DATABASE_PATH),
    }
)