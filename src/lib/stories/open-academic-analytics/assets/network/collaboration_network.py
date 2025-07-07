"""
collaboration_network.py - Network Analysis Stage

Analyze collaboration patterns using academic age data.
Pure HRDAG: reads from parquet files, uses parquet-based caching, writes to parquet.
"""
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import dagster as dg
from dagster import MaterializeResult, MetadataValue
from collections import Counter
import random

from config import config
from modules.utils import shuffle_date_within_month

def get_author_cache_from_parquet(target_aid, papers_file, collaborations_file):
    """
    Get existing records for a researcher from parquet files.
    Replaces db_exporter.get_author_cache(target_aid)
    """
    # Get paper cache from papers.parquet
    paper_cache = []
    if papers_file.exists():
        papers_df = pd.read_parquet(papers_file)
        researcher_papers = papers_df[papers_df['ego_aid'] == target_aid]
        paper_cache = [(row['ego_aid'], row['wid']) for _, row in researcher_papers.iterrows()]
    
    # Get coauthor cache from collaborations.parquet  
    coauthor_cache = []
    if collaborations_file.exists():
        collaborations_df = pd.read_parquet(collaborations_file)
        researcher_collabs = collaborations_df[collaborations_df['ego_aid'] == target_aid]
        coauthor_cache = [(row['ego_aid'], row['coauthor_aid'], row['pub_year']) 
                         for _, row in researcher_collabs.iterrows()]
    
    return paper_cache, coauthor_cache

def build_lookup_tables_from_parquet(authors_file):
    """Build optimization lookup tables from author profiles parquet."""
    if not authors_file.exists():
        return {}, {}
    
    df_auth = pd.read_parquet(authors_file)
    
    target2info = df_auth[['aid', 'pub_year', 'institution', 'author_age']]\
                        .set_index(['aid', 'pub_year'])\
                        .apply(tuple, axis=1).to_dict()
    
    coaut2info = df_auth[['display_name', 'pub_year', 'institution', 'aid']]\
                       .set_index(['display_name', 'pub_year'])\
                       .apply(tuple, axis=1).to_dict()
    
    return target2info, coaut2info

def check_force_update_from_parquet(target_aids, collaborations_file, force_update_flag):
    """Handle force update logic for parquet files."""
    if not force_update_flag or not collaborations_file.exists():
        return 0
    
    collaborations_df = pd.read_parquet(collaborations_file)
    records_to_clear = collaborations_df[collaborations_df['ego_aid'].isin(target_aids)]
    total_cleared = len(records_to_clear)
    
    if total_cleared > 0:
        remaining_df = collaborations_df[~collaborations_df['ego_aid'].isin(target_aids)]  # Remove current targets
        remaining_df.to_parquet(collaborations_file)
        print(f"🔄 FORCE UPDATE: Cleared {total_cleared} existing collaboration records")
    
    return total_cleared

