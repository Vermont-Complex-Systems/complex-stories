"""
coauthor_preprocessing_assets.py

UPDATED to use Dagster's official DuckDB resource with adapter.
All business logic remains identical - only the database connection changed.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import calendar
import random
import numpy as np
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

# Database configuration (exact same as original)
OUTPUT_FILE = "coauthor.parquet"

# Age bucket configuration (exact same as original)
AGE_BUCKETS = {
    'much_younger': (-float('inf'), -15),
    'younger': (-15, -7),
    'same_age': (-7, 7),
    'older': (7, 15),
    'much_older': (15, float('inf'))
}

# Data validation settings (exact same as original)
MIN_VALID_YEAR = 1950
MAX_VALID_YEAR = 2024

# Age standardization settings (exact same as original)
AGE_STD_PREFIX = "1"
AGE_PADDING_WIDTH = 3

# Required columns for validation (exact same as original)
REQUIRED_COLUMNS = [
    'aid', 'name', 'author_age', 'coauth_age', 
    'age_diff', 'pub_date'
]

# Age Difference Categorization (exact same as original):
# much_younger: < -15 years (significantly junior)
# younger:      -15 to -7 years (junior)  
# same_age:     -7 to +7 years (peer)
# older:        +7 to +15 years (senior)
# much_older:   > +15 years (significantly senior)
#
# Note: Negative values mean coauthor is younger than ego

# Core SQL Query Structure (exact same as original):
# SELECT: coauthor metadata + ego author data + coauthor author data
# FROM: coauthor2 table (collaboration records)
# LEFT JOIN: author table (twice - for ego and coauthor data)
# WHERE: Filter to recent years (< 2024)
# 
# Key Fields Retrieved:
# - Collaboration metadata: pub_year, yearly_collabo, acquaintance
# - Ego data: aid, name, institution, author_age, career span
# - Coauthor data: aid, name, age, first_pub_year
# - Derived: age_diff = coauth_age - ego_age


def load_coauthor_data(db_exporter):
    """
    Load coauthor relationship data with author metadata via complex SQL join.
    EXACT REPRODUCTION of original load_coauthor_data function
    
    Args:
        db_exporter: DatabaseExporterAdapter instance with active connection
        
    Returns:
        pd.DataFrame: Coauthor relationships with metadata
    """
    print("Querying coauthor data with author metadata...")
    
    # Complex SQL join query (exact same as original)
    query = """
        SELECT 
            c.pub_year, c.pub_date::CHAR as pub_date,
            ego_a.aid, ego_a.institution, ego_a.display_name as name, 
            ego_a.author_age, ego_a.first_pub_year, ego_a.last_pub_year,
            c.yearly_collabo, c.all_times_collabo, c.acquaintance, c.shared_institutions,
            coauth.aid as coauth_aid, coauth.display_name as coauth_name, 
            coauth.author_age as coauth_age, coauth.first_pub_year as coauth_min_year,
            (coauth.author_age-ego_a.author_age) AS age_diff
        FROM 
            coauthor2 c
        LEFT JOIN 
            author coauth ON c.coauthor_aid = coauth.aid AND c.pub_year = coauth.pub_year
        LEFT JOIN 
            author ego_a ON c.ego_aid = ego_a.aid AND c.pub_year = ego_a.pub_year
        WHERE 
            c.pub_year < $1
        ORDER BY c.pub_year
    """
    
    df = db_exporter.con.sql(query, params=[MAX_VALID_YEAR]).fetchdf()
    print(f"Retrieved {len(df):,} coauthor relationships")
    
    return df


def validate_data_quality(df):
    """
    Validate data quality and report missing information.
    EXACT REPRODUCTION of original validate_data_quality function
    
    Args:
        df (pd.DataFrame): Coauthor DataFrame to validate
        
    Returns:
        pd.DataFrame: Validated DataFrame
    """
    print("Validating data quality...")
    
    # Check for required columns (exact same as original)
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        print(f"Warning: Missing required columns: {missing_cols}")
        print(f"Available columns: {df.columns.tolist()}")
    
    # Report data quality metrics (exact same as original)
    total_records = len(df)
    missing_author_age = df.author_age.isna().sum()
    missing_coauth_age = df.coauth_age.isna().sum()
    missing_pub_date = df.pub_date.isna().sum()
    
    print(f"Data Quality Report:")
    print(f"  - Total relationships: {total_records:,}")
    print(f"  - Missing ego author_age: {missing_author_age:,} ({missing_author_age/total_records*100:.1f}%)")
    print(f"  - Missing coauthor age: {missing_coauth_age:,} ({missing_coauth_age/total_records*100:.1f}%)")
    print(f"  - Missing publication date: {missing_pub_date:,} ({missing_pub_date/total_records*100:.1f}%)")
    
    return df


def correct_publication_years(df):
    """
    Correct OpenAlex publication year anomalies and recalculate ages.
    EXACT REPRODUCTION of original correct_publication_years function
    
    OpenAlex often has incorrect early publication years (pre-1950) that skew
    age calculations. This function filters and corrects these issues.
    
    Args:
        df (pd.DataFrame): DataFrame with coauthor data
        
    Returns:
        pd.DataFrame: DataFrame with corrected publication years and ages
    """
    print("Correcting coauthor publication year anomalies...")
    
    # Track corrections (exact same as original)
    initial_invalid = df.coauth_min_year.lt(MIN_VALID_YEAR).sum()
    
    # Filter out unrealistic first publication years (exact same as original)
    df['coauth_min_year'] = df['coauth_min_year'].where(
        df['coauth_min_year'] >= MIN_VALID_YEAR
    )
    
    # Recalculate coauthor age based on corrected years (exact same as original)
    df['coauth_age'] = df.pub_year - df.coauth_min_year
    
    # Recalculate age difference (exact same as original)
    df['age_diff'] = df.coauth_age - df.author_age
    
    final_invalid = df.coauth_min_year.isna().sum()
    corrected = initial_invalid - final_invalid
    
    print(f"  - Initial invalid years (< {MIN_VALID_YEAR}): {initial_invalid:,}")
    print(f"  - Final missing years after correction: {final_invalid:,}")
    print(f"  - Years successfully corrected: {corrected:,}")
    
    return df


def create_age_buckets(df):
    """
    Create age difference buckets for collaboration analysis.
    EXACT REPRODUCTION of original create_age_buckets function
    
    Categorizes coauthor relationships based on career stage differences:
    - much_younger/younger: Junior collaborators
    - same_age: Peer collaborators
    - older/much_older: Senior collaborators
    
    Args:
        df (pd.DataFrame): DataFrame with age_diff column
        
    Returns:
        pd.DataFrame: DataFrame with age_bucket column
    """
    print("Creating age difference buckets...")
    
    # Apply age bucket logic using numpy for efficiency (exact same as original)
    age_diff_values = df.age_diff.to_numpy()
    categories = np.empty(age_diff_values.shape, dtype=object)
    
    # Apply age bucket logic (exact same as original)
    categories[age_diff_values < AGE_BUCKETS['much_younger'][1]] = "much_younger"
    categories[
        (age_diff_values >= AGE_BUCKETS['younger'][0]) & 
        (age_diff_values < AGE_BUCKETS['younger'][1])
    ] = "younger"
    categories[
        (age_diff_values >= AGE_BUCKETS['same_age'][0]) & 
        (age_diff_values < AGE_BUCKETS['same_age'][1])
    ] = "same_age"
    categories[
        (age_diff_values >= AGE_BUCKETS['older'][0]) & 
        (age_diff_values < AGE_BUCKETS['older'][1])
    ] = "older"
    categories[age_diff_values >= AGE_BUCKETS['much_older'][0]] = "much_older"

    df['age_bucket'] = categories
    
    # Verify that missing age buckets match missing coauthor ages (exact same as original)
    missing_buckets = df['age_bucket'].isna().sum()
    missing_coauth_ages = df['coauth_age'].isna().sum()
    
    print(f"  - Age buckets created: {len(df) - missing_buckets:,}")
    print(f"  - Missing age buckets: {missing_buckets:,}")
    
    if missing_buckets != missing_coauth_ages:
        print(f"  - Warning: Mismatch between missing buckets ({missing_buckets}) and missing ages ({missing_coauth_ages})")
    
    # Report bucket distribution (exact same as original)
    bucket_counts = df['age_bucket'].value_counts()
    print("  - Age bucket distribution:")
    for bucket, count in bucket_counts.items():
        print(f"    • {bucket}: {count:,} ({count/len(df)*100:.1f}%)")
    
    return df


def create_age_standardization(df):
    """
    Create standardized age representation for timeline visualization.
    EXACT REPRODUCTION of original create_age_standardization function
    
    Args:
        df (pd.DataFrame): DataFrame with author_age and pub_date columns
        
    Returns:
        pd.DataFrame: DataFrame with age_std column
    """
    print("Creating standardized age representation...")
    
    try:
        # Extract date components from pub_date and create age_std (exact same as original)
        df["age_std"] = (
            AGE_STD_PREFIX + 
            df.author_age.astype(str).map(lambda x: x.zfill(AGE_PADDING_WIDTH)) + 
            "-" + 
            df.pub_date.map(lambda x: "-".join(x.split("-")[-2:]) if isinstance(x, str) else "01-01")
        )
        
        # Handle leap year edge case (Feb 29 -> Feb 28) (exact same as original)
        df["age_std"] = df.age_std.map(
            lambda x: x.replace("29", "28") if x and x.endswith("29") else x
        )
        
        print("Successfully created age_std column")
        
    except Exception as e:
        print(f"Error creating age_std: {e}")
        print("Using fallback approach...")
        
        # Fallback approach (exact same as original)
        df["age_std"] = df.apply(
            lambda row: (
                f"{AGE_STD_PREFIX}{str(int(row.author_age)).zfill(AGE_PADDING_WIDTH)}-"
                f"{row.pub_date.split('-')[1]}-{row.pub_date.split('-')[2]}"
            ) if (
                not pd.isna(row.author_age) and 
                isinstance(row.pub_date, str) and 
                len(row.pub_date.split('-')) >= 3
            ) else None, 
            axis=1
        )
        
        # Handle leap year edge case (exact same as original)
        df["age_std"] = df.age_std.map(
            lambda x: x.replace("29", "28") if x and x.endswith("29") else x
        )
        
        print("Created age_std column with fallback approach")
    
    valid_age_std = df.age_std.notna().sum()
    print(f"  - Valid age_std records: {valid_age_std:,}")
    
    return df


@dg.asset(deps=["timeline_coauthor_main"])  # String dependency reference
def coauthor_preprocessing(duckdb: DuckDBResource):  # 🆕 UPDATED: Use DuckDB resource
    """
    UPDATED to use DuckDB resource, but all business logic remains identical
    
    Main processing pipeline:
    1. Load coauthor relationship data with author metadata via SQL join
    2. Filter relationships and validate data quality
    3. Correct publication year anomalies (OpenAlex pre-1950 issues)
    4. Calculate age differences and assign age buckets
    5. Create standardized age representation for visualization
    6. Export processed collaboration dataset
    """
    
    print("🚀 Starting coauthor preprocessing...")
    
    # 🆕 NEW: Use DuckDB resource with adapter
    with duckdb.get_connection() as conn:
        # Create adapter to maintain exact same interface
        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database via DuckDB resource")
        
        # === ALL BUSINESS LOGIC BELOW IS IDENTICAL TO ORIGINAL ===
        
        # Load coauthor data with complex joins (exact same as original)
        df = load_coauthor_data(db_exporter)
        
        # Validate data quality (exact same function call as original)
        df = validate_data_quality(df)
        
        # Filter records with valid author ages (required for analysis) (exact same as original)
        print("Filtering records with valid author ages...")
        initial_count = len(df)
        df = df[~df.author_age.isna()].reset_index(drop=True)
        df['author_age'] = df.author_age.astype(int)
        filtered_count = initial_count - len(df)
        print(f"  - Removed {filtered_count:,} records without valid author age")
        print(f"  - Remaining records: {len(df):,}")
        
        # Correct publication year anomalies (exact same function call as original)
        df = correct_publication_years(df)
        
        # Create age buckets for analysis (exact same function call as original)
        df = create_age_buckets(df)
        
        # Create standardized age representation (exact same function call as original)
        df = create_age_standardization(df)
        
        # Save processed data (exact same as original)
        output_path = DATA_PROCESSED / OUTPUT_FILE
        print(f"Saving {len(df):,} processed coauthor relationships to {output_path}")
        df.to_parquet(output_path)
        print("Coauthor preprocessing completed successfully!")
        
        # Print comprehensive processing summary (exact same as original)
        print("\n=== Processing Summary ===")
        print(f"Total relationships processed: {len(df):,}")
        print(f"Unique ego authors: {df.aid.nunique():,}")
        print(f"Unique coauthors: {df.coauth_aid.nunique():,}")
        print(f"Year range: {df.pub_year.min()}-{df.pub_year.max()}")
        print(f"Relationships with age buckets: {df.age_bucket.notna().sum():,}")
        print(f"Relationships with shared institutions: {df.shared_institutions.notna().sum():,}")
        
        # Collaboration type distribution (exact same as original)
        if 'acquaintance' in df.columns:
            print("Collaboration types:")
            for collab_type, count in df.acquaintance.value_counts().items():
                print(f"  - {collab_type}: {count:,} ({count/len(df)*100:.1f}%)")
        
        # No manual close needed - context manager handles it
        print("🔐 Database connection closed automatically by DuckDB resource")
        
        return f"Processed {len(df)} coauthor relationships, saved to {output_path}"


# Simple definitions - faithful to original script structure
defs = dg.Definitions(
    assets=[
        coauthor_preprocessing
    ]
)