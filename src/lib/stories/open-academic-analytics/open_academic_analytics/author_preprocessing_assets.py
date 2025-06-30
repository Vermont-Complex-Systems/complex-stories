"""
author_preprocessing_assets.py

UPDATED to use Dagster's official DuckDB resource with adapter.
All business logic remains identical - only the database connection changed.
"""

import sys
import os
from pathlib import Path
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
OUTPUT_FILE = "author.parquet"

# Age standardization settings (exact same as original)
AGE_STD_PREFIX = "1"  # Prefix for age standardization
AGE_PADDING_WIDTH = 3  # Zero-pad age to 3 digits
MONTH_RANGE = (1, 12)  # Random month range
DAY_RANGE = (1, 28)    # Random day range (avoid leap year issues)

# Data validation (exact same as original)
REQUIRED_COLUMNS = ['aid', 'author_age']

# Age Standardization Format (exact same as original):
# age_std = "1{author_age:03d}-{random_month:02d}-{random_day:02d}"
# 
# Examples:
# - Author age 5  -> "1005-03-15" (career year 5, random month/day)
# - Author age 25 -> "1025-11-08" (career year 25, random month/day)
#
# Purpose: Enables timeline visualization where:
# - Year component represents career stage
# - Month/day provide smooth animation transitions
# - Consistent format works with D3.js date parsing


def generate_random_date_components(size):
    """
    Generate random month and day components for date standardization.
    EXACT REPRODUCTION of original generate_random_date_components function
    
    Args:
        size (int): Number of random date components to generate
        
    Returns:
        tuple: (months, days) as zero-padded string arrays
    """
    months = np.char.zfill(
        np.random.randint(MONTH_RANGE[0], MONTH_RANGE[1] + 1, size).astype(str), 
        2
    )
    days = np.char.zfill(
        np.random.randint(DAY_RANGE[0], DAY_RANGE[1] + 1, size).astype(str), 
        2
    )
    return months, days


def create_age_standardization(df):
    """
    Create standardized age representation for timeline visualization.
    EXACT REPRODUCTION of original create_age_standardization function
    
    The age_std format enables smooth temporal animations in frontend:
    - Format: "1{age:03d}-{month:02d}-{day:02d}"
    - Year component represents career stage (1000 + author_age)
    - Month/day provide random variation for animation smoothness
    
    Args:
        df (pd.DataFrame): DataFrame with author_age column
        
    Returns:
        pd.DataFrame: DataFrame with added age_std column
    """
    print("Creating standardized age representation for visualization...")
    
    try:
        # Generate random date components (exact same as original)
        months, days = generate_random_date_components(len(df))
        
        # Create age_std with consistent formatting (exact same as original)
        df["age_std"] = (
            AGE_STD_PREFIX + 
            df.author_age.astype(str).str.replace(".0", "").map(lambda x: x.zfill(AGE_PADDING_WIDTH)) + 
            "-" + months + "-" + days
        )
        
        print("Successfully created age_std column using vectorized approach")
        
    except Exception as e:
        print(f"Error in vectorized approach: {e}")
        print("Falling back to row-by-row processing...")
        
        # Fallback approach with better error handling (exact same as original)
        df["age_std"] = df.apply(
            lambda row: (
                f"{AGE_STD_PREFIX}{str(int(row.author_age)).zfill(AGE_PADDING_WIDTH)}-"
                f"{np.random.randint(MONTH_RANGE[0], MONTH_RANGE[1] + 1):02d}-"
                f"{np.random.randint(DAY_RANGE[0], DAY_RANGE[1] + 1):02d}"
            ) if not pd.isna(row.author_age) else None, 
            axis=1
        )
        
        print("Created age_std column with fallback approach")
    
    # Handle leap year edge case (Feb 29 -> Feb 28) (exact same as original)
    df["age_std"] = df.age_std.map(
        lambda x: x.replace("29", "28") if x and x.endswith("29") else x
    )
    
    return df


