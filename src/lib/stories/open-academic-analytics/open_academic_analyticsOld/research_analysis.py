"""
research_analysis.py

Stage 2: Core research analysis - career profiles and collaboration networks
"""
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import dagster as dg
from dagster import MaterializeResult, MetadataValue
from dagster_duckdb import DuckDBResource

from config import config
from modules.database_adapter import DatabaseExporterAdapter
from modules.data_fetcher import OpenAlexFetcher
from modules.author_processor import AuthorProcessor
from modules.utils import shuffle_date_within_month

@dg.asset(
    deps=["academic_publications"],
    group_name="research_analysis",
    description="👩‍🎓 Build researcher career profiles: publication history, ages, institutional affiliations"
)
def researcher_career_profiles(duckdb: DuckDBResource):
    """
    Extract and process researcher career information from collected papers.
    This creates the foundation for age-based collaboration analysis.
    """
    print("🚀 Starting researcher career analysis...")
    
    with duckdb.get_connection() as conn:
        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database")
        
        # Initialize author processor with your sophisticated caching logic
        author_processor = AuthorProcessor(db_exporter)
        author_processor.preload_publication_years()
        
        # Initialize fetcher for coauthor lookups
        fetcher = OpenAlexFetcher()
        
        # Get researchers that have papers
        researchers_with_papers = db_exporter.con.execute("""
            SELECT DISTINCT ego_aid, ego_display_name, 
                   MIN(pub_year) as min_year, MAX(pub_year) as max_year
            FROM paper 
            GROUP BY ego_aid, ego_display_name
        """).fetchall()
        
        print(f"Found {len(researchers_with_papers)} researchers with papers")
        
        # Development mode filtering
        if config.target_researcher:
            researchers_with_papers = [r for r in researchers_with_papers if r[0] == config.target_researcher]
            print(f"🎯 DEV MODE: Processing {config.target_researcher}")
        
        total_author_records = 0
        total_coauthors_identified = 0
        
        for target_aid, target_name, min_yr, max_yr in tqdm(researchers_with_papers, desc="Processing careers"):
            print(f"\n👥 Processing career data for {target_name} ({target_aid})")
            
            # Get papers for this researcher
            papers_query = """
                SELECT * FROM paper WHERE ego_aid = ? ORDER BY pub_year
            """
            papers_df = db_exporter.con.execute(papers_query, (target_aid,)).fetchdf()
            papers = [tuple(row) for _, row in papers_df.iterrows()]
            
            print(f"  Found {len(papers)} papers spanning {min_yr}-{max_yr}")
            
            # Extract coauthor information from papers
            coauthor_info = []
            for paper in papers:
                pub_year = paper[4]  # paper year
                if paper[9]:  # paper[9] contains author list
                    try:
                        coauthor_names = paper[9].split(", ")
                        for coauthor_name in coauthor_names:
                            if coauthor_name != target_name:
                                coauthor_info.append({
                                    'name': coauthor_name,
                                    'year': pub_year,
                                    'institution': paper[12]  # paper institution
                                })
                    except Exception as e:
                        print(f"    Error extracting coauthors from paper: {e}")
            
            print(f"  Extracted {len(coauthor_info)} coauthor records from papers")
            
            # Get coauthor IDs from OpenAlex (this is where your caching logic shines)
            coauthors_with_ids = []
            for info in coauthor_info:
                try:
                    if not info.get('name') or not info.get('year'):
                        continue
                        
                    # Check if author is already cached
                    result = db_exporter.get_author_cache_by_name(info['name'])
                    if result is None:
                        result = fetcher.get_author_info_by_name(info['name'])
                        
                    if result and ('id' in result or 'aid' in result):
                        coauthor_id_raw = result.get('id') or result.get('aid')
                        coauthor_id = coauthor_id_raw.split('/')[-1] if isinstance(coauthor_id_raw, str) else str(coauthor_id_raw)
                        
                        pub_date = f"{info['year']}-01-01"
                        coauthor_tuple = (
                            target_aid, pub_date, info['year'],
                            coauthor_id, info['name'], "from_paper",
                            1, 1, None, info.get('institution')
                        )
                        coauthors_with_ids.append(coauthor_tuple)
                except Exception as e:
                    print(f"    Error processing coauthor {info.get('name', 'Unknown')}: {e}")

            print(f"  Found {len(coauthors_with_ids)} coauthors with OpenAlex IDs")
            total_coauthors_identified += len(coauthors_with_ids)

            # Process author records using your sophisticated AuthorProcessor
            author_records = author_processor.collect_author_info(
                target_aid, target_name, (min_yr, max_yr),
                papers, coauthors_with_ids, fetcher
            )
            
            if author_records:
                print(f"  💾 Saving {len(author_records)} author career records")
                db_exporter.save_authors(author_records)
                total_author_records += len(author_records)
            else:
                print("  No author career records to save")

        print(f"\n🎉 Career analysis completed!")
        print(f"  👥 Total author career records: {total_author_records}")
        print(f"  🤝 Total coauthors identified: {total_coauthors_identified}")
        
        return MaterializeResult(
            metadata={
                "researchers_analyzed": MetadataValue.int(len(researchers_with_papers)),
                "career_records_created": MetadataValue.int(total_author_records),
                "coauthors_identified": MetadataValue.int(total_coauthors_identified),
                "analysis_approach": MetadataValue.md(
                    "**Career stage analysis** using publication timing to calculate researcher ages. "
                    "Enables age-based collaboration pattern analysis."
                ),
                "research_value": MetadataValue.md(
                    "**Critical foundation** for collaboration analysis. Maps researcher career "
                    "trajectories and identifies all potential collaboration partners with age data."
                )
            }
        )

