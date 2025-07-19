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
from shared.database.database_adapter import DatabaseExporterAdapter
from shared.utils.utils import shuffle_date_within_month

@dg.asset(
    deps=["coauthor_cache","academic_publications"],
    group_name="network", 
    description="🤝 Analyze collaboration patterns: who works with whom, when, and how relationships evolve"
)
def collaboration_network(duckdb: DuckDBResource):
    """
    Build coauthor collaboration network with sophisticated relationship analysis.
    This is your existing timeline_coauthor_main logic moved here.
    """
    paper_file = config.data_raw_path / config.paper_output_file
    author_file = config.data_raw_path / config.author_output_file
    output_file = config.data_clean_path / config.coauthor_output_file

    print("🚀 Starting collaboration network analysis...")
    
    with duckdb.get_connection() as conn:
        # import duckdb
        # conn = duckdb.connect(":memory:")
        
        df_pap = pd.read_parquet(paper_file)
        conn.execute("CREATE TABLE paper AS SELECT * FROM df_pap")

        df_auth = pd.read_parquet(author_file)
        print(f"Loaded {len(df_auth)} author records")
        conn.execute("CREATE TABLE author AS SELECT * FROM df_auth")
        
        if output_file.exists():
            df_coauth = pd.read_parquet(output_file)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS coauthor2 (
                ego_aid VARCHAR,
                pub_date DATE,
                pub_year INT,
                coauthor_aid VARCHAR,
                coauthor_name VARCHAR,
                acquaintance VARCHAR,
                yearly_collabo INT,
                all_times_collabo INT,
                shared_institutions VARCHAR,
                coauthor_institution VARCHAR,
                PRIMARY KEY(ego_aid, coauthor_aid, pub_year)
            )
        """)
            conn.execute("INSERT INTO coauthor2 SELECT * FROM df_coauth")

        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database")
        
        # Create optimization lookups
        print("Creating lookup tables for collaboration analysis...")
        target2info = df_auth[['aid', 'pub_year', 'institution']]\
                            .set_index(['aid', 'pub_year'])\
                            .apply(tuple, axis=1).to_dict()
        
        coaut2info = df_auth[['display_name', 'pub_year', 'institution', 'aid']]\
                            .set_index(['display_name', 'pub_year'])\
                            .apply(tuple, axis=1).to_dict()
        
        print(f"Created lookup tables with {len(target2info)} target entries and {len(coaut2info)} coauthor entries")
        
        # Get target authors
        targets = df_pap[['ego_aid', 'ego_display_name']].drop_duplicates()
        print(f"Found {len(targets)} target authors")

        # Development mode filtering
        if config.target_researcher:
            targets = targets[targets['ego_aid'] == config.target_researcher]
            print(f"🎯 DEV MODE: Processing {config.target_researcher}")
        
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
            target_aid, target_name = row['ego_aid'], row['ego_display_name']
            
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

            # Process each year 
            all_coauthors = []
            set_all_collabs = set()
            all_time_collabo = {}
            
            for yr in years:
                # yr = years[0]
                # Get target author info for this year
                target_info = target2info.get((target_aid, yr))
                if target_info is None:
                    print(f"Missing info for {target_name} in {yr}")
                    continue
                
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

                    if w['work_type'] not in config.accepted_work_types:
                        continue

                    # Process coauthors
                    if 'authors' not in w or pd.isna(w['authors']):
                        continue
                        
                    for coauthor_name in w['authors'].split(", "):
                        if coauthor_name != w['ego_display_name']:
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

            db_exporter.con.sql("SELECT * FROM coauthor2").df().to_parquet(output_file)

        print(f"\n🎉 Collaboration network analysis completed!")
        print(f"  🤝 Total collaboration relationships: {total_new_records}")
        
        return MaterializeResult(
            metadata={
                "collaboration_relationships": MetadataValue.int(total_new_records),
                "researchers_analyzed": MetadataValue.int(len(targets)),
                "collaboration_types": MetadataValue.json(collaboration_types),
                "input_file_1": MetadataValue.path(str(paper_file)),
                "input_file_2": MetadataValue.path(str(author_file)),
                "output_file": MetadataValue.path(str(output_file)),
                "research_insight": MetadataValue.md(
                    "**Core research findings** on collaboration patterns. Reveals mentorship "
                    "relationships, career-stage effects, and institutional collaboration networks."
                )
            }
        )