#!/usr/bin/env python3
"""
Script to process dfall.csv into trust_circles.csv format
Using pandas for cleaner, more readable code
"""

import pandas as pd

def process_dfall_to_trust_circles(input_file="dfall.csv", output_file="trust_circles.csv"):
    """
    Process the raw survey data into trust circles format using pandas
    """
    
    # Read and filter data
    try:
        df = pd.read_csv(input_file)
        print(f"Loaded {len(df)} rows from {input_file}")
        
        # Filter to only include Timepoint == 4
        df = df[df['Timepoint'] == 4].copy()
        print(f"Filtered to {len(df)} rows where Timepoint == 4")
        
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Please provide the raw data file.")
        return
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return
    
    if len(df) == 0:
        print("No data found after filtering")
        return
    
    # Institution columns - exclude unwanted patterns
    exclude_patterns = ['TP_Platforms_', 'TP_Month', 'TP_Which_Platforms', 'TP_Measure', 'TP_Social']
    institution_columns = [col for col in df.columns 
                          if col.startswith('TP_') 
                          and not any(pattern in col for pattern in exclude_patterns)]
    
    print(f"Found institution columns: {institution_columns}")
    
    # Create ordinal demographic categories
    # Race ordinal: White=0, Mixed=1, POC=2
    race_cols = ['Dem_Race_White', 'Dem_Race_Mixed', 'Dem_Race_POC']
    if all(col in df.columns for col in race_cols):
        df['race_ord'] = (df[race_cols] == 1.0).idxmax(axis=1).map({
            'Dem_Race_White': 0,
            'Dem_Race_Mixed': 1, 
            'Dem_Race_POC': 2
        }).fillna(0)
    
    # Sexual orientation ordinal: straight=0, bisexual=1, gay=2, other=3  
    orientation_cols = ['Dem_Sexual_Orientation_straight', 'Dem_Sexual_Orientation_Bisexual', 
                       'Dem_Sexual_Orientation_Gay', 'Dem_Sexual_Orientation_other']
    if all(col in df.columns for col in orientation_cols):
        df['orientation_ord'] = (df[orientation_cols] == 1.0).idxmax(axis=1).map({
            'Dem_Sexual_Orientation_straight': 0,
            'Dem_Sexual_Orientation_Bisexual': 1,
            'Dem_Sexual_Orientation_Gay': 2, 
            'Dem_Sexual_Orientation_other': 3
        }).fillna(0)
    
    # Gender ordinal: Woman=0, Man=1, Other=2
    gender_cols = ['Dem_Gender_Woman', 'Dem_Gender_Man', 'Dem_Gender_Other']
    if all(col in df.columns for col in gender_cols):
        df['Dem_Gender_Man'] = (df[gender_cols] == 1.0).idxmax(axis=1).map({
            'Dem_Gender_Woman': 0,
            'Dem_Gender_Man': 1,
            'Dem_Gender_Other': 2
        }).fillna(0)
    
    # Relationship status is already in the right format (0/1)
    demographic_columns = ['Dem_Gender_Man', 'Dem_Relationship_Status_Single', 'orientation_ord', 'race_ord']
    
    print(f"Created ordinal demographic columns: {demographic_columns}")
    
    results = []
    
    # 1. Overall average for all institutions
    for institution in institution_columns:
        avg_distance = df[institution].mean()
        if pd.notna(avg_distance):
            results.append({
                'institution': institution,
                'distance': avg_distance,
                'category': 'overall_average',
                'value': 1.0
            })
    
    # 2. Process each demographic category
    for demo_col in demographic_columns:
        if demo_col in df.columns:
            # Group by demographic values and calculate means
            grouped = df.groupby(demo_col)[institution_columns].mean()
            
            for demo_value, row in grouped.iterrows():
                for institution in institution_columns:
                    avg_distance = row[institution]
                    if pd.notna(avg_distance):
                        results.append({
                            'institution': institution,
                            'distance': avg_distance,
                            'category': demo_col,
                            'value': float(demo_value)
                        })
    
    # Convert to DataFrame and sort
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(['category', 'value', 'institution'])
    
    # Save to CSV
    results_df.to_csv(output_file, index=False)
    print(f"Saved {len(results_df)} rows to {output_file}")
    
    return results_df.to_dict('records')

def main():
    """Main function"""
    print("Processing dfall.csv to trust_circles.csv...")
    
    # Process the data
    result = process_dfall_to_trust_circles()
    
    if result is not None:
        print("\nFirst few rows of output:")
        for i, row in enumerate(result[:10]):
            print(f"{i+1}: {row}")
        
        categories = sorted(set(row['category'] for row in result))
        institutions = sorted(set(row['institution'] for row in result))
        
        print(f"\nCategories found: {categories}")
        print(f"Institutions found: {institutions}")

if __name__ == "__main__":
    main()