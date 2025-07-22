"""
research_analysis.py

Stage 2: Core research analysis - career profiles and collaboration networks (CLEAN VERSION)
"""
import pandas as pd
from datetime import datetime
import dagster as dg
from dagster import MaterializeResult, MetadataValue
from dagster_duckdb import DuckDBResource
import random

from config import config
from shared.database.database_adapter import DatabaseExporterAdapter
from shared.utils.utils import shuffle_date_within_month


def parse_and_shuffle_publication_date(paper, publication_year):
    """
    Parse publication date from paper and return shuffled date within same month.
    Falls back to January 1st of publication year if parsing fails.
    """
    try:
        date_string = str(paper['pub_date'])
        parsed_date = None
        
        # Try common date formats
        for date_format in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
            try:
                parsed_date = datetime.strptime(date_string, date_format)
                break
            except ValueError:
                continue
        
        # If parsing failed, use January 1st
        if parsed_date is None:
            parsed_date = datetime(publication_year, 1, 1)
        
        return shuffle_date_within_month(parsed_date)
        
    except Exception:
        return f"{publication_year}-01-01"


def determine_collaboration_type(coauthor_name, new_collaborators_this_year, career_collaborator_names):
    """
    Determine if a collaboration is NEW or EXISTING based on author's collaboration history.
    
    Logic: A collaboration is NEW if the coauthor appears for the first time this year
    (i.e., they're in new_collaborators_this_year but not in career_collaborator_names).
    """
    if coauthor_name in (new_collaborators_this_year - career_collaborator_names):
        return config.collab_types['NEW']
    else:
        return config.collab_types['EXISTING']


def clear_existing_collaboration_records(db_exporter, target_author_ids):
    """
    Clear existing collaboration records for specified target authors.
    Used when force_update is enabled to ensure clean rebuild.
    """
    print("🔄 FORCE UPDATE: Clearing existing coauthor records")
    total_deleted = 0
    
    for target_author_id in target_author_ids:
        # Count existing records for this author
        count_result = db_exporter.con.execute(
            "SELECT COUNT(*) FROM coauthor2 WHERE ego_aid = ?", 
            (target_author_id,)
        ).fetchone()
        deleted_count = count_result[0] if count_result else 0
        
        # Delete records for this author
        db_exporter.con.execute(
            "DELETE FROM coauthor2 WHERE ego_aid = ?", 
            (target_author_id,)
        )
        total_deleted += deleted_count
    
    db_exporter.con.commit()
    print(f"  Cleared {total_deleted} existing records")
    return total_deleted


