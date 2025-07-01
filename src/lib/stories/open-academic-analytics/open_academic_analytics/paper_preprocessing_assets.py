"""
Simplified paper_preprocessing_assets.py
"""
import pandas as pd
import dagster as dg
from dagster_duckdb import DuckDBResource

from config import config
from modules.database_adapter import DatabaseExporterAdapter

@dg.asset(deps=["timeline_paper_main"])
def paper_preprocessing(duckdb: DuckDBResource):
    """Process papers for visualization"""
    
    print("🚀 Starting paper preprocessing...")
    
    with duckdb.get_connection() as conn:
        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database")
        
        # Query database for papers with author metadata
        print("Querying database for papers...")
        query = """
            SELECT p.ego_aid, a.display_name as name, p.pub_date, p.pub_year, p.title,
                   p.cited_by_count, p.doi, p.wid, p.authors, p.work_type, 
                   a.author_age as ego_age
            FROM paper p
            LEFT JOIN author a ON p.ego_aid = a.aid AND p.pub_year = a.pub_year
        """
        
        df = db_exporter.con.sql(query).fetchdf()
        print(f"Retrieved {len(df)} papers from database")

        # Filter papers without titles
        df = df[~df.title.isna()]
        print(f"After removing papers without titles: {len(df)} papers")

        # Deduplicate papers
        df = df.sort_values("pub_date", ascending=False).reset_index(drop=True)
        df['title'] = df.title.str.lower()
        df = df[~df[['ego_aid', 'title']].duplicated()]
        print(f"After deduplication: {len(df)} papers")

        # Filter by work types
        print(f"Filtering by work types: {config.ACCEPTED_WORK_TYPES}")
        df = df[df.work_type.isin(config.ACCEPTED_WORK_TYPES)]
        print(f"After filtering by work type: {len(df)} papers")

        # Filter out mislabeled articles
        print("Filtering out mislabeled articles...")
        initial_count = len(df)
        
        for pattern in config.FILTER_TITLE_PATTERNS:
            before_count = len(df)
            df = df[~df.title.str.contains(pattern, case=False, na=False)]
            filtered = before_count - len(df)
            if filtered > 0:
                print(f"  - Filtered {filtered} papers matching '{pattern}'")
        
        total_filtered = initial_count - len(df)
        print(f"  - Total mislabeled articles removed: {total_filtered}")

        # Calculate coauthor counts
        print("Computing number of coauthors...")
        df['nb_coauthors'] = df.authors.apply(
            lambda x: len(x.split(", ")) if isinstance(x, str) else 0
        )
        
        # Save processed data
        output_path = config.DATA_PROCESSED_DIR / config.PAPER_OUTPUT_FILE
        print(f"Saving {len(df)} processed papers to {output_path}")
        df.to_parquet(output_path)
        
        print("✅ Paper preprocessing completed!")
        print(f"Final paper count: {len(df)}")
        print(f"Unique authors: {df.ego_aid.nunique()}")
        print(f"Year range: {df.pub_year.min()}-{df.pub_year.max()}")
        print(f"Work types: {df.work_type.value_counts().to_dict()}")
        print(f"Average coauthors per paper: {df.nb_coauthors.mean():.1f}")
        
        return f"Processed {len(df)} papers, saved to {output_path}"