"""
visualization_prep.py

Stage 3: Prepare datasets for interactive dashboards and analysis
"""
import numpy as np
import pandas as pd
import dagster as dg
from dagster import MaterializeResult, MetadataValue
from dagster_duckdb import DuckDBResource

from config import config
from modules.database_adapter import DatabaseExporterAdapter

@dg.asset(
    deps=["author"],
    group_name="export",
    description="📊 Clean and prepare publication data for analysis dashboard"
)
def paper(duckdb: DuckDBResource):
    """Process papers for visualization - filtering, deduplication, and enrichment"""
    
    print("🚀 Starting publication dataset preparation...")
    
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
        initial_count = len(df)
        df = df[~df.title.isna()]
        print(f"After removing papers without titles: {len(df)} papers ({initial_count - len(df)} removed)")

        # Deduplicate papers
        df = df.sort_values("pub_date", ascending=False).reset_index(drop=True)
        df['title'] = df.title.str.lower()
        before_dedup = len(df)
        df = df[~df[['ego_aid', 'title']].duplicated()]
        print(f"After deduplication: {len(df)} papers ({before_dedup - len(df)} duplicates removed)")

        # Filter by accepted work types
        print(f"Filtering by work types: {config.accepted_work_types}")
        before_work_filter = len(df)
        df = df[df.work_type.isin(config.accepted_work_types)]
        print(f"After filtering by work type: {len(df)} papers ({before_work_filter - len(df)} filtered out)")

        # Filter out mislabeled articles
        print("Filtering out mislabeled articles...")
        initial_count = len(df)
        
        for pattern in config.filter_title_patterns:
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
        
        # Generate summary statistics (convert numpy types to Python types)
        work_type_dist = df.work_type.value_counts().to_dict()
        year_range = f"{int(df.pub_year.min())}-{int(df.pub_year.max())}"
        avg_coauthors = float(df.nb_coauthors.mean())
        unique_authors = int(df.ego_aid.nunique())
        
        # Save processed data
        output_path = config.data_processed_path / config.paper_output_file
        print(f"Saving {len(df)} processed papers to {output_path}")
        df.to_parquet(output_path)
        
        print("✅ Publication dataset preparation completed!")
        print(f"Final paper count: {len(df)}")
        print(f"Unique authors: {unique_authors}")
        print(f"Year range: {year_range}")
        print(f"Work types: {work_type_dist}")
        print(f"Average coauthors per paper: {avg_coauthors:.1f}")
        
        return MaterializeResult(
            metadata={
                "papers_processed": MetadataValue.int(len(df)),
                "unique_authors": MetadataValue.int(unique_authors),
                "year_range": MetadataValue.text(year_range),
                "work_type_distribution": MetadataValue.json(work_type_dist),
                "avg_coauthors_per_paper": MetadataValue.float(avg_coauthors),
                "output_file": MetadataValue.path(str(output_path)),
                "dashboard_ready": MetadataValue.bool(True),
                "research_value": MetadataValue.md(
                    "**Publication timeline dataset** ready for dashboard visualization. "
                    "Shows researcher productivity, collaboration breadth, and career progression."
                )
            }
        )