def validate_data_quality(df):
    """
    Validate data quality and report issues.
    EXACT REPRODUCTION of original validate_data_quality function
    
    Args:
        df (pd.DataFrame): Author DataFrame to validate
        
    Returns:
        pd.DataFrame: Validated DataFrame
    """
    print("Validating data quality...")
    
    # Check for required columns (exact same as original)
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        print(f"Warning: Missing required columns: {missing_cols}")
        print(f"Available columns: {df.columns.tolist()}")
        return df
    
    # Report data quality metrics (exact same as original)
    total_records = len(df)
    missing_age = df.author_age.isna().sum()
    missing_aid = df.aid.isna().sum()
    
    print(f"Data Quality Report:")
    print(f"  - Total records: {total_records:,}")
    print(f"  - Missing author_age: {missing_age:,} ({missing_age/total_records*100:.1f}%)")
    print(f"  - Missing aid: {missing_aid:,} ({missing_aid/total_records*100:.1f}%)")
    
    if missing_age > 0:
        print(f"  - Records with valid age: {total_records - missing_age:,}")
    
    # Check age distribution (exact same as original)
    if not df.author_age.isna().all():
        print(f"  - Age range: {df.author_age.min():.0f} to {df.author_age.max():.0f} years")
        print(f"  - Mean age: {df.author_age.mean():.1f} years")
    
    return df


@dg.asset(deps=["timeline_paper_main"])  # String dependency reference
def author_preprocessing(duckdb: DuckDBResource):  # 🆕 UPDATED: Use DuckDB resource
    """
    UPDATED to use DuckDB resource, but all business logic remains identical
    
    Main processing pipeline:
    1. Load author data from database
    2. Validate required columns exist
    3. Create standardized age representation (age_std) for visualization:
       - Format: "1{age:03d}-{month:02d}-{day:02d}"
       - Enables smooth temporal animations in frontend
    4. Handle missing values and data type conversion
    5. Export processed dataset to parquet format
    """
    
    print("🚀 Starting author preprocessing...")
    
    # 🆕 NEW: Use DuckDB resource with adapter
    with duckdb.get_connection() as conn:
        # Create adapter to maintain exact same interface
        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database via DuckDB resource")
        
        # === ALL BUSINESS LOGIC BELOW IS IDENTICAL TO ORIGINAL ===
        
        # Load author data from database (exact same as original)
        print("Querying author data from database...")
        df = db_exporter.con.sql("SELECT * FROM author").fetchdf()
        print(f"Retrieved {len(df):,} author records")
        
        # Validate data quality (exact same function call as original)
        df = validate_data_quality(df)
        
        # Create standardized age representation (exact same function call as original)
        df = create_age_standardization(df)
        
        # Validate age_std creation (exact same as original)
        valid_age_std = df.age_std.notna().sum()
        print(f"Successfully created age_std for {valid_age_std:,} records")
        
        # Save processed data (exact same as original)
        output_path = DATA_PROCESSED / OUTPUT_FILE
        print(f"Saving {len(df):,} processed author records to {output_path}")
        df.to_parquet(output_path)
        print("Author preprocessing completed successfully!")
        
        # Print processing summary (exact same as original)
        print("\n=== Processing Summary ===")
        print(f"Total authors processed: {len(df):,}")
        print(f"Unique author IDs: {df.aid.nunique():,}")
        if 'institution' in df.columns:
            print(f"Unique institutions: {df.institution.nunique():,}")
        if 'pub_year' in df.columns:
            print(f"Year range: {df.pub_year.min()}-{df.pub_year.max()}")
        print(f"Records with age_std: {valid_age_std:,}")
        
        # No manual close needed - context manager handles it
        print("🔐 Database connection closed automatically by DuckDB resource")
        
        return f"Processed {len(df)} author records, saved to {output_path}"


# Simple definitions - faithful to original script structure
defs = dg.Definitions(
    assets=[
        author_preprocessing
    ]
)