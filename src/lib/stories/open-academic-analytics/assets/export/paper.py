"""
visualization_prep.py

Stage 3: Prepare datasets for interactive dashboards and analysis
"""
import pandas as pd
import dagster as dg
from dagster import MaterializeResult, MetadataValue
import duckdb

from config import config

def filter_no_title(df):
    """Remove papers without titles"""
    initial_count = len(df)
    df_filtered = df[~df.title.isna()]
    print(f"After removing papers without titles: {len(df_filtered)} papers ({initial_count - len(df_filtered)} removed)")
    return df_filtered

def deduplicate_papers(df):
    """Remove duplicate papers based on ego_aid and title"""
    before_dedup = len(df)
    df_dedup = df[~df[['ego_aid', 'title']].duplicated()]
    print(f"After deduplication: {len(df_dedup)} papers ({before_dedup - len(df_dedup)} duplicates removed)")
    return df_dedup

def filter_work_type(df):
    """Filter by accepted work types"""
    print(f"Filtering by work types: {config.accepted_work_types}")
    before_work_filter = len(df)
    df_filtered = df[df.work_type.isin(config.accepted_work_types)]
    print(f"After filtering by work type: {len(df_filtered)} papers ({before_work_filter - len(df_filtered)} filtered out)")
    return df_filtered

def filter_mislabeled_title(df):
    """Filter out mislabeled articles based on title patterns"""
    print("Filtering out mislabeled articles...")
    initial_count = len(df)
    df_filtered = df.copy()
    
    for pattern in config.filter_title_patterns:
        before_count = len(df_filtered)
        df_filtered = df_filtered[~df_filtered.title.str.contains(pattern, case=False, na=False)]
        filtered = before_count - len(df_filtered)
        if filtered > 0:
            print(f"  - Filtered {filtered} papers matching '{pattern}'")
    
    total_filtered = initial_count - len(df_filtered)
    print(f"  - Total mislabeled articles removed: {total_filtered}")
    return df_filtered

def calculate_number_authors(df):
    """Add column for number of coauthors"""
    print("Computing number of coauthors...")
    df_with_coauthors = df.copy()
    df_with_coauthors['nb_coauthors'] = df_with_coauthors.authors.apply(
        lambda x: len(x.split(", ")) if isinstance(x, str) else 0
    )
    return df_with_coauthors

def prepare_for_deduplication(df):
    """Sort by publication date and lowercase titles for deduplication"""
    return (df
            .sort_values("pub_date", ascending=False)
            .reset_index(drop=True)
            .assign(title=lambda x: x.title.str.lower())
           )

def load_and_join_data():
    """Load papers and authors data and perform the join"""
    print("🚀 Starting publication dataset preparation...")
    
    # HRDAG: Load from intermediary files  
    papers_file = config.data_raw_path / config.paper_output_file
    authors_file = config.data_raw_path / config.author_output_file
    
    print(f"📖 Loading papers from {papers_file}")
    df_papers = pd.read_parquet(papers_file)
    
    print(f"📚 Loading author profiles from {authors_file}")
    df_authors = pd.read_parquet(authors_file)
    
    # Use DuckDB to do the JOIN - exactly like the original SQL
    print("Querying papers with author metadata...")
    df = duckdb.sql("""
        SELECT p.ego_aid, a.display_name as name, p.pub_date, p.pub_year, p.title,
               p.cited_by_count, p.doi, p.wid, p.authors, p.work_type, 
               a.author_age as ego_age
        FROM df_papers p
        LEFT JOIN df_authors a ON p.ego_aid = a.aid AND p.pub_year = a.pub_year
    """).df()
    
    print(f"Retrieved {len(df)} papers")
    return df

@dg.asset(
    deps=["academic_publications", "author"],
    group_name="export",
    description="📊 Clean and prepare publication data for analysis dashboard"
)
def paper():
    """Process papers for visualization - filtering, deduplication, and enrichment"""
    
    # Load and join data
    df = load_and_join_data()
    
    # Apply all transformations using pipe
    df_processed = (df
                    .pipe(filter_no_title)
                    .pipe(prepare_for_deduplication)
                    .pipe(deduplicate_papers)
                    .pipe(filter_work_type)
                    .pipe(filter_mislabeled_title)
                    .pipe(calculate_number_authors)
                   )
    
    # Generate summary statistics
    work_type_dist = df_processed.work_type.value_counts().to_dict()
    year_range = f"{int(df_processed.pub_year.min())}-{int(df_processed.pub_year.max())}"
    avg_coauthors = float(df_processed.nb_coauthors.mean())
    unique_authors = int(df_processed.ego_aid.nunique())
    
    # HRDAG: Save processed data
    output_file = config.data_processed_path / config.paper_output_file
    print(f"💾 Saving {len(df_processed)} processed papers to {output_file}")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df_processed.to_parquet(output_file)
    
    print("✅ Publication dataset preparation completed!")
    print(f"Final paper count: {len(df_processed)}")
    print(f"Unique authors: {unique_authors}")
    print(f"Year range: {year_range}")
    print(f"Work types: {work_type_dist}")
    print(f"Average coauthors per paper: {avg_coauthors:.1f}")
    
    return MaterializeResult(
        metadata={
            "papers_processed": MetadataValue.int(len(df_processed)),
            "unique_authors": MetadataValue.int(unique_authors),
            "year_range": MetadataValue.text(year_range),
            "work_type_distribution": MetadataValue.json(work_type_dist),
            "avg_coauthors_per_paper": MetadataValue.float(avg_coauthors),
            "input_papers_file": MetadataValue.path(str(config.data_raw_path / config.paper_output_file)),
            "input_authors_file": MetadataValue.path(str(config.data_raw_path / config.author_output_file)),
            "output_file": MetadataValue.path(str(output_file)),
            "dashboard_ready": MetadataValue.bool(True),
            "research_value": MetadataValue.md(
                "**Publication timeline dataset** ready for dashboard visualization. "
                "Shows researcher productivity, collaboration breadth, and career progression."
            )
        }
    )