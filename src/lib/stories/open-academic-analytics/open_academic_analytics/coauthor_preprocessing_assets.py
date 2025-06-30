"""
coauthor_preprocessing_assets.py

Fixed version with proper config usage and import paths.
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

# Import configuration and database adapter
from config import PipelineConfig
from modules.database_adapter import DatabaseExporterAdapter  # Fixed import path


def load_coauthor_data(db_exporter, config: PipelineConfig):
    """
    Load coauthor relationship data with author metadata via complex SQL join.
    UPDATED to use config for max valid year
    
    Args:
        db_exporter: DatabaseExporterAdapter instance with active connection
        config: PipelineConfig with settings
        
    Returns:
        pd.DataFrame: Coauthor relationships with metadata
    """
    print("Querying coauthor data with author metadata...")
    
    # Complex SQL join query using config for max year
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
    
    df = db_exporter.con.sql(query, params=[config.max_valid_year]).fetchdf()
    print(f"Retrieved {len(df):,} coauthor relationships")
    
    return df


def validate_data_quality(df, config: PipelineConfig):
    """
    Validate data quality and report missing information.
    UPDATED to use config for required columns
    """
    print("Validating data quality...")
    
    # Check for required columns using config
    missing_cols = [col for col in config.required_coauthor_columns if col not in df.columns]
    if missing_cols:
        print(f"Warning: Missing required columns: {missing_cols}")
        print(f"Available columns: {df.columns.tolist()}")
    
    # Report data quality metrics
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


def correct_publication_years(df, config: PipelineConfig):
    """
    Correct OpenAlex publication year anomalies and recalculate ages.
    UPDATED to use config for min valid year
    """
    print("Correcting coauthor publication year anomalies...")
    
    # Track corrections using config
    initial_invalid = df.coauth_min_year.lt(config.min_valid_year).sum()
    
    # Filter out unrealistic first publication years using config
    df['coauth_min_year'] = df['coauth_min_year'].where(
        df['coauth_min_year'] >= config.min_valid_year
    )
    
    # Recalculate coauthor age based on corrected years
    df['coauth_age'] = df.pub_year - df.coauth_min_year
    
    # Recalculate age difference
    df['age_diff'] = df.coauth_age - df.author_age
    
    final_invalid = df.coauth_min_year.isna().sum()
    corrected = initial_invalid - final_invalid
    
    print(f"  - Initial invalid years (< {config.min_valid_year}): {initial_invalid:,}")
    print(f"  - Final missing years after correction: {final_invalid:,}")
    print(f"  - Years successfully corrected: {corrected:,}")
    
    return df


def create_age_buckets(df, config: PipelineConfig):
    """
    Create age difference buckets for collaboration analysis.
    UPDATED to use config for age bucket definitions
    """
    print("Creating age difference buckets...")
    
    # Apply age bucket logic using config values
    age_diff_values = df.age_diff.to_numpy()
    categories = np.empty(age_diff_values.shape, dtype=object)
    
    # Apply age bucket logic using config
    categories[age_diff_values < config.age_buckets['much_younger'][1]] = "much_younger"
    categories[
        (age_diff_values >= config.age_buckets['younger'][0]) & 
        (age_diff_values < config.age_buckets['younger'][1])
    ] = "younger"
    categories[
        (age_diff_values >= config.age_buckets['same_age'][0]) & 
        (age_diff_values < config.age_buckets['same_age'][1])
    ] = "same_age"
    categories[
        (age_diff_values >= config.age_buckets['older'][0]) & 
        (age_diff_values < config.age_buckets['older'][1])
    ] = "older"
    categories[age_diff_values >= config.age_buckets['much_older'][0]] = "much_older"

    df['age_bucket'] = categories
    
    # Verify that missing age buckets match missing coauthor ages
    missing_buckets = df['age_bucket'].isna().sum()
    missing_coauth_ages = df['coauth_age'].isna().sum()
    
    print(f"  - Age buckets created: {len(df) - missing_buckets:,}")
    print(f"  - Missing age buckets: {missing_buckets:,}")
    
    if missing_buckets != missing_coauth_ages:
        print(f"  - Warning: Mismatch between missing buckets ({missing_buckets}) and missing ages ({missing_coauth_ages})")
    
    # Report bucket distribution
    bucket_counts = df['age_bucket'].value_counts()
    print("  - Age bucket distribution:")
    for bucket, count in bucket_counts.items():
        print(f"    • {bucket}: {count:,} ({count/len(df)*100:.1f}%)")
    
    return df


def create_age_standardization(df, config: PipelineConfig):
    """
    Create standardized age representation for timeline visualization.
    UPDATED to use config for age standardization settings
    """
    print("Creating standardized age representation...")
    
    try:
        # Extract date components from pub_date and create age_std using config
        df["age_std"] = (
            config.age_std_prefix + 
            df.author_age.astype(str).map(lambda x: x.zfill(config.age_padding_width)) + 
            "-" + 
            df.pub_date.map(lambda x: "-".join(x.split("-")[-2:]) if isinstance(x, str) else "01-01")
        )
        
        # Handle leap year edge case (Feb 29 -> Feb 28)
        df["age_std"] = df.age_std.map(
            lambda x: x.replace("29", "28") if x and x.endswith("29") else x
        )
        
        print("Successfully created age_std column")
        
    except Exception as e:
        print(f"Error creating age_std: {e}")
        print("Using fallback approach...")
        
        # Fallback approach using config
        df["age_std"] = df.apply(
            lambda row: (
                f"{config.age_std_prefix}{str(int(row.author_age)).zfill(config.age_padding_width)}-"
                f"{row.pub_date.split('-')[1]}-{row.pub_date.split('-')[2]}"
            ) if (
                not pd.isna(row.author_age) and 
                isinstance(row.pub_date, str) and 
                len(row.pub_date.split('-')) >= 3
            ) else None, 
            axis=1
        )
        
        # Handle leap year edge case
        df["age_std"] = df.age_std.map(
            lambda x: x.replace("29", "28") if x and x.endswith("29") else x
        )
        
        print("Created age_std column with fallback approach")
    
    valid_age_std = df.age_std.notna().sum()
    print(f"  - Valid age_std records: {valid_age_std:,}")
    
    return df


@dg.asset(deps=["timeline_coauthor_main"])  # String dependency reference
def coauthor_preprocessing(duckdb: DuckDBResource, config: PipelineConfig):
    """
    UPDATED to use config for all settings and paths
    
    Main processing pipeline:
    1. Load coauthor relationship data with author metadata via SQL join
    2. Filter relationships and validate data quality
    3. Correct publication year anomalies (OpenAlex pre-1950 issues)
    4. Calculate age differences and assign age buckets
    5. Create standardized age representation for visualization
    6. Export processed collaboration dataset
    """
    
    print("🚀 Starting coauthor preprocessing...")
    
    # Ensure output directory exists
    config.data_processed_path.mkdir(parents=True, exist_ok=True)
    
    with duckdb.get_connection() as conn:
        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database via DuckDB resource")
        
        # Load coauthor data with complex joins (now passing config)
        df = load_coauthor_data(db_exporter, config)
        
        # Validate data quality (now passing config)
        df = validate_data_quality(df, config)
        
        # Filter records with valid author ages (required for analysis)
        print("Filtering records with valid author ages...")
        initial_count = len(df)
        df = df[~df.author_age.isna()].reset_index(drop=True)
        df['author_age'] = df.author_age.astype(int)
        filtered_count = initial_count - len(df)
        print(f"  - Removed {filtered_count:,} records without valid author age")
        print(f"  - Remaining records: {len(df):,}")
        
        # Correct publication year anomalies (now passing config)
        df = correct_publication_years(df, config)
        
        # Create age buckets for analysis (now passing config)
        df = create_age_buckets(df, config)
        
        # Create standardized age representation (now passing config)
        df = create_age_standardization(df, config)
        
        # Save processed data using config for output path
        output_path = config.data_processed_path / config.coauthor_output_file
        print(f"Saving {len(df):,} processed coauthor relationships to {output_path}")
        df.to_parquet(output_path)
        print("Coauthor preprocessing completed successfully!")
        
        # Print comprehensive processing summary
        print("\n=== Processing Summary ===")
        print(f"Total relationships processed: {len(df):,}")
        print(f"Unique ego authors: {df.aid.nunique():,}")
        print(f"Unique coauthors: {df.coauth_aid.nunique():,}")
        print(f"Year range: {df.pub_year.min()}-{df.pub_year.max()}")
        print(f"Relationships with age buckets: {df.age_bucket.notna().sum():,}")
        print(f"Relationships with shared institutions: {df.shared_institutions.notna().sum():,}")
        
        # Collaboration type distribution
        if 'acquaintance' in df.columns:
            print("Collaboration types:")
            for collab_type, count in df.acquaintance.value_counts().items():
                print(f"  - {collab_type}: {count:,} ({count/len(df)*100:.1f}%)")
        
        print("🔐 Database connection closed automatically by DuckDB resource")
        
        return f"Processed {len(df)} coauthor relationships, saved to {output_path}"


# Simple definitions - faithful to original script structure
defs = dg.Definitions(
    assets=[
        coauthor_preprocessing
    ]
)