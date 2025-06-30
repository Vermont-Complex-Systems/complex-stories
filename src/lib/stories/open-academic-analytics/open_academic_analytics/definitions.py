"""
Updated definitions.py with centralized configuration
"""
from dagster import Definitions, load_assets_from_modules, EnvVar
from dagster_duckdb import DuckDBResource
from pathlib import Path

# Import configuration
from config import PipelineConfig, EnvironmentConfig

# Import all your asset modules
from open_academic_analytics import (
    timeline_paper_assets, 
    paper_preprocessing_assets, 
    timeline_coauthor_assets, 
    author_preprocessing_assets, 
    coauthor_preprocessing_assets
)

# Ensure database directory exists
database_path = EnvironmentConfig.get_database_path()
Path(database_path).parent.mkdir(parents=True, exist_ok=True)

# Load all assets from modules
all_assets = load_assets_from_modules([
    timeline_paper_assets, 
    paper_preprocessing_assets, 
    timeline_coauthor_assets, 
    author_preprocessing_assets, 
    coauthor_preprocessing_assets
])

# Define everything with configuration
defs = Definitions(
    assets=all_assets,
    resources={
        "duckdb": DuckDBResource(
            database=EnvVar("DATABASE_PATH").get_value(database_path)
        ),
        "config": PipelineConfig(
            # Override config based on environment
            **{
                "pyalex_email": EnvVar("PYALEX_EMAIL").get_value("your-email@example.com"),
                "s2orc_token": EnvVar("S2ORC_TOKEN").get_value(""),
                "base_dir": EnvVar("PROJECT_BASE_DIR").get_value("."),
                # Environment-specific overrides
                "development_mode": not EnvironmentConfig.is_production(),
                "enable_debug": not EnvironmentConfig.is_production(),
                "max_researchers": 1 if EnvironmentConfig.is_development() else None,
                "force_update": EnvironmentConfig.is_development(),
            }
        )
    }
)