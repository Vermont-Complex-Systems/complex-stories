"""
visualization_prep.py

Stage 3: Prepare datasets for interactive dashboards and analysis
"""
import numpy as np
import pandas as pd
import dagster as dg
from dagster import MaterializeResult, MetadataValue

from config import config
from shared.utils.data_transforms import create_age_standardization

def validate_data_quality(df):
    """Validate data quality and print quality report"""
    print("Validating data quality...")
    total_records = len(df)
    missing_age = df.author_age.isna().sum()
    missing_aid = df.aid.isna().sum()
    
    print(f"Data Quality Report:")
    print(f"  - Total records: {total_records}")
    print(f"  - Missing author_age: {missing_age} ({missing_age/total_records*100:.1f}%)")
    print(f"  - Missing aid: {missing_aid} ({missing_aid/total_records*100:.1f}%)")
    
    if not df.author_age.isna().all():
        age_min = float(df.author_age.min())
        age_max = float(df.author_age.max())
        age_mean = float(df.author_age.mean())
        print(f"  - Age range: {age_min:.0f} to {age_max:.0f} years")
        print(f"  - Mean age: {age_mean:.1f} years")
    
    return df


def load_author_data():
    """Load author data from the input file"""
    print("🚀 Starting researcher dataset preparation...")
    
    # HRDAG: Define file paths
    input_file = config.data_raw_path / config.author_output_file  # author_profiles.parquet
    
    # HRDAG: Load from previous stage
    print(f"📖 Loading author profiles from {input_file}")
    df = pd.read_parquet(input_file)
    print(f"Retrieved {len(df)} author records")
    
    return df

def print_final_summary(df):
    """Print final processing summary"""
    print("✅ Researcher dataset preparation completed!")
    print(f"Total authors processed: {len(df)}")
    print(f"Unique author IDs: {df.aid.nunique()}")
    
    if 'institution' in df.columns:
        print(f"Unique institutions: {df.institution.nunique()}")
        
    if 'pub_year' in df.columns:
        year_min = df.pub_year.min()
        year_max = df.pub_year.max()
        print(f"Year range: {year_min}-{year_max}")
    
    valid_age_std = df.age_std.notna().sum()
    print(f"Records with age_std: {valid_age_std}")
    
    return df

def normalize_author_institutions(df):
    """Clean and normalize institution names for author data"""
    print("Normalizing author institution names...")
    df_normalized = df.copy()
    
    if 'institution' in df_normalized.columns:
        df_normalized['institution_normalized'] = (
            df_normalized['institution']
            .fillna('Unknown')
            .str.strip()
            .str.replace(r'\s+', ' ', regex=True)
            .str.replace(r'[^\w\s\-\.]', '', regex=True)
            .str.title()
        )
        print(f"  - Added institution_normalized")
    else:
        print("  - No institution column found in author data")
    
    return df_normalized

def calculate_age(df):
    df['author_age'] = df.pub_year - df.first_pub_year
    return df

@dg.asset(
    deps=["coauthor_cache"],
    group_name="export",
    description="👩‍🎓 Prepare researcher career data for timeline and profile visualizations"
)
def author():
    """Process author career data for visualization with age standardization"""
    
    # Load data
    df = load_author_data()
    
    # Apply all transformations using pipe
    df_processed = (df
                    .pipe(calculate_age)
                    .pipe(validate_data_quality)
                    .pipe(create_age_standardization)
                    .pipe(normalize_author_institutions)  # NEW: If institution column exists
                    .pipe(print_final_summary)
                   )
    
    # Extract metrics for metadata
    valid_age_std = df_processed.age_std.notna().sum()
    unique_institutions = df_processed.institution.nunique() if 'institution' in df_processed.columns else 0
    
    # HRDAG: Save processed data to export directory
    output_file = config.data_export_path / config.author_output_file
    print(f"💾 Saving {len(df_processed)} processed author records to {output_file}")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df_processed.to_parquet(output_file)
    
    return MaterializeResult(
        metadata={
            "researcher_records": MetadataValue.int(len(df_processed)),
            "unique_researchers": MetadataValue.int(int(df_processed.aid.nunique())),
            "records_with_age_std": MetadataValue.int(int(valid_age_std)),
            "institutions": MetadataValue.int(int(unique_institutions)),
            "input_file": MetadataValue.path(str(config.data_raw_path / config.author_output_file)),
            "output_file": MetadataValue.path(str(output_file)),
            "visualization_feature": MetadataValue.md(
                "**Age standardization** enables smooth timeline animations showing "
                "career progression and collaboration patterns over time."
            ),
            "research_value": MetadataValue.md(
                "**Researcher profile dataset** for career stage analysis and "
                "timeline visualization of academic progression."
            )
        }
    )