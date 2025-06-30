"""
author_preprocessing_assets.py

Updated to use centralized configuration instead of hardcoded values.
All business logic remains identical - only configuration management changed.
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import dagster as dg
from dagster_duckdb import DuckDBResource

# Import configuration and modules
from config import PipelineConfig
from modules.database_adapter import DatabaseExporterAdapter

# Age Standardization Format (from config):
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


def generate_random_date_components(size, config: PipelineConfig):
    """
    Generate random month and day components for date standardization.
    UPDATED to use config for month and day ranges
    
    Args:
        size (int): Number of random date components to generate
        config (PipelineConfig): Configuration with month/day ranges
        
    Returns:
        tuple: (months, days) as zero-padded string arrays
    """
    months = np.char.zfill(
        np.random.randint(config.month_range[0], config.month_range[1] + 1, size).astype(str), 
        2
    )
    days = np.char.zfill(
        np.random.randint(config.day_range[0], config.day_range[1] + 1, size).astype(str), 
        2
    )
    return months, days


def create_age_standardization(df, config: PipelineConfig):
    """
    Create standardized age representation for timeline visualization.
    UPDATED to use config for age standardization settings
    
    The age_std format enables smooth temporal animations in frontend:
    - Format: "{prefix}{age:0{width}d}-{month:02d}-{day:02d}"
    - Year component represents career stage (prefix + author_age)
    - Month/day provide random variation for animation smoothness
    
    Args:
        df (pd.DataFrame): DataFrame with author_age column
        config (PipelineConfig): Configuration with age standardization settings
        
    Returns:
        pd.DataFrame: DataFrame with added age_std column
    """
    print("Creating standardized age representation for visualization...")
    
    try:
        # Generate random date components using config
        months, days = generate_random_date_components(len(df), config)
        
        # Create age_std with consistent formatting using config values
        df["age_std"] = (
            config.age_std_prefix + 
            df.author_age.astype(str).str.replace(".0", "").map(lambda x: x.zfill(config.age_padding_width)) + 
            "-" + months + "-" + days
        )
        
        print("Successfully created age_std column using vectorized approach")
        
    except Exception as e:
        print(f"Error in vectorized approach: {e}")
        print("Falling back to row-by-row processing...")
        
        # Fallback approach with better error handling using config values
        df["age_std"] = df.apply(
            lambda row: (
                f"{config.age_std_prefix}{str(int(row.author_age)).zfill(config.age_padding_width)}-"
                f"{np.random.randint(config.month_range[0], config.month_range[1] + 1):02d}-"
                f"{np.random.randint(config.day_range[0], config.day_range[1] + 1):02d}"
            ) if not pd.isna(row.author_age) else None, 
            axis=1
        )
        
        print("Created age_std column with fallback approach")
    
    # Handle leap year edge case (Feb 29 -> Feb 28) (exact same as original)
    df["age_std"] = df.age_std.map(
        lambda x: x.replace("29", "28") if x and x.endswith("29") else x
    )
    
    return df


def validate_data_quality(df, config: PipelineConfig):
    """
    Validate data quality and report issues.
    UPDATED to use config for required columns validation
    
    Args:
        df (pd.DataFrame): Author DataFrame to validate
        config (PipelineConfig): Configuration with required columns list
        
    Returns:
        pd.DataFrame: Validated DataFrame
    """
    print("Validating data quality...")
    
    # Check for required columns using config
    required_columns = config.required_author_columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(f"Warning: Missing required columns: {missing_cols}")
        print(f"Available columns: {df.columns.tolist()}")
        print(f"Required columns from config: {required_columns}")
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
    
    # Check age distribution with config age thresholds
    if not df.author_age.isna().all():
        age_min = df.author_age.min()
        age_max = df.author_age.max()
        age_mean = df.author_age.mean()
        
        print(f"  - Age range: {age_min:.0f} to {age_max:.0f} years")
        print(f"  - Mean age: {age_mean:.1f} years")
        
        # Validate against config thresholds
        if age_min < config.min_author_age:
            print(f"  - Warning: Found ages below minimum threshold ({config.min_author_age})")
        if age_max > config.max_author_age:
            print(f"  - Warning: Found ages above maximum threshold ({config.max_author_age})")
    
    return df


@dg.asset(deps=["timeline_paper_main"])  # String dependency reference
def author_preprocessing(duckdb: DuckDBResource, config: PipelineConfig):
    """
    UPDATED to use centralized configuration for all settings and paths
    
    Main processing pipeline:
    1. Load author data from database
    2. Validate required columns exist (using config)
    3. Create standardized age representation (age_std) for visualization:
       - Format: "{prefix}{age:0{width}d}-{month:02d}-{day:02d}" (using config)
       - Enables smooth temporal animations in frontend
    4. Handle missing values and data type conversion
    5. Export processed dataset to parquet format (using config path)
    """
    
    print("🚀 Starting author preprocessing...")
    
    # Ensure output directory exists using config
    config.data_processed_path.mkdir(parents=True, exist_ok=True)
    
    # 🆕 NEW: Use DuckDB resource with adapter
    with duckdb.get_connection() as conn:
        # Create adapter to maintain exact same interface
        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database via DuckDB resource")
        
        # === BUSINESS LOGIC NOW USES CONFIG VALUES ===
        
        # Load author data from database (exact same as original)
        print("Querying author data from database...")
        df = db_exporter.con.sql("SELECT * FROM author").fetchdf()
        print(f"Retrieved {len(df):,} author records")
        
        # Validate data quality using config for validation rules
        df = validate_data_quality(df, config)
        
        # Create standardized age representation using config settings
        df = create_age_standardization(df, config)
        
        # Validate age_std creation (exact same as original)
        valid_age_std = df.age_std.notna().sum()
        print(f"Successfully created age_std for {valid_age_std:,} records")
        
        # Save processed data using config path and filename
        output_path = config.data_processed_path / config.author_output_file
        print(f"Saving {len(df):,} processed author records to {output_path}")
        df.to_parquet(output_path)
        print("Author preprocessing completed successfully!")
        
        # Print processing summary with enhanced config-aware reporting
        print("\n=== Processing Summary ===")
        print(f"Total authors processed: {len(df):,}")
        print(f"Unique author IDs: {df.aid.nunique():,}")
        
        if 'institution' in df.columns:
            unique_institutions = df.institution.nunique()
            print(f"Unique institutions: {unique_institutions:,}")
            
        if 'pub_year' in df.columns:
            year_min = df.pub_year.min()
            year_max = df.pub_year.max()
            print(f"Year range: {year_min}-{year_max}")
            
            # Check against config year validation
            if year_min < config.min_valid_year:
                print(f"  - Warning: Years below {config.min_valid_year} found")
            if year_max > config.max_valid_year:
                print(f"  - Warning: Years above {config.max_valid_year} found")
        
        print(f"Records with age_std: {valid_age_std:,}")
        
        # Config-aware summary
        print(f"\nConfiguration used:")
        print(f"  - Age prefix: '{config.age_std_prefix}'")
        print(f"  - Age padding width: {config.age_padding_width}")
        print(f"  - Month range: {config.month_range}")
        print(f"  - Day range: {config.day_range}")
        print(f"  - Output file: {config.author_output_file}")
        
        # No manual close needed - context manager handles it
        print("🔐 Database connection closed automatically by DuckDB resource")
        
        return f"Processed {len(df)} author records, saved to {output_path}"


# Simple definitions - faithful to original script structure
defs = dg.Definitions(
    assets=[
        author_preprocessing
    ]
)