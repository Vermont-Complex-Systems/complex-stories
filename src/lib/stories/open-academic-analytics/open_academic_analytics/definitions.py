"""
definitions.py

Bring together all pipeline stages for academic collaboration analysis
"""
from dagster import Definitions, load_assets_from_modules
from dagster_duckdb import DuckDBResource
from pathlib import Path

from open_academic_analytics import data_collection, research_analysis, visualization_prep
from config import get_database_path

# Ensure database directory exists
database_path = get_database_path()
Path(database_path).parent.mkdir(parents=True, exist_ok=True)

# Load all assets from the three pipeline stages
all_assets = load_assets_from_modules([
    data_collection,      # Stage 1: Collect raw academic data
    research_analysis,    # Stage 2: Analyze collaboration patterns  
    visualization_prep    # Stage 3: Prepare for dashboards
])

# Simple, focused definitions
defs = Definitions(
    assets=all_assets,
    resources={
        "duckdb": DuckDBResource(database=database_path)
    }
)