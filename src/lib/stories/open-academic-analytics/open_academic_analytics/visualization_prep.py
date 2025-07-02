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
    deps=["researcher_career_profiles"],
    group_name="visualization_prep",
    description="📊 Clean and prepare publication data for analysis dashboard"
)
def publication_dataset(duckdb: DuckDBResource):
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

@dg.asset(
    deps=["researcher_career_profiles"],
    group_name="visualization_prep",
    description="👩‍🎓 Prepare researcher career data for timeline and profile visualizations"
)
def researcher_dataset(duckdb: DuckDBResource):
    """Process author career data for visualization with age standardization"""
    
    print("🚀 Starting researcher dataset preparation...")
    
    with duckdb.get_connection() as conn:
        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database")
        
        # Load author data from database
        print("Querying author data from database...")
        df = db_exporter.con.sql("SELECT * FROM author").fetchdf()
        print(f"Retrieved {len(df)} author records")
        
        # Basic data quality validation
        print("Validating data quality...")
        total_records = len(df)
        missing_age = df.author_age.isna().sum()
        missing_aid = df.aid.isna().sum()
        
        print(f"Data Quality Report:")
        print(f"  - Total records: {total_records}")
        print(f"  - Missing author_age: {missing_age} ({missing_age/total_records*100:.1f}%)")
        print(f"  - Missing aid: {missing_aid} ({missing_aid/total_records*100:.1f}%)")
        
        if not df.author_age.isna().all():
            age_min = float(df.author_age.min())
            age_max = float(df.author_age.max())
            age_mean = float(df.author_age.mean())
            print(f"  - Age range: {age_min:.0f} to {age_max:.0f} years")
            print(f"  - Mean age: {age_mean:.1f} years")
        
        # Create standardized age representation for timeline visualization
        print("Creating standardized age representation for timeline visualization...")
        
        try:
            # Generate random month and day components for smooth animation
            months = np.char.zfill(
                np.random.randint(1, 13, len(df)).astype(str), 2
            )
            days = np.char.zfill(
                np.random.randint(1, 29, len(df)).astype(str), 2  # Avoid leap year issues
            )
            
            # Create age_std format: "1{age:03d}-{month:02d}-{day:02d}"
            # This enables smooth timeline animations in the dashboard
            df["age_std"] = (
                "1" + 
                df.author_age.astype(str).str.replace(".0", "").map(lambda x: x.zfill(3)) + 
                "-" + months + "-" + days
            )
            
            print("Successfully created age_std column using vectorized approach")
            
        except Exception as e:
            print(f"Error in vectorized approach: {e}")
            print("Falling back to row-by-row processing...")
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
        output_path = config.data_processed_path / config.author_output_file
        print(f"Saving {len(df)} processed author records to {output_path}")
        df.to_parquet(output_path)
        
        print("✅ Researcher dataset preparation completed!")
        print(f"Total authors processed: {len(df)}")
        print(f"Unique author IDs: {df.aid.nunique()}")
        
        if 'institution' in df.columns:
            print(f"Unique institutions: {df.institution.nunique()}")
            
        if 'pub_year' in df.columns:
            year_min = df.pub_year.min()
            year_max = df.pub_year.max()
            print(f"Year range: {year_min}-{year_max}")
        
        print(f"Records with age_std: {valid_age_std}")
        
        return MaterializeResult(
            metadata={
                "researcher_records": MetadataValue.int(len(df)),
                "unique_researchers": MetadataValue.int(int(df.aid.nunique())),
                "records_with_age_std": MetadataValue.int(int(valid_age_std)),
                "institutions": MetadataValue.int(int(df.institution.nunique()) if 'institution' in df.columns else 0),
                "output_file": MetadataValue.path(str(output_path)),
                "visualization_feature": MetadataValue.md(
                    "**Age standardization** enables smooth timeline animations showing "
                    "career progression and collaboration patterns over time."
                ),
                "research_value": MetadataValue.md(
                    "**Researcher profile dataset** for career stage analysis and "
                    "timeline visualization of academic progression."
                )
            }
        )

