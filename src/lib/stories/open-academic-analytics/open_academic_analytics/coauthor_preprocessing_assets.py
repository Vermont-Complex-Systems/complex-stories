"""
Simplified coauthor_preprocessing_assets.py
"""
import numpy as np
import pandas as pd
import dagster as dg
from dagster_duckdb import DuckDBResource

from config import config
from modules.database_adapter import DatabaseExporterAdapter

@dg.asset(deps=["timeline_coauthor_main"])
def coauthor_preprocessing(duckdb: DuckDBResource):
    """Process coauthor relationships for visualization"""
    
    print("🚀 Starting coauthor preprocessing...")
    
    with duckdb.get_connection() as conn:
        db_exporter = DatabaseExporterAdapter(conn)
        
        # Check if we have data
        coauthor_count = db_exporter.con.execute("SELECT COUNT(*) FROM coauthor2").fetchone()[0]
        print(f"Found {coauthor_count} coauthor records")
        
        if coauthor_count == 0:
            print("❌ No coauthor data found")
            return "No coauthor data"
        
        # Load coauthor data with author info
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
                c.pub_year < 2024
            ORDER BY c.pub_year
        """
        
        df = db_exporter.con.sql(query).fetchdf()
        print(f"Retrieved {len(df)} coauthor relationships")
        
        if len(df) == 0:
            print("❌ No data after JOIN")
            return "No data after JOIN"
        
        # Filter valid records
        df = df[~df.author_age.isna()].reset_index(drop=True)
        df['author_age'] = df.author_age.astype(int)
        print(f"After filtering: {len(df)} records with valid author ages")
        
        # Correct publication years (remove pre-1950 anomalies)
        df['coauth_min_year'] = df['coauth_min_year'].where(df['coauth_min_year'] >= 1950)
        df['coauth_age'] = df.pub_year - df.coauth_min_year
        df['age_diff'] = df.coauth_age - df.author_age
        
        # Create age buckets
        age_diff_values = df.age_diff.to_numpy()
        categories = np.empty(age_diff_values.shape, dtype=object)
        
        categories[age_diff_values < -15] = "much_younger"
        categories[(age_diff_values >= -15) & (age_diff_values < -7)] = "younger"
        categories[(age_diff_values >= -7) & (age_diff_values < 7)] = "same_age"
        categories[(age_diff_values >= 7) & (age_diff_values < 15)] = "older"
        categories[age_diff_values >= 15] = "much_older"
        
        df['age_bucket'] = categories
        
        # Create age standardization for visualization
        try:
            df["age_std"] = (
                "1" + 
                df.author_age.astype(str).str.zfill(3) + 
                "-" + 
                df.pub_date.map(lambda x: "-".join(x.split("-")[-2:]) if isinstance(x, str) else "01-01")
            )
            # Handle leap year
            df["age_std"] = df.age_std.map(
                lambda x: x.replace("29", "28") if x and x.endswith("29") else x
            )
        except Exception as e:
            print(f"Error creating age_std: {e}")
            df["age_std"] = None
        
        # Save processed data
        output_path = config.DATA_PROCESSED_DIR / config.COAUTHOR_OUTPUT_FILE
        print(f"Saving {len(df)} records to {output_path}")
        df.to_parquet(output_path)
        
        print(f"✅ Success! Processed {len(df)} coauthor relationships")
        print(f"Age bucket distribution:")
        for bucket, count in df['age_bucket'].value_counts().items():
            print(f"  - {bucket}: {count}")
        
        return f"Processed {len(df)} coauthor relationships"