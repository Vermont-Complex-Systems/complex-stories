"""
visualization_prep.py

Stage 3: Prepare datasets for interactive dashboards and analysis
"""
import numpy as np
import pandas as pd
import dagster as dg
from dagster import MaterializeResult, MetadataValue

from config import config

@dg.asset(
    deps=["coauthor"],
    group_name="export",
    description="👩‍🎓 Prepare researcher career data for timeline and profile visualizations"
)
def author():
    """Process author career data for visualization with age standardization"""
    
    print("🚀 Starting researcher dataset preparation...")
    
    # HRDAG: Define file paths
    input_file = config.data_raw_path / config.author_output_file  # author_profiles.parquet
    output_file = config.data_processed_path / config.author_output_file  # Final viz-ready file
    
    # HRDAG: Load from previous stage
    print(f"📖 Loading author profiles from {input_file}")
    df = pd.read_parquet(input_file)
    print(f"Retrieved {len(df)} author records")
    
    # Basic data quality validation
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
    
    # Create standardized age representation for timeline visualization
    print("Creating standardized age representation for timeline visualization...")
    
    try:
        # Generate random month and day components for smooth animation
        months = np.char.zfill(
            np.random.randint(1, 13, len(df)).astype(str), 2
        )
        days = np.char.zfill(
            np.random.randint(1, 29, len(df)).astype(str), 2  # Avoid leap year issues
        )
        
        # Create age_std format: "1{age:03d}-{month:02d}-{day:02d}"
        # This enables smooth timeline animations in the dashboard
        df["age_std"] = (
            "1" + 
            df.author_age.astype(str).str.replace(".0", "").map(lambda x: x.zfill(3)) + 
            "-" + months + "-" + days
        )
        
        print("Successfully created age_std column using vectorized approach")
        
    except Exception as e:
        print(f"Error in vectorized approach: {e}")
        print("Falling back to row-by-row processing...")
        # Fallback approach
        df["age_std"] = df.apply(
            lambda row: (
                f"1{str(int(row.author_age)).zfill(3)}-"
                f"{np.random.randint(1, 13):02d}-"
                f"{np.random.randint(1, 29):02d}"
            ) if not pd.isna(row.author_age) else None, 
            axis=1
        )
        print("Created age_std column with fallback approach")
    
    # Handle leap year edge case (Feb 29 -> Feb 28)
    df["age_std"] = df.age_std.map(
        lambda x: x.replace("29", "28") if x and x.endswith("29") else x
    )
    
    valid_age_std = df.age_std.notna().sum()
    print(f"Successfully created age_std for {valid_age_std} records")
    
    # HRDAG: Save processed data to export directory
    print(f"💾 Saving {len(df)} processed author records to {output_file}")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_file)
    
    print("✅ Researcher dataset preparation completed!")
    print(f"Total authors processed: {len(df)}")
    print(f"Unique author IDs: {df.aid.nunique()}")
    
    if 'institution' in df.columns:
        print(f"Unique institutions: {df.institution.nunique()}")
        
    if 'pub_year' in df.columns:
        year_min = df.pub_year.min()
        year_max = df.pub_year.max()
        print(f"Year range: {year_min}-{year_max}")
    
    print(f"Records with age_std: {valid_age_std}")
    
    return MaterializeResult(
        metadata={
            "researcher_records": MetadataValue.int(len(df)),
            "unique_researchers": MetadataValue.int(int(df.aid.nunique())),
            "records_with_age_std": MetadataValue.int(int(valid_age_std)),
            "institutions": MetadataValue.int(int(df.institution.nunique()) if 'institution' in df.columns else 0),
            "input_file": MetadataValue.path(str(input_file)),
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