@dg.asset(
    deps=["coauthor_cache"],
    group_name="network", 
    description="🤝 Analyze collaboration patterns: who works with whom, when, and how relationships evolve"
)
def collaboration_network():
    """
    Build coauthor collaboration network with sophisticated relationship analysis.
    Pure HRDAG: reads from parquet files, uses parquet-based caching, writes to parquet.
    """
    print("🚀 Starting collaboration network analysis...")
    
    # HRDAG: Define file paths
    papers_file = config.data_raw_path / config.paper_output_file
    authors_file = config.data_raw_path / config.author_output_file
    collaborations_file = config.data_clean_path / config.coauthor_output_file
    
    # HRDAG: Load from previous stages' parquet files
    print(f"📖 Loading papers from {papers_file}")
    df_pap = pd.read_parquet(papers_file)
    print(f"Loaded {len(df_pap)} papers")
    
    # HRDAG: Build lookup tables from parquet
    print(f"📚 Building lookup tables from {authors_file}")
    target2info, coaut2info = build_lookup_tables_from_parquet(authors_file)
    print(f"Created lookup tables with {len(target2info)} target entries and {len(coaut2info)} coauthor entries")
        
    # Get target authors - use the correct column name from paper table
    if 'ego_display_name' in df_pap.columns:
        targets = df_pap[['ego_aid', 'ego_display_name']].drop_duplicates()
        targets = targets.rename(columns={'ego_display_name': 'name'})
    elif 'name' in df_pap.columns:
        targets = df_pap[['ego_aid', 'name']].drop_duplicates()
    else:
        # Fallback: create name column from ego_aid
        print("No name column found, using ego_aid as name...")
        targets = df_pap[['ego_aid']].drop_duplicates()
        targets['name'] = targets['ego_aid']
    
    print(f"Found {len(targets)} target authors")

    # Development mode filtering
    if config.target_researcher:
        targets = targets[targets['ego_aid'] == config.target_researcher]
        print(f"🎯 DEV MODE: Processing {config.target_researcher}")
    elif config.max_researchers:
        targets = targets.head(config.max_researchers)
        print(f"🔧 DEV MODE: Processing first {config.max_researchers} researchers")
    
    print(f"Selected {len(targets)} target authors for processing")

    # HRDAG: Handle force update from parquet
    if config.force_update:
        target_aids = targets['ego_aid'].tolist()
        total_cleared = check_force_update_from_parquet(target_aids, collaborations_file, config.force_update)

    # Process each target author (your existing sophisticated logic)
    all_collaboration_records = []
    collaboration_types = {"new": 0, "existing": 0, "mutual": 0}
    
    for i, row in tqdm(targets.iterrows(), total=len(targets), desc="Processing authors"):
        target_aid, target_name = row['ego_aid'], row['name']
        
        if pd.isna(target_name):
            target_name = target_aid
            
        print(f"\nProcessing {target_name} ({target_aid})")
        
        # HRDAG: Get existing records from parquet (replaces db_exporter.get_author_cache)
        _, cache_coauthor = get_author_cache_from_parquet(target_aid, papers_file, collaborations_file)
        existing_records = set([(aid, caid, yr) for aid, caid, yr in cache_coauthor])
        print(f"Found {len(existing_records)} existing collaboration records from parquet cache")
        
        # Get publication years for this author
        author_papers = df_pap[df_pap['ego_aid'] == target_aid]
        years = sorted(author_papers['pub_year'].unique())
        
        if not years:
            print(f"No publication years found for {target_name}")
            continue
            
        print(f"Found publications in years: {years}")

        # Process each year (your existing sophisticated logic)
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

                # Process coauthors - use the correct column name
                authors_col = None
                if 'authors' in w:
                    authors_col = 'authors'
                elif 'coauthors' in w:
                    authors_col = 'coauthors'
                elif 'author_list' in w:
                    authors_col = 'author_list'
                
                if authors_col is None or pd.isna(w[authors_col]):
                    continue
                    
                # Get the target author's name for comparison
                target_name_for_comparison = target_name
                if 'ego_display_name' in w:
                    target_name_for_comparison = w['ego_display_name']
                    
                for coauthor_name in w[authors_col].split(", "):
                    if coauthor_name != target_name_for_comparison:
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
                
                # Check if this is a new record (faithful to original per-researcher cache check)
                if config.force_update or (target_aid, coauthor_aid, yr) not in existing_records:
                    # Determine collaboration type
                    if coauthor_name in (new_collabs_this_year - set_all_collabs):
                        subtype = config.collab_types['NEW']
                        collaboration_types["new"] += 1
                    else:
                        subtype = config.collab_types['EXISTING']
                        collaboration_types["existing"] += 1

                    # Assign publication date
                    author_date = random.choice(dates_in_year) if dates_in_year else f"{yr}-01-01"
                    
                    coauthor_record = (
                        target_aid, author_date, int(yr),  # Convert numpy.int32 to int
                        coauthor_aid, coauthor_name, subtype,
                        coauthor_data['count'], all_time_collabo[coauthor_name],
                        None, None  # shared_institutions, coauthor_institution
                    )
                    all_collaboration_records.append(coauthor_record)
            
            # Update all-time collaborators for next year
            set_all_collabs.update(new_collabs_this_year)

    print(f"\n💾 Saving collaboration data...")
    
    # HRDAG: Save to parquet file for next stage
    if all_collaboration_records:
        collab_columns = ['ego_aid', 'pub_date', 'pub_year', 'coauthor_aid', 'coauthor_name', 
                        'acquaintance', 'yearly_collabo', 'all_times_collabo', 
                        'shared_institutions', 'coauthor_institution']
        collaborations_df = pd.DataFrame(all_collaboration_records, columns=collab_columns)
        
        print(f"💾 Saving {len(collaborations_df)} collaboration records to {collaborations_file}")
        collaborations_df.to_parquet(collaborations_file)
    
    print(f"\n🎉 Collaboration network analysis completed!")
    print(f"  🤝 Total collaboration relationships: {len(all_collaboration_records)}")
    
    return MaterializeResult(
        metadata={
            "collaboration_relationships": MetadataValue.int(len(all_collaboration_records)),
            "researchers_analyzed": MetadataValue.int(len(targets)),
            "collaboration_types": MetadataValue.json(collaboration_types),
            "input_papers_file": MetadataValue.path(str(papers_file)),
            "input_authors_file": MetadataValue.path(str(authors_file)),
            "output_file": MetadataValue.path(str(collaborations_file)),
            "research_insight": MetadataValue.md(
                "**Core research findings** on collaboration patterns. Reveals mentorship "
                "relationships, career-stage effects, and institutional collaboration networks."
            )
        }
    )