@dg.asset(
    deps=["collaboration_network"],
    group_name="visualization_prep",
    description="🌐 Prepare collaboration data for interactive network visualization"  
)
def collaboration_dataset(duckdb: DuckDBResource):
    """Process collaboration data for network visualization with age buckets and timing analysis"""
    
    print("🚀 Starting collaboration dataset preparation...")
    
    with duckdb.get_connection() as conn:
        db_exporter = DatabaseExporterAdapter(conn)
        
        # Check if we have collaboration data
        coauthor_count = db_exporter.con.execute("SELECT COUNT(*) FROM coauthor2").fetchone()[0]
        print(f"Found {coauthor_count} coauthor records")
        
        if coauthor_count == 0:
            print("❌ No coauthor data found")
            return MaterializeResult(
                metadata={"status": MetadataValue.text("No collaboration data available")}
            )
        
        # Load coauthor data with author info
        print("Loading collaboration data with researcher profiles...")
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
        print(f"Retrieved {len(df)} collaboration relationships")
        
        if len(df) == 0:
            print("❌ No data after JOIN")
            return MaterializeResult(
                metadata={"status": MetadataValue.text("No data after JOIN - check data pipeline")}
            )
        
        # Filter valid records
        initial_count = len(df)
        df = df[~df.author_age.isna()].reset_index(drop=True)
        df['author_age'] = df.author_age.astype(int)
        print(f"After filtering for valid author ages: {len(df)} records ({initial_count - len(df)} removed)")
        
        # Correct publication years (remove pre-1950 anomalies)
        print("Correcting publication year anomalies...")
        initial_invalid = df.coauth_min_year.lt(1950).sum()
        df['coauth_min_year'] = df['coauth_min_year'].where(df['coauth_min_year'] >= 1950)
        df['coauth_age'] = df.pub_year - df.coauth_min_year
        df['age_diff'] = df.coauth_age - df.author_age
        final_invalid = df.coauth_min_year.isna().sum()
        print(f"  - Corrected {initial_invalid} invalid years, {final_invalid} remain missing")
        
        # Create age buckets for collaboration analysis
        print("Creating age difference buckets...")
        age_diff_values = df.age_diff.to_numpy()
        categories = np.empty(age_diff_values.shape, dtype=object)
        
        categories[age_diff_values < -15] = "much_younger"
        categories[(age_diff_values >= -15) & (age_diff_values < -7)] = "younger"
        categories[(age_diff_values >= -7) & (age_diff_values < 7)] = "same_age"
        categories[(age_diff_values >= 7) & (age_diff_values < 15)] = "older"
        categories[age_diff_values >= 15] = "much_older"
        
        df['age_bucket'] = categories
        
        # Create age standardization for timeline visualization
        print("Creating age standardization for timeline...")
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
        
        # Generate summary statistics (convert numpy types to Python types)
        age_bucket_dist = df['age_bucket'].value_counts().to_dict()
        collab_type_dist = df['acquaintance'].value_counts().to_dict() if 'acquaintance' in df.columns else {}
        year_range = f"{int(df.pub_year.min())}-{int(df.pub_year.max())}"
        unique_ego_authors = int(df.aid.nunique())
        unique_coauthors = int(df.coauth_aid.nunique())
        
        # Save processed data
        output_path = config.data_processed_path / config.coauthor_output_file
        print(f"Saving {len(df)} collaboration records to {output_path}")
        df.to_parquet(output_path)
        
        print(f"✅ Collaboration dataset preparation completed!")
        print(f"Total relationships processed: {len(df)}")
        print(f"Unique ego authors: {unique_ego_authors}")
        print(f"Unique coauthors: {unique_coauthors}")
        print(f"Year range: {year_range}")
        print(f"Age bucket distribution: {age_bucket_dist}")
        
        return MaterializeResult(
            metadata={
                "collaboration_relationships": MetadataValue.int(len(df)),
                "unique_ego_authors": MetadataValue.int(unique_ego_authors),
                "unique_coauthors": MetadataValue.int(unique_coauthors),
                "year_range": MetadataValue.text(year_range),
                "age_bucket_distribution": MetadataValue.json(age_bucket_dist),
                "collaboration_types": MetadataValue.json(collab_type_dist),
                "output_file": MetadataValue.path(str(output_path)),
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