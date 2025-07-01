"""
Simple definitions.py - everything in one place
"""
from dagster import Definitions, load_assets_from_modules
from dagster_duckdb import DuckDBResource
from config import config

# Import all your asset modules
from open_academic_analytics import (
    timeline_paper_assets, 
    paper_preprocessing_assets, 
    timeline_coauthor_assets, 
    author_preprocessing_assets, 
    coauthor_preprocessing_assets
)

# Load all assets
all_assets = load_assets_from_modules([
    timeline_paper_assets, 
    paper_preprocessing_assets, 
    timeline_coauthor_assets, 
    author_preprocessing_assets, 
    coauthor_preprocessing_assets
])

# Simple definitions
defs = Definitions(
    assets=all_assets,
    resources={
        "duckdb": DuckDBResource(database=str(config.DATABASE_PATH))
    }
)