@dg.asset(
    deps=["coauthor_cache","academic_publications"],
    group_name="network", 
    description="🤝 Analyze collaboration patterns: who works with whom, when, and how relationships evolve. Each row is aggregated at the yearly level."
)
def collaboration_network(duckdb: DuckDBResource):
    """
    Build coauthor collaboration network with temporal relationship tracking.
    
    Core algorithm:
    1. For each target author
    2. For each year in their career
    3. For each paper they published that year
    4. For each coauthor on that paper
    5. Track collaboration counts and relationship evolution (NEW vs EXISTING)
    """
    paper_file = config.data_raw_path / config.paper_output_file
    author_file = config.data_raw_path / config.author_output_file
    output_file = config.data_clean_path / config.coauthor_output_file

    print("🚀 Starting collaboration network analysis...")
    
    with duckdb.get_connection() as conn:
        # ===============================
        # SETUP AND INITIALIZATION
        # ===============================
        db_exporter = DatabaseExporterAdapter(conn)
        db_exporter.load_existing_paper_data(paper_file)
        db_exporter.load_existing_author_data(author_file)
        db_exporter.load_existing_coauthor_data(output_file)

        print(f"✅ Connected to database")
        
        authors_df = db_exporter.con.sql("SELECT * FROM author").df()
        papers_df = db_exporter.con.sql("SELECT * FROM paper").df()

        # Build fast lookup dictionaries for author/institution data
        print("Creating lookup tables for collaboration analysis...")
        
        # Lookup: (author_id, year) -> (institution,)
        ego_author_lookup = authors_df[['aid', 'pub_year', 'institution']]\
                                   .set_index(['aid', 'pub_year'])\
                                   .apply(tuple, axis=1).to_dict()
        
        # Lookup: (author_name, year) -> (institution, author_id)
        coauthor_lookup = authors_df[['display_name', 'pub_year', 'institution', 'aid']]\
                                   .set_index(['display_name', 'pub_year'])\
                                   .apply(tuple, axis=1).to_dict()
        
        print(f"Created lookup tables with {len(ego_author_lookup)} ego entries and {len(coauthor_lookup)} coauthor entries")
        
        # Get list of target authors to process
        target_authors = db_exporter.con.sql("SELECT DISTINCT ego_aid, ego_display_name FROM paper").df()
        print(f"Found {len(target_authors)} target authors")

        # ===============================
        # CONFIGURATION HANDLING
        # ===============================
        
        # Development mode: process only specific researcher
        if config.target_researcher:
            target_authors = target_authors[target_authors['ego_aid'] == config.target_researcher]
            print(f"🎯 DEV MODE: Processing {config.target_researcher}")
        
        print(f"Selected {len(target_authors)} target authors for processing")
        
        # Handle age update mode
        if config.update_age:
            df_coauthors = db_exporter.con.execute("""
                SELECT * FROM coauthor2 c
                WHERE EXISTS (SELECT 1 FROM author a WHERE a.aid = c.coauthor_aid)
            """).df()
            df_coauthors.to_parquet(output_file)
            return MaterializeResult(metadata={"status": MetadataValue.text("Age has been updated")})

        # Handle force update: clear existing records for target authors only
        if config.force_update:
            target_author_ids = target_authors['ego_aid'].tolist()
            clear_existing_collaboration_records(db_exporter, target_author_ids)

        # ===============================
        # MAIN PROCESSING LOOP
        # ===============================
        total_new_records = 0
        collaboration_type_counts = {"new": 0, "existing": 0, "mutual": 0}
        
        # LEVEL 1: Process each target author individually
        for author_idx, author_row in target_authors.iterrows():
            target_author_id = author_row['ego_aid']
            target_author_name = author_row['ego_display_name']
            
            if pd.isna(target_author_name):
                target_author_name = target_author_id
                
            print(f"\nProcessing {target_author_name} ({target_author_id})")
            
            # Get existing collaboration records to avoid duplicates
            _, existing_coauthor_cache = db_exporter.get_author_cache(target_author_id)
            existing_collaboration_keys = set([(ego_id, coauthor_id, year) for ego_id, coauthor_id, year in existing_coauthor_cache])
            print(f"Found {len(existing_collaboration_keys)} existing coauthor records")
            
            # Get all papers published by this author
            author_papers = papers_df[papers_df['ego_aid'] == target_author_id]
            publication_years = sorted(author_papers['pub_year'].unique())
            
            if not publication_years:
                print(f"No publication years found for {target_author_name}")
                continue
                
            print(f"Found publications in years: {publication_years}")

            # Initialize career-long collaboration tracking for this author
            new_coauthor_records = []
            career_collaborator_names = set()  # All collaborators ever seen
            career_collaboration_counts = {}   # Total papers with each collaborator
            
            # LEVEL 2: Process each year in author's career chronologically
            for publication_year in publication_years:
                
                # Get author's institutional info for this year
                author_info_this_year = ego_author_lookup.get((target_author_id, publication_year))
                if author_info_this_year is None:
                    print(f"Missing institutional info for {target_author_name} in {publication_year}")
                    continue
                
                # Get all papers published by this author in this year
                papers_this_year = papers_df[
                    (papers_df['ego_aid'] == target_author_id) & 
                    (papers_df['pub_year'] == publication_year)
                ]
                
                if len(papers_this_year) == 0:
                    continue
                    
                print(f"  Processing {len(papers_this_year)} papers for {publication_year}")

                # Initialize year-specific collaboration tracking
                publication_dates_this_year = []
                yearly_collaboration_counts = {}  # Papers with each collaborator THIS year
                coauthor_name_to_id_mapping = {}  # Name -> ID lookup for this year
                new_collaborators_this_year = set()  # Collaborators appearing for first time this year

                # LEVEL 3: Process each paper published this year
                for paper_idx, paper in papers_this_year.iterrows():
                    
                    # Collect publication dates for randomization
                    shuffled_date = parse_and_shuffle_publication_date(paper, publication_year)
                    publication_dates_this_year.append(shuffled_date)

                    # Filter papers by work type
                    if paper['work_type'] not in config.accepted_work_types:
                        continue

                    # Check if paper has author list
                    if 'authors' not in paper or pd.isna(paper['authors']):
                        continue
                        
                    # LEVEL 4: Process each coauthor on this paper
                    for coauthor_name in paper['authors'].split(", "):
                        
                        # Skip if coauthor is the ego author themselves
                        if coauthor_name == paper['ego_display_name']:
                            continue
                            
                        # Update collaboration count (temporary variable, same as old code)
                        author_yearly_data = yearly_collaboration_counts.get(coauthor_name, {'count': 0})
                        author_yearly_data['count'] += 1

                        # Look up coauthor's institutional info and ID
                        coauthor_info = coauthor_lookup.get((coauthor_name, publication_year))
                        if coauthor_info is None:
                            continue  # Skip coauthors not in our database

                        coauthor_institution, coauthor_id = coauthor_info
                        
                        # Only save to dictionaries if lookup succeeded (same as old code)
                        yearly_collaboration_counts[coauthor_name] = author_yearly_data
                        career_collaboration_counts[coauthor_name] = career_collaboration_counts.get(coauthor_name, 0) + 1
                        coauthor_name_to_id_mapping[coauthor_name] = coauthor_id

                        # Track if this is a new collaborator for this author
                        if coauthor_name not in career_collaborator_names:
                            new_collaborators_this_year.add(coauthor_name)

                # Create collaboration records for this year
                for coauthor_name, collaboration_data in yearly_collaboration_counts.items():
                    coauthor_id = coauthor_name_to_id_mapping[coauthor_name]
                    
                    # Determine if this is a NEW or EXISTING collaboration
                    relationship_type = determine_collaboration_type(
                        coauthor_name, 
                        new_collaborators_this_year, 
                        career_collaborator_names
                    )
                    
                    # Update statistics
                    if relationship_type == config.collab_types['NEW']:
                        collaboration_type_counts["new"] += 1
                    else:
                        collaboration_type_counts["existing"] += 1

                    # Assign random publication date from this year's papers
                    if publication_dates_this_year:
                        representative_date = random.choice(publication_dates_this_year)
                    else:
                        representative_date = f"{publication_year}-01-01"
                    
                    # Check if this collaboration record already exists
                    collaboration_key = (target_author_id, coauthor_id, publication_year)
                    if config.force_update or collaboration_key not in existing_collaboration_keys:
                        
                        # Create coauthor record in expected format
                        coauthor_record = (
                            target_author_id,                              # ego_aid
                            representative_date,                           # pub_date
                            int(publication_year),                         # pub_year
                            coauthor_id,                                   # coauthor_aid
                            coauthor_name,                                 # coauthor_name
                            relationship_type,                             # acquaintance
                            collaboration_data['count'],                   # yearly_collabo
                            career_collaboration_counts[coauthor_name],    # all_times_collabo
                            None,                                          # shared_institutions
                            None                                           # coauthor_institution
                        )
                        new_coauthor_records.append(coauthor_record)
                
                # Update career-long collaborator set for next year
                career_collaborator_names.update(new_collaborators_this_year)

            # Save new collaboration records for this author
            if len(new_coauthor_records) > 0:
                print(f"Saving {len(new_coauthor_records)} new coauthor records")
                db_exporter.save_coauthors(new_coauthor_records)
                total_new_records += len(new_coauthor_records)
            else:
                print("No new coauthor records to save")

        # ===============================
        # EXPORT AND CLEANUP
        # ===============================
        
        # Export final results to parquet file
        final_collaboration_data = db_exporter.con.sql("SELECT * FROM coauthor2").df()
        final_collaboration_data.to_parquet(output_file)

        print(f"\n🎉 Collaboration network analysis completed!")
        print(f"  🤝 Total collaboration relationships: {total_new_records}")
        
        return MaterializeResult(
            metadata={
                "collaboration_types": MetadataValue.json(collaboration_type_counts),
                "input_files": MetadataValue.json({
                        "papers": str(paper_file),
                        "authors": str(author_file)
                }),
                "output_file": MetadataValue.path(str(output_file)),
            }
        )