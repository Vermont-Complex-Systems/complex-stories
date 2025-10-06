#!/usr/bin/env python3
"""
Script to process dfall.csv into trust_circles.csv format
Using pandas for cleaner, more readable code
"""

import pandas as pd

def process_dfall_to_trust_circles(input_file="dfall.csv", output_file="trust_circles.csv"):
    """
    Process the raw survey data into trust circles format using pandas,
    grouped by Timepoint as well as demographics.
    """
    # Read
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} rows from {input_file}")

    # Multi-platform ordinal: sum of all TP_Platforms_* columns (0-5)
    platform_cols = ['TP_Platforms_twitter', 'TP_Platforms_instagram', 'TP_Platforms_facebook',
                     'TP_Platforms_tiktok', 'TP_Platforms_other']
    if all(col in df.columns for col in platform_cols):
        df['multi_platform_ord'] = df[platform_cols].sum(axis=1)
        # Drop the individual platform columns after creating the ordinal
        df = df.drop(columns=platform_cols)

    # Institution columns - exclude unwanted patterns
    exclude_patterns = ['TP_Month', 'TP_Which_Platforms', 'TP_Measure', 'TP_Social']
    institution_columns = [
        col for col in df.columns
        if col.startswith('TP_') and not any(pattern in col for pattern in exclude_patterns)
    ]
    print(f"Found institution columns: {institution_columns}")

    # Create ordinal demographic categories
    race_cols = ['Dem_Race_White', 'Dem_Race_Mixed', 'Dem_Race_POC']
    if all(col in df.columns for col in race_cols):
        df['race_ord'] = (df[race_cols] == 1.0).idxmax(axis=1).map({
            'Dem_Race_White': 0,
            'Dem_Race_Mixed': 1, 
            'Dem_Race_POC': 2
        }).fillna(0)
    
    orientation_cols = [
        'Dem_Sexual_Orientation_straight', 
        'Dem_Sexual_Orientation_Bisexual', 
        'Dem_Sexual_Orientation_Gay', 
        'Dem_Sexual_Orientation_other'
    ]
    if all(col in df.columns for col in orientation_cols):
        df['orientation_ord'] = (df[orientation_cols] == 1.0).idxmax(axis=1).map({
            'Dem_Sexual_Orientation_straight': 0,
            'Dem_Sexual_Orientation_Bisexual': 1,
            'Dem_Sexual_Orientation_Gay': 2, 
            'Dem_Sexual_Orientation_other': 3
        }).fillna(0)
    
    gender_cols = ['Dem_Gender_Woman', 'Dem_Gender_Man', 'Dem_Gender_Other']
    if all(col in df.columns for col in gender_cols):
        df['gender_ord'] = (df[gender_cols] == 1.0).idxmax(axis=1).map({
            'Dem_Gender_Woman': 0,
            'Dem_Gender_Man': 1,
            'Dem_Gender_Other': 2
        }).fillna(0)

    demographic_columns = ['gender_ord', 'Dem_Relationship_Status_Single', 'orientation_ord', 'race_ord', 'multi_platform_ord', 'ACES_Compound']
    print(f"Created ordinal demographic columns: {demographic_columns}")
    
    results = []
    
    # 1. Overall average for all institutions, grouped by Timepoint
    if "Timepoint" in df.columns:
        grouped_time = df.groupby("Timepoint")[institution_columns].mean()
        for timepoint, row in grouped_time.iterrows():
            for institution in institution_columns:
                avg_distance = row[institution]
                if pd.notna(avg_distance):
                    results.append({
                        'Timepoint': timepoint,
                        'institution': institution,
                        'distance': avg_distance,
                        'category': 'overall_average',
                        'value': 1.0
                    })
    
    # 2. Process each demographic category within each Timepoint
    for demo_col in demographic_columns:
        if demo_col in df.columns and "Timepoint" in df.columns:
            grouped = df.groupby(["Timepoint", demo_col])[institution_columns].mean()
            for (timepoint, demo_value), row in grouped.iterrows():
                for institution in institution_columns:
                    avg_distance = row[institution]
                    if pd.notna(avg_distance):
                        results.append({
                            'Timepoint': timepoint,
                            'institution': institution,
                            'distance': avg_distance,
                            'category': demo_col,
                            'value': float(demo_value)
                        })
    
    # Convert to DataFrame and sort
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(['Timepoint', 'category', 'value', 'institution'])
    
    # Save to CSV
    results_df.to_csv(output_file, index=False)
    print(f"Saved {len(results_df)} rows to {output_file}")
    
    return results_df.to_dict('records')

