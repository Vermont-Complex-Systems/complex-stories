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

def create_age_buckets(df):
    """Create age difference buckets for collaboration analysis"""
    print("Creating age difference buckets...")
    df_with_buckets = df.copy()
    
    age_diff_values = df_with_buckets.age_diff.to_numpy()
    categories = np.empty(age_diff_values.shape, dtype=object)
    
    categories[age_diff_values < -15] = "much_younger"
    categories[(age_diff_values >= -15) & (age_diff_values < -7)] = "younger"
    categories[(age_diff_values >= -7) & (age_diff_values < 7)] = "same_age"
    categories[(age_diff_values >= 7) & (age_diff_values < 15)] = "older"
    categories[age_diff_values >= 15] = "much_older"
    
    df_with_buckets['age_bucket'] = categories
    return df_with_buckets

def create_age_standardization(df):
    """Create age standardization for timeline visualization"""
    print("Creating age standardization for timeline...")
    df_with_std = df.copy()
    
    try:
        df_with_std["age_std"] = (
            "1" + 
            df_with_std.author_age.astype(str).str.zfill(3) + 
            "-" + 
            df_with_std.pub_date.map(lambda x: "-".join(str(x).split("-")[-2:]) if isinstance(x, str) else "01-01")
        )
        # Handle leap year
        df_with_std["age_std"] = df_with_std.age_std.map(
            lambda x: x.replace("29", "28") if x and x.endswith("29") else x
        )
    except Exception as e:
        print(f"Error creating age_std: {e}")
        df_with_std["age_std"] = None
    
    return df_with_std

def highlight_shared_institutions(df):
    """Add shared institutions indicator"""
    df_with_shared = df.copy()
    df_with_shared['shared_institutions'] = np.where(
        df_with_shared.institution == df_with_shared.coauth_institution, 
        df_with_shared.institution, 
        None
    )
    return df_with_shared

def load_and_join_collaboration_data():
    """Load collaboration and author data and perform the join"""
    print("🚀 Starting collaboration dataset preparation...")
    
    # HRDAG: Load from intermediary files
    collaborations_file = config.data_clean_path / config.coauthor_output_file
    authors_file = config.data_raw_path / config.author_output_file
    
    print(f"📖 Loading collaboration data from {collaborations_file}")
    df_coauth = pd.read_parquet(collaborations_file)
    
    print(f"📚 Loading author profiles from {authors_file}")
    df_authors = pd.read_parquet(authors_file)
    
    # Check if we have collaboration data
    coauthor_count = duckdb.sql("SELECT COUNT(*) FROM df_coauth").fetchone()[0]
    print(f"Found {coauthor_count} coauthor records")
    
    if coauthor_count == 0:
        print("❌ No coauthor data found")
        return None
    
    # Use DuckDB to do the complex JOIN - exactly like the original SQL
    print("Loading collaboration data with researcher profiles...")
    df = duckdb.sql("""
        SELECT 
            c.pub_year, c.pub_date::VARCHAR as pub_date,
            ego_a.aid, ego_a.institution, ego_a.display_name as name, 
            ego_a.author_age, ego_a.first_pub_year, ego_a.last_pub_year,
            c.yearly_collabo, c.all_times_collabo, c.acquaintance, c.shared_institutions,
            coauth.aid as coauth_aid, coauth.display_name as coauth_name, coauth.institution as coauth_institution, 
            coauth.author_age as coauth_age, coauth.first_pub_year as coauth_min_year,
            (coauth.author_age-ego_a.author_age) AS age_diff
        FROM 
            df_coauth c
        LEFT JOIN 
            df_authors coauth ON c.coauthor_aid = coauth.aid AND c.pub_year = coauth.pub_year
        LEFT JOIN 
            df_authors ego_a ON c.ego_aid = ego_a.aid AND c.pub_year = ego_a.pub_year
        WHERE 
            c.pub_year < 2024
        ORDER BY c.pub_year
    """).df()
    
    print(f"Retrieved {len(df)} collaboration relationships")
    
    if len(df) == 0:
        print("❌ No data after JOIN")
        return None
    
    return df

@dg.asset(
    deps=["collaboration_network", "coauthor_cache"],
    group_name="export",
    description="🌐 Prepare collaboration data for interactive network visualization"  
)
def coauthor():
    """Process collaboration data for network visualization with age buckets and timing analysis"""
    
    # Load and join data
    df = load_and_join_collaboration_data()
    
    if df is None:
        return MaterializeResult(
            metadata={"status": MetadataValue.text("No collaboration data available")}
        )
    
    # Apply all transformations using pipe
    df_processed = (df
                    .pipe(filter_valid_author_ages)
                    .pipe(correct_publication_years)
                    .pipe(create_age_buckets)
                    .pipe(create_age_standardization)
                    .pipe(highlight_shared_institutions)
                   )
    
    # Generate summary statistics
    age_bucket_dist = df_processed['age_bucket'].value_counts().to_dict()
    collab_type_dist = df_processed['acquaintance'].value_counts().to_dict() if 'acquaintance' in df_processed.columns else {}
    year_range = f"{int(df_processed.pub_year.min())}-{int(df_processed.pub_year.max())}"
    unique_ego_authors = int(df_processed.aid.nunique())
    unique_coauthors = int(df_processed.coauth_aid.nunique())
    
    # HRDAG: Save processed data
    output_file = config.data_processed_path / config.coauthor_output_file
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
            "collaboration_relationships": MetadataValue.int(len(df_processed)),
            "unique_ego_authors": MetadataValue.int(unique_ego_authors),
            "unique_coauthors": MetadataValue.int(unique_coauthors),
            "year_range": MetadataValue.text(year_range),
            "age_bucket_distribution": MetadataValue.json(age_bucket_dist),
            "collaboration_types": MetadataValue.json(collab_type_dist),
            "input_collaborations_file": MetadataValue.path(str(config.data_clean_path / config.coauthor_output_file)),
            "input_authors_file": MetadataValue.path(str(config.data_raw_path / config.author_output_file)),
            "output_file": MetadataValue.path(str(output_file)),
            "dashboard_ready": MetadataValue.bool(True),
            "visualization_features": MetadataValue.json({
                "network_analysis": "Interactive collaboration network",
                "timeline_view": "Career-stage collaboration evolution", 
                "age_analysis": "Mentorship and peer collaboration patterns",
                "institutional_effects": "Role of shared affiliations"
            }),
            "research_value": MetadataValue.md(
                "**Final collaboration network dataset** ready for interactive visualization. "
                "Enables exploration of mentorship patterns, career-stage effects, and "
                "institutional collaboration networks."
            )
        }
    )