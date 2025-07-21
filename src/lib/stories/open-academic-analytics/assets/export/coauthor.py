"""
visualization_prep.py

Stage 3: Prepare datasets for interactive dashboards and analysis
"""
import numpy as np
import pandas as pd
import dagster as dg
from dagster import MaterializeResult, MetadataValue
import duckdb

from config import config
from shared.utils.data_transforms import create_age_standardization

def filter_valid_author_ages(df):
    """Filter records with valid author ages"""
    initial_count = len(df)
    df_filtered = df[~df.author_age.isna()].reset_index(drop=True)
    df_filtered['author_age'] = df_filtered.author_age.astype(int)
    print(f"After filtering for valid author ages: {len(df_filtered)} records ({initial_count - len(df_filtered)} removed)")
    return df_filtered

def correct_publication_years(df):
    """Correct publication year anomalies and recalculate age differences"""
    print("Correcting publication year anomalies...")
    df_corrected = df.copy()
    
    initial_invalid = df_corrected.coauth_min_year.lt(1950).sum()
    df_corrected['coauth_min_year'] = df_corrected['coauth_min_year'].where(df_corrected['coauth_min_year'] >= 1950)
    df_corrected['coauth_age'] = df_corrected.pub_year - df_corrected.coauth_min_year
    df_corrected['age_diff'] = df_corrected.coauth_age - df_corrected.author_age
    
    final_invalid = df_corrected.coauth_min_year.isna().sum()
    print(f"  - Corrected {initial_invalid} invalid years, {final_invalid} remain missing")
    return df_corrected

def create_age_categories(df):
    """Create age difference categories that match frontend expectations exactly"""
    print("Creating age difference categories...")
    df_with_categories = df.copy()
    
    age_diff_values = df_with_categories.age_diff.to_numpy()
    categories = np.empty(age_diff_values.shape, dtype=object)
    
    # Match frontend logic exactly: default 'same', then check > 7 and < -7
    categories[:] = 'same'  # Default all to 'same'
    categories[age_diff_values > 7] = 'older'
    categories[age_diff_values < -7] = 'younger'
    
    df_with_categories['age_category'] = categories
    print(f"  - Added age_category column (same/older/younger)")
    return df_with_categories

def add_collaboration_intensity(df):
    """Add categorical collaboration levels for better frontend scaling"""
    df_with_intensity = df.copy()
    
    # Create quartile-based categories
    collab_counts = df_with_intensity['all_times_collabo'].fillna(1)
    quartiles = collab_counts.quantile([0.25, 0.5, 0.75])
    
    conditions = [
        collab_counts <= quartiles[0.25],
        (collab_counts > quartiles[0.25]) & (collab_counts <= quartiles[0.5]),
        (collab_counts > quartiles[0.5]) & (collab_counts <= quartiles[0.75]),
        collab_counts > quartiles[0.75]
    ]
    categories = ['low', 'medium', 'high', 'very_high']
    
    df_with_intensity['collaboration_intensity'] = np.select(conditions, categories, default='low')
    return df_with_intensity

def normalize_institutions(df, institution_col='institution'):
    """Clean and normalize institution names"""
    df_normalized = df.copy()
    
    # Basic cleaning
    df_normalized[f'{institution_col}_normalized'] = (
        df_normalized[institution_col]
        .fillna('Unknown')
        .str.strip()
        .str.replace(r'\s+', ' ', regex=True)  # Multiple spaces to single
        .str.replace(r'[^\w\s-]', '', regex=True)  # Remove special chars except hyphens
        .str.title()  # Consistent capitalization
    )
    
    return df_normalized

def highlight_shared_institutions(df):
    """Add shared institutions indicator"""
    df_with_shared = df.copy()
    df_with_shared['shared_institutions'] = np.where(
        df_with_shared.institution == df_with_shared.coauth_institution, 
        df_with_shared.institution, 
        None
    )
    return df_with_shared

def normalize_coauthor_institutions(df):
    """Clean and normalize institution names for coauthor data"""
    print("Normalizing coauthor institution names...")
    df_normalized = df.copy()
    
    # Normalize main institution
    df_normalized['institution_normalized'] = (
        df_normalized['institution']
        .fillna('Unknown')
        .str.strip()
        .str.replace(r'\s+', ' ', regex=True)  # Multiple spaces to single
        .str.replace(r'[^\w\s\-\.]', '', regex=True)  # Keep letters, numbers, spaces, hyphens, dots
        .str.title()  # Consistent capitalization
    )
    
    # Normalize coauthor institution
    df_normalized['coauth_institution_normalized'] = (
        df_normalized['coauth_institution']
        .fillna('Unknown')
        .str.strip()
        .str.replace(r'\s+', ' ', regex=True)
        .str.replace(r'[^\w\s\-\.]', '', regex=True)
        .str.title()
    )
    
    # Update shared_institutions with normalized names
    df_normalized['shared_institutions_normalized'] = np.where(
        df_normalized['institution_normalized'] == df_normalized['coauth_institution_normalized'],
        df_normalized['institution_normalized'],
        None
    )
    
    print(f"  - Added institution_normalized, coauth_institution_normalized, shared_institutions_normalized")
    return df_normalized