def process_individual_level_data(input_file="dfall.csv", output_file="trust_circles_individual.csv", balanced=True):
    """
    Process the raw survey data to individual-level format (not aggregated)
    Each row represents one person's trust rating for one institution
    """
    
    # Read and filter data
    df = pd.read_csv(input_file)

    # Multi-platform ordinal: sum of all TP_Platforms_* columns (0-5)
    platform_cols = ['TP_Platforms_twitter', 'TP_Platforms_instagram', 'TP_Platforms_facebook',
                     'TP_Platforms_tiktok', 'TP_Platforms_other']
    if all(col in df.columns for col in platform_cols):
        df['multi_platform_ord'] = df[platform_cols].sum(axis=1)
        # Drop the individual platform columns after creating the ordinal
        df = df.drop(columns=platform_cols)

    # Institution columns - exclude unwanted patterns
    exclude_patterns = ['TP_Month', 'TP_Which_Platforms', 'TP_Measure', 'TP_Social']
    institution_columns = [col for col in df.columns
                          if col.startswith('TP_')
                          and not any(pattern in col for pattern in exclude_patterns)]

    print(f"Found institution columns: {institution_columns}")

    # Create ordinal demographic categories (same as aggregated version)
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
    
    # Keep the original Dem_Gender_Man column (Woman=0, Man=1)
    # Gender ordinal: Woman=0, Man=1, Other=2
    gender_cols = ['Dem_Gender_Woman', 'Dem_Gender_Man', 'Dem_Gender_Other']
    if all(col in df.columns for col in gender_cols):
        df['gender_ord'] = (df[gender_cols] == 1.0).idxmax(axis=1).map({
            'Dem_Gender_Woman': 0,
            'Dem_Gender_Man': 1,
            'Dem_Gender_Other': 2
        }).fillna(0)

    # Add respondent ID for tracking individuals
    df['respondent_id'] = range(len(df))

    # Melt the dataframe to have one row per person-institution combination
    id_vars = ['respondent_id', 'gender_ord', 'Dem_Relationship_Status_Single', 'orientation_ord', 'race_ord', 'multi_platform_ord', 'ACES_Compound', 'Timepoint']

    # Only include id_vars that exist in the dataframe
    id_vars = [col for col in id_vars if col in df.columns]
    
    melted_df = pd.melt(df, 
                       id_vars=id_vars,
                       value_vars=institution_columns,
                       var_name='institution',
                       value_name='distance')
    
    # Remove rows with missing trust ratings
    melted_df = melted_df.dropna(subset=['distance'])
    
    # Convert distance to numeric
    melted_df['distance'] = pd.to_numeric(melted_df['distance'], errors='coerce')
    melted_df = melted_df.dropna(subset=['distance'])
    
    if balanced == True:
        groups = melted_df.groupby(["Timepoint", "institution", "race_ord"])
        min_size = groups.size().min()

        melted_df = groups.apply(
            lambda g: g.sample(n=min_size, random_state=42, replace=False)
        ).reset_index(drop=True)

    # Save to CSV
    melted_df.to_csv("trust_circles_individual.csv", index=False)
    print(f"Saved {len(melted_df)} individual responses to {output_file}")
    
    return melted_df

def main():
    """Main function"""
    print("Processing dfall.csv to trust_circles.csv...")
    
    # Process aggregated data
    aggregated_result = process_dfall_to_trust_circles()
    
    if aggregated_result is not None:
        print("\\nFirst few rows of aggregated output:")
        for i, row in enumerate(aggregated_result[:10]):
            print(f"{i+1}: {row}")
        
        categories = sorted(set(row['category'] for row in aggregated_result))
        institutions = sorted(set(row['institution'] for row in aggregated_result))
        
        print(f"\\nCategories found: {categories}")
        print(f"Institutions found: {institutions}")
    
    print("\\n" + "="*50)
    print("Processing individual-level data...")
    
    # Process individual-level data
    individual_result = process_individual_level_data(balanced=False)
    
    if individual_result is not None:
        print(f"\nIndividual data shape: {individual_result.shape}")
        print("\nFirst few rows of individual data:")
        print(individual_result.head())

if __name__ == "__main__":
    main()