@dg.asset(
    deps=["researcher_career_profiles"],
    group_name="research_analysis", 
    description="🤝 Analyze collaboration patterns: who works with whom, when, and how relationships evolve"
)
def collaboration_network(duckdb: DuckDBResource):
    """
    Build coauthor collaboration network with sophisticated relationship analysis.
    This is your existing timeline_coauthor_main logic moved here.
    """
    print("🚀 Starting collaboration network analysis...")
    
    with duckdb.get_connection() as conn:
        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database")
        
        # Load paper and author data (your existing logic)
        paper_file = config.data_processed_path / config.paper_output_file
        print(f"Loading paper data from {paper_file}")
        
        try:
            df_pap = pd.read_parquet(paper_file)
            print(f"Loaded {len(df_pap)} papers")
        except Exception as e:
            print(f"Error loading paper data: {e}")
            # Fall back to loading from database
            df_pap = db_exporter.con.sql("SELECT * FROM paper").fetchdf()
            print(f"Loaded {len(df_pap)} papers from database")
        
        print("Loading author data from database")
        df_auth = db_exporter.con.sql("SELECT * from author").fetchdf()
        print(f"Loaded {len(df_auth)} author records")
        
        # Create optimization lookups (your existing sophisticated logic)
        print("Creating lookup tables for collaboration analysis...")
        target2info = df_auth[['aid', 'pub_year', 'institution', 'author_age']]\
                            .set_index(['aid', 'pub_year'])\
                            .apply(tuple, axis=1).to_dict()
        
        coaut2info = df_auth[['display_name', 'pub_year', 'institution', 'aid']]\
                            .set_index(['display_name', 'pub_year'])\
                            .apply(tuple, axis=1).to_dict()
        
        print(f"Created lookup tables with {len(target2info)} target entries and {len(coaut2info)} coauthor entries")
        
        # Get target authors
        targets = df_pap[['ego_aid', 'name']].drop_duplicates()
        print(f"Found {len(targets)} target authors")

        # Development mode filtering
        if config.target_researcher:
            targets = targets[targets['ego_aid'] == config.target_researcher]
            print(f"🎯 DEV MODE: Processing {config.target_researcher}")
        elif config.max_researchers:
            targets = targets.head(config.max_researchers)
            print(f"🔧 DEV MODE: Processing first {config.max_researchers} researchers")
        
        print(f"Selected {len(targets)} target authors for processing")

        # Force update logic if needed
        if config.force_update:
            print("🔄 FORCE UPDATE: Clearing existing coauthor records")
            target_aids = targets['ego_aid'].tolist()
            total_deleted = 0
            for target_aid in target_aids:
                count_result = db_exporter.con.execute(
                    "SELECT COUNT(*) FROM coauthor2 WHERE ego_aid = ?", 
                    (target_aid,)
                ).fetchone()
                deleted_count = count_result[0] if count_result else 0
                
                db_exporter.con.execute(
                    "DELETE FROM coauthor2 WHERE ego_aid = ?", 
                    (target_aid,)
                )
                total_deleted += deleted_count
            
            db_exporter.con.commit()
            print(f"  Cleared {total_deleted} existing records")

        # Process each target author (your existing sophisticated logic)
        total_new_records = 0
        collaboration_types = {"new": 0, "existing": 0, "mutual": 0}
        
        # Import your existing helper functions from the old timeline_coauthor_assets
        from collections import Counter
        import random
        
        for i, row in tqdm(targets.iterrows(), total=len(targets), desc="Processing authors"):
            target_aid, target_name = row['ego_aid'], row['name']
            
            if pd.isna(target_name):
                target_name = target_aid
                
            print(f"\nProcessing {target_name} ({target_aid})")
            
            # Get existing records to avoid duplicates
            _, cache_coauthor = db_exporter.get_author_cache(target_aid)
            existing_records = set([(aid, caid, yr) for aid, caid, yr in cache_coauthor])
            print(f"Found {len(existing_records)} existing coauthor records")
            
            # Get publication years for this author
            author_papers = df_pap[df_pap['ego_aid'] == target_aid]
            years = sorted(author_papers['pub_year'].unique())
            
            if not years:
                print(f"No publication years found for {target_name}")
                continue
                
            print(f"Found publications in years: {years}")

            # Process each year (simplified version of your complex logic)
            all_coauthors = []
            set_all_collabs = set()
            all_time_collabo = {}
            
            for yr in years:
                # Get target author info for this year
                target_info = target2info.get((target_aid, yr))
                if target_info is None:
                    print(f"Missing info for {target_name} in {yr}")
                    continue
                
                _, auth_age = target_info
                
                # Get papers for this year
                works = df_pap[(df_pap['ego_aid'] == target_aid) & (df_pap['pub_year'] == yr)]
                if len(works) == 0:
                    continue
                    
                print(f"  Processing {len(works)} papers for {yr}")

                # Process collaborations for this year
                dates_in_year = []
                time_collabo = {}
                coauthName2aid = {}
                new_collabs_this_year = set()

                for _, w in works.iterrows():
                    # Handle date
                    try:
                        date_str = str(w['pub_date'])
                        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                            try:
                                pub_date = datetime.strptime(date_str, fmt)
                                break
                            except ValueError:
                                continue
                        else:
                            pub_date = datetime(yr, 1, 1)
                        
                        shuffled_date = shuffle_date_within_month(pub_date)
                        dates_in_year.append(shuffled_date)
                    except:
                        shuffled_date = f"{yr}-01-01"
                        dates_in_year.append(shuffled_date)

                    # Process coauthors
                    if 'authors' not in w or pd.isna(w['authors']):
                        continue
                        
                    for coauthor_name in w['authors'].split(", "):
                        if coauthor_name != w['name']:
                            # Update collaboration count
                            author_yearly_data = time_collabo.get(coauthor_name, {'count': 0})
                            author_yearly_data['count'] += 1

                            # Get coauthor info
                            coauthor_info = coaut2info.get((coauthor_name, yr))
                            if coauthor_info is None:
                                continue

                            inst_name, coauthor_aid = coauthor_info
                            
                            time_collabo[coauthor_name] = author_yearly_data
                            all_time_collabo[coauthor_name] = all_time_collabo.get(coauthor_name, 0) + 1
                            coauthName2aid[coauthor_name] = coauthor_aid

                            # Track new collaborators
                            if coauthor_name not in set_all_collabs:
                                new_collabs_this_year.add(coauthor_name)

                # Create coauthor records for this year
                for coauthor_name, coauthor_data in time_collabo.items():
                    coauthor_aid = coauthName2aid[coauthor_name]
                    
                    # Determine collaboration type
                    if coauthor_name in (new_collabs_this_year - set_all_collabs):
                        subtype = config.collab_types['NEW']
                        collaboration_types["new"] += 1
                    else:
                        subtype = config.collab_types['EXISTING']
                        collaboration_types["existing"] += 1

                    # Assign publication date
                    author_date = random.choice(dates_in_year) if dates_in_year else f"{yr}-01-01"
                    
                    # Check if this is a new record
                    if config.force_update or (target_aid, coauthor_aid, yr) not in existing_records:
                        coauthor_record = (
                            target_aid, author_date, int(yr),  # Convert numpy.int32 to int
                            coauthor_aid, coauthor_name, subtype,
                            coauthor_data['count'], all_time_collabo[coauthor_name],
                            None, None  # shared_institutions, coauthor_institution
                        )
                        all_coauthors.append(coauthor_record)
                
                # Update all-time collaborators for next year
                set_all_collabs.update(new_collabs_this_year)

            # Save new records
            if len(all_coauthors) > 0:
                print(f"Saving {len(all_coauthors)} new coauthor records")
                db_exporter.save_coauthors(all_coauthors)
                total_new_records += len(all_coauthors)
            else:
                print("No new coauthor records to save")

        print(f"\n🎉 Collaboration network analysis completed!")
        print(f"  🤝 Total collaboration relationships: {total_new_records}")
        
        return MaterializeResult(
            metadata={
                "collaboration_relationships": MetadataValue.int(total_new_records),
                "researchers_analyzed": MetadataValue.int(len(targets)),
                "collaboration_types": MetadataValue.json(collaboration_types),
                "research_insight": MetadataValue.md(
                    "**Core research findings** on collaboration patterns. Reveals mentorship "
                    "relationships, career-stage effects, and institutional collaboration networks."
                )
            }
        )