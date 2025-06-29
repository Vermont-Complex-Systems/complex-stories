"""
paper_preprocessing_assets.py

UPDATED to use Dagster's official DuckDB resource with adapter.
All business logic remains identical - only the database connection changed.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import dagster as dg
from dagster_duckdb import DuckDBResource

# Import the database adapter
from modules.database_adapter import DatabaseExporterAdapter

# Configuration - matching original paths
DATA_RAW = Path("data/raw")
DATA_PROCESSED = Path("data/processed")

# Ensure directories exist
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

# Paper filtering configuration (exact same as original)
ACCEPTED_WORK_TYPES = [
    'article', 
    'preprint', 
    'book-chapter', 
    'book', 
    'report'
]

# Patterns for filtering mislabeled articles (exact same as original)
FILTER_TITLE_PATTERNS = [
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

# DOI patterns to exclude (exact same as original)
FILTER_DOI_PATTERNS = [
    "supplement", 
    "zenodo"
]

# Output configuration
OUTPUT_FILE = "paper.parquet"


def filter_mislabeled_articles(df):
    """
    Remove papers that are mislabeled as articles but are actually supplements,
    figures, corrections, or other non-research content.
    
    EXACT REPRODUCTION of the original filter_mislabeled_articles function
    
    Args:
        df (pd.DataFrame): DataFrame with paper records
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    print("Filtering out mislabeled articles...")
    initial_count = len(df)
    
    # Filter by title patterns (exact same logic as original)
    for pattern in FILTER_TITLE_PATTERNS:
        before_count = len(df)
        df = df[~df.title.str.contains(pattern, case=False, na=False)]
        filtered = before_count - len(df)
        if filtered > 0:
            print(f"  - Filtered {filtered} papers matching title pattern '{pattern}'")
    
    # Filter by DOI patterns (exact same logic as original)
    for pattern in FILTER_DOI_PATTERNS:
        before_count = len(df)
        df = df[~df.doi.str.contains(pattern, case=False, na=False)]
        filtered = before_count - len(df)
        if filtered > 0:
            print(f"  - Filtered {filtered} papers with DOI containing '{pattern}'")
    
    total_filtered = initial_count - len(df)
    print(f"  - Total mislabeled articles removed: {total_filtered}")
    
    return df


def calculate_coauthor_counts(df):
    """
    Calculate the number of coauthors for each paper.
    
    EXACT REPRODUCTION of the original calculate_coauthor_counts function
    
    Args:
        df (pd.DataFrame): DataFrame with paper records containing 'authors' column
        
    Returns:
        pd.DataFrame: DataFrame with added 'nb_coauthors' column
    """
    print("Computing number of coauthors...")
    df['nb_coauthors'] = df.authors.apply(
        lambda x: len(x.split(", ")) if isinstance(x, str) else 0
    )
    return df


@dg.asset(deps=["timeline_paper_main"])  # String dependency reference
def paper_preprocessing(duckdb: DuckDBResource):  # 🆕 UPDATED: Use DuckDB resource
    """
    UPDATED to use DuckDB resource, but all business logic remains identical
    
    Main preprocessing pipeline:
    1. Load raw paper data from database with author metadata
    2. Remove papers without titles
    3. Deduplicate by title and author ID
    4. Filter by accepted work types
    5. Remove mislabeled articles using title/DOI patterns
    6. Calculate number of coauthors
    7. Export cleaned dataset to parquet format
    """
    
    print("🚀 Starting paper preprocessing...")
    
    # 🆕 NEW: Use DuckDB resource with adapter
    with duckdb.get_connection() as conn:
        # Create adapter to maintain exact same interface
        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database via DuckDB resource")
        
        # === ALL BUSINESS LOGIC BELOW IS IDENTICAL TO ORIGINAL ===

        # Query to get papers with author metadata (exact same as original)
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

        # Step 1: Remove papers without titles (exact same as original)
        print("Filtering papers without titles...")
        df = df[~df.title.isna()]
        print(f"After removing papers without titles: {len(df)} papers")

        # Step 2: Deduplicate papers by title and author ID (exact same as original)
        print("Deduplicating papers...")
        df = df.sort_values("pub_date", ascending=False).reset_index(drop=True)
        df['title'] = df.title.str.lower()
        df = df[~df[['ego_aid', 'title']].duplicated()]
        print(f"After deduplication: {len(df)} papers")

        # Step 3: Filter by accepted work types (exact same as original)
        print("Filtering by work types...")
        print(f"Accepted work types: {ACCEPTED_WORK_TYPES}")
        df = df[df.work_type.isin(ACCEPTED_WORK_TYPES)]
        print(f"After filtering by work type: {len(df)} papers")

        # Step 4: Remove mislabeled articles (exact same function call as original)
        df = filter_mislabeled_articles(df)

        # Step 5: Calculate coauthor counts (exact same function call as original)
        df = calculate_coauthor_counts(df)
        
        # Save processed data (exact same as original)
        output_path = DATA_PROCESSED / OUTPUT_FILE
        print(f"Saving {len(df)} processed papers to {output_path}")
        df.to_parquet(output_path)
        print("Paper preprocessing completed successfully!")
        
        # Print summary statistics (exact same as original)
        print("\n=== Processing Summary ===")
        print(f"Final paper count: {len(df):,}")
        print(f"Unique authors: {df.ego_aid.nunique():,}")
        print(f"Year range: {df.pub_year.min()}-{df.pub_year.max()}")
        print(f"Work types: {df.work_type.value_counts().to_dict()}")
        print(f"Average coauthors per paper: {df.nb_coauthors.mean():.1f}")
        
        # No manual close needed - context manager handles it
        print("🔐 Database connection closed automatically by DuckDB resource")
        
        return f"Processed {len(df)} papers, saved to {output_path}"


# Simple definitions - faithful to original script structure
defs = dg.Definitions(
    assets=[
        paper_preprocessing
    ]
)