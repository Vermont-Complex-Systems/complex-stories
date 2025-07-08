"""
definitions.py

Bring together all pipeline stages for academic collaboration analysis.
"""
from dagster import Definitions, load_assets_from_modules
from dagster_duckdb import DuckDBResource
from pathlib import Path

from assets.collect import researcher_list, academic_publications, coauthor_cache
from assets.network import collaboration_network
from assets.export import  paper, author, coauthor

# Load all assets from the three pipeline stages
all_assets = load_assets_from_modules([
    researcher_list,      # Stage 1: Collect raw academic data
    academic_publications,
    coauthor_cache,    
    collaboration_network, # Stage 2: Analyze collaboration patterns  
    paper,      # Stage 3: Prepare for dashboards
    author,
    coauthor
])

defs = Definitions(
    assets=all_assets,
    resources={
        "duckdb": DuckDBResource(database=":memory:")
    }
)