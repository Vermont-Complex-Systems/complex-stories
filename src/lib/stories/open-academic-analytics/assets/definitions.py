"""
definitions.py

Bring together all pipeline stages for academic collaboration analysis.
"""
from dagster import Definitions, load_assets_from_modules
from dagster_duckdb import DuckDBResource
from pathlib import Path

from assets.collect import uvm_profs_2023, academic_publications, coauthor_cache, embeddings
from assets.network import collaboration_network
from assets.export import  paper, author, coauthor
from assets.prepare import  split_training
from assets.fit import  change_point_bayesian, umap_embeddings

# Load all assets from the three pipeline stages
all_assets = load_assets_from_modules([
    uvm_profs_2023,      # Stage 1: Collect raw academic data
    academic_publications,
    embeddings,
    coauthor_cache,    
    collaboration_network, # Stage 2: Analyze collaboration patterns  
    paper,      # Stage 3: Prepare for dashboards
    author,
    coauthor,
    split_training,
    change_point_bayesian,
    umap_embeddings
])

defs = Definitions(
    assets=all_assets,
    resources={
        "duckdb": DuckDBResource(database=":memory:")
    }
)