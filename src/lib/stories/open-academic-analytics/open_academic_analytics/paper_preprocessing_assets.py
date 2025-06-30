"""
paper_preprocessing_assets.py

Fixed to use config for both input and output paths consistently.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import dagster as dg
from dagster_duckdb import DuckDBResource

# Import configuration and database adapter
from config import PipelineConfig
from modules.database_adapter import DatabaseExporterAdapter


def filter_mislabeled_articles(df, config: PipelineConfig):
    """Remove mislabeled articles - same logic as before"""
    print("Filtering out mislabeled articles...")
    initial_count = len(df)
    
    for pattern in config.filter_title_patterns:
        before_count = len(df)
        df = df[~df.title.str.contains(pattern, case=False, na=False)]
        filtered = before_count - len(df)
        if filtered > 0:
            print(f"  - Filtered {filtered} papers matching title pattern '{pattern}'")
    
    for pattern in config.filter_doi_patterns:
        before_count = len(df)
        df = df[~df.doi.str.contains(pattern, case=False, na=False)]
        filtered = before_count - len(df)
        if filtered > 0:
            print(f"  - Filtered {filtered} papers with DOI containing '{pattern}'")
    
    total_filtered = initial_count - len(df)
    print(f"  - Total mislabeled articles removed: {total_filtered}")
    
    return df


def calculate_coauthor_counts(df):
    """Calculate coauthor counts - same logic as before"""
    print("Computing number of coauthors...")
    df['nb_coauthors'] = df.authors.apply(
        lambda x: len(x.split(", ")) if isinstance(x, str) else 0
    )
    return df


@dg.asset(deps=["timeline_paper_main"])
def paper_preprocessing(duckdb: DuckDBResource, config: PipelineConfig):
    """
    Paper preprocessing with consistent config-based paths
    
    Key fix: Uses config for output path to match where other assets expect it
    """
    
    print("🚀 Starting paper preprocessing...")
    
    # Ensure output directory exists
    config.data_processed_path.mkdir(parents=True, exist_ok=True)
    
    with duckdb.get_connection() as conn:
        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database via DuckDB resource")
        
        # Query database (same as before)
        print("Querying database for papers with author metadata...")
        query = """
            SELECT p.ego_aid, a.display_name as name, p.pub_date, p.pub_year, p.title,
                   p.cited_by_count, p.doi, p.wid, p.authors, p.work_type, 
                   a.author_age as ego_age
            FROM paper p
            LEFT JOIN author a ON p.ego_aid = a.aid AND p.pub_year = a.pub_year
        """
        
        df = db_exporter.con.sql(query).fetchdf()
        print(f"Retrieved {len(df)} papers from database")

        # Same processing steps as before
        print("Filtering papers without titles...")
        df = df[~df.title.isna()]
        print(f"After removing papers without titles: {len(df)} papers")

        print("Deduplicating papers...")
        df = df.sort_values("pub_date", ascending=False).reset_index(drop=True)
        df['title'] = df.title.str.lower()
        df = df[~df[['ego_aid', 'title']].duplicated()]
        print(f"After deduplication: {len(df)} papers")

        print("Filtering by work types...")
        print(f"Accepted work types: {config.accepted_work_types}")
        df = df[df.work_type.isin(config.accepted_work_types)]
        print(f"After filtering by work type: {len(df)} papers")

        df = filter_mislabeled_articles(df, config)
        df = calculate_coauthor_counts(df)
        
        # 🎯 KEY FIX: Use config for output path
        output_path = config.data_processed_path / config.paper_output_file
        print(f"Saving {len(df)} processed papers to {output_path}")
        df.to_parquet(output_path)
        print("Paper preprocessing completed successfully!")
        
        print("\n=== Processing Summary ===")
        print(f"Final paper count: {len(df):,}")
        print(f"Unique authors: {df.ego_aid.nunique():,}")
        print(f"Year range: {df.pub_year.min()}-{df.pub_year.max()}")
        print(f"Work types: {df.work_type.value_counts().to_dict()}")
        print(f"Average coauthors per paper: {df.nb_coauthors.mean():.1f}")
        
        print("🔐 Database connection closed automatically by DuckDB resource")
        
        return f"Processed {len(df)} papers, saved to {output_path}"


defs = dg.Definitions(
    assets=[
        paper_preprocessing
    ]
)