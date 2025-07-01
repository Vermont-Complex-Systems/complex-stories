"""
Simplified author_preprocessing_assets.py
"""
import numpy as np
import pandas as pd
import dagster as dg
from dagster_duckdb import DuckDBResource

from config import config
from modules.database_adapter import DatabaseExporterAdapter

@dg.asset(deps=["timeline_paper_main"])
def author_preprocessing(duckdb: DuckDBResource):
    """Process author data for visualization"""
    
    print("🚀 Starting author preprocessing...")
    
    with duckdb.get_connection() as conn:
        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database")
        
        # Load author data from database
        print("Querying author data from database...")
        df = db_exporter.con.sql("SELECT * FROM author").fetchdf()
        print(f"Retrieved {len(df)} author records")
        
        # Basic data quality check
        print("Validating data quality...")
        total_records = len(df)
        missing_age = df.author_age.isna().sum()
        missing_aid = df.aid.isna().sum()
        
        print(f"Data Quality Report:")
        print(f"  - Total records: {total_records}")
        print(f"  - Missing author_age: {missing_age} ({missing_age/total_records*100:.1f}%)")
        print(f"  - Missing aid: {missing_aid} ({missing_aid/total_records*100:.1f}%)")
        
        if not df.author_age.isna().all():
            age_min = df.author_age.min()
            age_max = df.author_age.max()
            age_mean = df.author_age.mean()
            print(f"  - Age range: {age_min:.0f} to {age_max:.0f} years")
            print(f"  - Mean age: {age_mean:.1f} years")
        
        # Create standardized age representation for visualization
        print("Creating standardized age representation...")
        
        try:
            # Generate random month and day components
            months = np.char.zfill(
                np.random.randint(1, 13, len(df)).astype(str), 2
            )
            days = np.char.zfill(
                np.random.randint(1, 29, len(df)).astype(str), 2  # Avoid leap year issues
            )
            
            # Create age_std format: "1{age:03d}-{month:02d}-{day:02d}"
            df["age_std"] = (
                "1" + 
                df.author_age.astype(str).str.replace(".0", "").map(lambda x: x.zfill(3)) + 
                "-" + months + "-" + days
            )
            
            print("Successfully created age_std column")
            
        except Exception as e:
            print(f"Error creating age_std: {e}")
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
        
        # Save processed data
        output_path = config.DATA_PROCESSED_DIR / config.AUTHOR_OUTPUT_FILE
        print(f"Saving {len(df)} processed author records to {output_path}")
        df.to_parquet(output_path)
        
        print("✅ Author preprocessing completed!")
        print(f"Total authors processed: {len(df)}")
        print(f"Unique author IDs: {df.aid.nunique()}")
        
        if 'institution' in df.columns:
            print(f"Unique institutions: {df.institution.nunique()}")
            
        if 'pub_year' in df.columns:
            year_min = df.pub_year.min()
            year_max = df.pub_year.max()
            print(f"Year range: {year_min}-{year_max}")
        
        print(f"Records with age_std: {valid_age_std}")
        
        return f"Processed {len(df)} author records, saved to {output_path}"