@dg.asset(
    deps=["collaboration_network", "author", "paper"],
    group_name="export",
    description="🌐 Prepare collaboration data for interactive network visualization"  
)
def coauthor():
    """Process collaboration data for network visualization with age buckets and timing analysis"""
    
    """Load collaboration and author data and perform the join"""
    print("🚀 Starting collaboration dataset preparation...")
    
    # HRDAG: Load from intermediary files
    collaborations_file = config.data_clean_path / config.coauthor_output_file
    authors_file = config.data_export_path / config.author_output_file
    paper_file = config.data_export_path / config.paper_output_file
    
    print(f"📖 Loading collaboration data from {collaborations_file}")
    df_coauth = pd.read_parquet(collaborations_file)
    
    print(f"📚 Loading author profiles from {authors_file}")
    df_authors = pd.read_parquet(authors_file)
    
    print(f"📚 Loading author profiles from {authors_file}")
    df_pap = pd.read_parquet(paper_file)
    
    # Check if we have collaboration data
    coauthor_count = duckdb.sql("SELECT COUNT(*) FROM df_coauth").fetchone()[0]
    print(f"Found {coauthor_count} coauthor records")
    
    if coauthor_count == 0:
        print("❌ No coauthor data found")
        return None
    
    ####################################
    #                                  #
    #        MERGE TABLES              #
    #                                  #
    ####################################

    print("Loading collaboration data with researcher profiles...")
    query = """
            -- Main SELECT: Return collaboration data with author details and age differences
                SELECT 
                    -- Publication timing information
                    c.pub_year, 
                    c.pub_date::VARCHAR as pub_date,
                    
                    -- Ego author (main author) information
                    ego_a.aid, 
                    ego_a.institution, 
                    ego_a.display_name as name, 
                    ego_a.author_age, 
                    ego_a.first_pub_year, 
                    ego_a.last_pub_year,
                    
                    -- Collaboration metrics
                    c.yearly_collabo,           -- Collaborations in this year
                    c.all_times_collabo,        -- Total lifetime collaborations
                    c.acquaintance,             -- Acquaintance level/familiarity
                    c.shared_institutions,      -- Number of shared institutions
                    
                    -- Co-author information
                    coauth.aid as coauth_aid, 
                    coauth.display_name as coauth_name, 
                    coauth.institution as coauth_institution, 
                    coauth.author_age as coauth_age, 
                    coauth.first_pub_year as coauth_min_year,
                    
                    -- Calculated field: Age difference between ego author and co-author
                    (coauth.author_age - ego_a.author_age) AS age_diff

                FROM 
                    -- Base table: collaboration data
                    df_coauth c

                -- Join to get co-author details (LEFT JOIN keeps all collaborations even if co-author details missing)
                LEFT JOIN 
                    df_authors coauth ON c.coauthor_aid = coauth.aid 
                                    AND c.pub_year = coauth.pub_year

                -- Join to get ego author details (LEFT JOIN keeps all collaborations even if ego author details missing)  
                LEFT JOIN 
                    df_authors ego_a ON c.ego_aid = ego_a.aid 
                                    AND c.pub_year = ego_a.pub_year

                -- FILTER: Only keep collaborations where the ego author actually has papers in df_pap for that year
                -- This ensures we're only analyzing collaborations for authors who were actually publishing
                WHERE EXISTS (
                    SELECT 1 
                    FROM df_pap p 
                    WHERE p.ego_aid = c.ego_aid     -- Same ego author
                    AND p.pub_year = c.pub_year     -- Same publication year
                )

                -- Sort results chronologically
                ORDER BY c.pub_year
    """
    
    df = duckdb.sql(query).df()
    
    if df is None:
        return MaterializeResult(
            metadata={"status": MetadataValue.text("No collaboration data available")}
        )
    

    ####################################
    #                                  #
    #            FILTERS               #
    #                                  #
    ####################################

    # Apply all transformations using pipe
    df_processed = (df
                .pipe(filter_valid_author_ages)
                .pipe(correct_publication_years)
                .pipe(create_age_categories)           # Creates 'age_category' column
                .pipe(add_collaboration_intensity)     # Creates 'collaboration_intensity' column  
                .pipe(normalize_coauthor_institutions) # Creates normalized institution columns
                .pipe(create_age_standardization)
                .pipe(highlight_shared_institutions)
            )
    
    # Generate summary statistics
    age_bucket_dist = df_processed['age_category'].value_counts().to_dict()
    year_range = f"{int(df_processed.pub_year.min())}-{int(df_processed.pub_year.max())}"
    unique_ego_authors = int(df_processed.aid.nunique())
    unique_coauthors = int(df_processed.coauth_aid.nunique())
    
    # HRDAG: Save processed data
    output_file = config.data_export_path / config.coauthor_output_file
    print(f"💾 Saving {len(df_processed)} collaboration records to {output_file}")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df_processed.to_parquet(output_file)
    
    print(f"✅ Collaboration dataset preparation completed!")
    print(f"Total relationships processed: {len(df_processed)}")
    print(f"Unique ego authors: {unique_ego_authors}")
    print(f"Unique coauthors: {unique_coauthors}")
    print(f"Year range: {year_range}")
    print(f"Age bucket distribution: {age_bucket_dist}")
    
    return MaterializeResult(
                metadata={
                    "unique_ego_authors": MetadataValue.int(unique_ego_authors),
                    "year_range": MetadataValue.text(year_range),
                    "input_files": MetadataValue.json({
                        "collaborations": str(config.data_clean_path / config.coauthor_output_file),
                        "authors": str(config.data_export_path / config.author_output_file)
                    }),
                    "output_file": MetadataValue.path(str(output_file)),
                    "PRIMARY KEY": MetadataValue.md("Tidy on (ego_aid, coauthor_aid, pub_year): Data is aggregated by the number of yearly collaborations between ego aid and each of its coauthor."),
                    "dependencies": MetadataValue.md("""
- **collaboration_network**: Raw coauthor data source  
- **author**: Augments coauthor data with ego information  
- **paper**: Visualizes coauthors from filtered papers
                    """)
                }
            )