# shared/utils/data_transforms.py
import numpy as np
import pandas as pd

def create_age_standardization(df):
    """Create standardized age representation for timeline visualization"""
    print("Creating standardized age representation for timeline visualization...")
    df_with_age_std = df.copy()
    
    try:
        # Generate random month and day components for smooth animation
        months = np.char.zfill(
            np.random.randint(1, 13, len(df_with_age_std)).astype(str), 2
        )
        days = np.char.zfill(
            np.random.randint(1, 28, len(df_with_age_std)).astype(str), 2  # Max 28 days - no Feb 29th
        )
        
        # Create age_std format: "1{age:03d}-{month:02d}-{day:02d}"
        df_with_age_std["age_std"] = (
            "1" + 
            df_with_age_std.author_age.astype(str).str.replace(".0", "").map(lambda x: x.zfill(3)) + 
            "-" + months + "-" + days
        )
        
        print("Successfully created age_std column using vectorized approach")
        
    except Exception as e:
        print(f"Error in vectorized approach: {e}")
        print("Falling back to row-by-row processing...")
        df_with_age_std["age_std"] = df_with_age_std.apply(
            lambda row: (
                f"1{str(int(row.author_age)).zfill(3)}-"
                f"{np.random.randint(1, 13):02d}-"
                f"{np.random.randint(1, 28):02d}"  # Max 28 days - no Feb 29th
            ) if not pd.isna(row.author_age) else None, 
            axis=1
        )
        print("Created age_std column with fallback approach")
    
    return df_with_age_std

