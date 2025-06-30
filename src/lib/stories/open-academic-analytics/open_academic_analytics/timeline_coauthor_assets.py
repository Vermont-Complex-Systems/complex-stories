"""
timeline_coauthor_assets.py

UPDATED to use Dagster's official DuckDB resource with adapter.
All business logic remains identical - only the database connection changed.
"""
import calendar
import random
import sys
import os
from pathlib import Path
from datetime import datetime
from collections import Counter

import pandas as pd
from tqdm import tqdm
import dagster as dg
from dagster_duckdb import DuckDBResource

# Import the database adapter and utilities
from modules.database_adapter import DatabaseExporterAdapter
from modules.utils import shuffle_date_within_month

# Configuration - matching original paths
DATA_RAW = Path("data/raw")
DATA_PROCESSED = Path("data/processed") 
PAPER_FILE = DATA_PROCESSED / "paper.parquet"

# Collaboration categories (exact same as original)
COLLAB_TYPES = {
    'NEW': 'new_collab',
    'NEW_THROUGH_MUTUAL': 'new_collab_of_collab', 
    'EXISTING': 'existing_collab'
}

# Processing settings (exact same as original)
BATCH_SIZE = 1000
PROGRESS_REPORT_INTERVAL = 10
MIN_VALID_YEAR = 1950

# Development configuration
DEV_CONFIG = {
    "target_researcher": "A5010744577",
    "force_update": True,  # 🔄 Reprocess everything
    "update_missing_only": False,  # (ignored when force_update=True)
    "enable_debug": True,
}

def load_and_validate_data(db_exporter):
    """
    Load paper and author data, validate integrity.
    UPDATED to take db_exporter as parameter instead of creating it
    
    Args:
        db_exporter: DatabaseExporterAdapter instance from resource
        
    Returns:
        tuple: (df_pap, df_auth) - dataframes only
    """
    # Load processed papers (exact same as original)
    print(f"Loading paper data from {PAPER_FILE}")
    
    try:
        df_pap = pd.read_parquet(PAPER_FILE)
        print(f"Loaded {len(df_pap):,} papers")
    except Exception as e:
        print(f"Error loading paper data: {e}")
        raise
    
    # Load author data from database (exact same as original)
    print("Loading author data from database")
    try:
        df_auth = db_exporter.con.sql("SELECT * from author").fetchdf()
        print(f"Loaded {len(df_auth):,} author records")
    except Exception as e:
        print(f"Error loading author data: {e}")
        raise
    
    return df_pap, df_auth


def create_optimization_lookups(df_auth):
    """
    Create lookup dictionaries for performance optimization.
    EXACT REPRODUCTION of original create_optimization_lookups function
    """
    print("Creating lookup tables for optimization...")
    
    # Create lookup for target author information by (aid, pub_year)
    target2info = df_auth[['aid', 'pub_year', 'institution', 'author_age']]\
                        .set_index(['aid', 'pub_year'])\
                        .apply(tuple, axis=1).to_dict()
    
    # Create lookup for coauthor information by (display_name, pub_year)
    coaut2info = df_auth[['display_name', 'pub_year', 'institution', 'aid']]\
                        .set_index(['display_name', 'pub_year'])\
                        .apply(tuple, axis=1).to_dict()
    
    print(f"Created lookup tables with {len(target2info):,} target entries and {len(coaut2info):,} coauthor entries")
    
    return target2info, coaut2info


def get_target_authors(df_pap):
    """
    Extract list of target authors to process.
    EXACT REPRODUCTION of original get_target_authors function
    """
    targets = df_pap[['ego_aid', 'name']].drop_duplicates()
    print(f"Processing {len(targets):,} target authors")
    
    return targets


def get_author_publication_years(df_pap, target_aid):
    """
    Get publication years for a specific author from paper dataframe.
    EXACT REPRODUCTION of original get_author_publication_years function
    """
    author_papers = df_pap[df_pap['ego_aid'] == target_aid]
    years = sorted(author_papers['pub_year'].unique())
    
    return years


def process_author_year(df_pap, target_aid, target_name, yr, target_info, 
                       coaut2info, set_all_collabs, all_time_collabo, 
                       set_collabs_of_collabs_never_worked_with):
    """
    Process coauthor relationships for a specific author and year.
    EXACT REPRODUCTION of original process_author_year function (with date fix)
    """
    _, auth_age = target_info  # We'll determine target_institution via majority vote
    
    # Initialize yearly tracking variables (exact same as original)
    dates_in_year = []
    all_target_inst_this_year = []  # Collect all target institutions for majority vote
    new_collabs_this_year = set()
    collabs_of_collabs_time_t = set()
    coauthName2aid = {}
    time_collabo = {}
    
    # Get papers for this year from dataframe (exact same as original)
    works = df_pap[(df_pap['ego_aid'] == target_aid) & (df_pap['pub_year'] == yr)]
    
    if len(works) == 0:
        return [], dates_in_year, new_collabs_this_year, time_collabo
        
    print(f"  Processing {len(works)} papers for {target_name} in {yr}")

    for i, w in works.iterrows():
        try:
            # Handle different possible date formats from the database
            date_str = str(w['pub_date'])
            
            # Try different formats that might come from the database
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%d  %H:%M:%S"]:
                try:
                    pub_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                # If no format worked, create a date object for the year
                pub_date = datetime(yr, 1, 1)
            
            shuffled_date = shuffle_date_within_month(pub_date)
            dates_in_year.append(shuffled_date)
        except Exception as e:
            print(f"Error processing date {w['pub_date']}: {e}")
            shuffled_date = f"{yr}-01-01"
            dates_in_year.append(shuffled_date)

        # Collect target author's institutions for this paper (exact same as original)
        if hasattr(w, 'ego_institution') and not pd.isna(w['ego_institution']):
            all_target_inst_this_year.append(w['ego_institution'])
        elif hasattr(w, 'target_institution') and not pd.isna(w['target_institution']):
            all_target_inst_this_year.append(w['target_institution'])

        # Process each coauthor (exact same as original)
        if 'authors' not in w or pd.isna(w['authors']):
            print(f"Warning: Missing authors for paper {w['title']}")
            continue
            
        for coauthor_name in w['authors'].split(", "):
            if coauthor_name != w['name']:
                # Update collaboration count (exact same as original)
                author_yearly_data = time_collabo.get(coauthor_name, {'count': 0, 'institutions': {}})
                author_yearly_data['count'] += 1

                # Get coauthor info (exact same as original)
                coauthor_info = coaut2info.get((coauthor_name, yr))
                
                if coauthor_info is None:
                    time_collabo.pop(coauthor_name, None)
                    continue

                # Extract institution and aid (exact same as original)
                inst_name, coauthor_aid = coauthor_info
                
                # Update institution tracking for coauthor (exact same as original)
                if inst_name:  # Only track if institution is not None
                    author_yearly_data['institutions'][inst_name] = author_yearly_data['institutions'].get(inst_name, 0) + 1

                # Update collaboration trackers (exact same as original)
                time_collabo[coauthor_name] = author_yearly_data
                all_time_collabo[coauthor_name] = all_time_collabo.get(coauthor_name, 0) + 1

                # Store coauthor ID (exact same as original)
                if coauthName2aid.get(coauthor_name) is None:
                    coauthName2aid[coauthor_name] = coauthor_aid

                # Track new collaborators (exact same as original)
                if coauthor_name not in set_all_collabs:
                    new_collabs_this_year.add(coauthor_name)

    # Determine target institution via majority vote (exact same as original)
    target_institution = None
    if len(all_target_inst_this_year) > 0:
        target_institution = Counter(all_target_inst_this_year).most_common(1)[0][0]
    else:
        # Fallback to institution from target_info if no institutions found in papers
        target_institution = target_info[0] if target_info[0] else None

    # Update indirect connections (exact same as original)
    set_collabs_of_collabs_never_worked_with.update(
        collabs_of_collabs_time_t - new_collabs_this_year - set_all_collabs - set([target_name])
    )
    
    # Process yearly collaboration statistics (exact same as original)
    coauthors = []
    if len(time_collabo) > 0:
        print(f"  Processing {len(time_collabo)} coauthors for {target_name} in {yr}")

        for coauthor_name, coauthor_data in time_collabo.items():
            coauthor_aid = coauthName2aid[coauthor_name]
            
            # Determine collaboration type (exact same as original)
            if coauthor_name in (new_collabs_this_year - set_all_collabs):
                if coauthor_name in set_collabs_of_collabs_never_worked_with:
                    subtype = COLLAB_TYPES['NEW_THROUGH_MUTUAL']
                else:
                    subtype = COLLAB_TYPES['NEW']
            else:
                subtype = COLLAB_TYPES['EXISTING']

            # Assign publication date (exact same as original)
            author_date = random.choice(dates_in_year) if dates_in_year else f"{yr}-01-01"
            
            # Create standardized age date for visualization (exact same as original)
            shuffled_auth_age = "1" + author_date.replace(author_date.split("-")[0], str(auth_age).zfill(3))
            # Handle leap year edge case
            shuffled_auth_age = shuffled_auth_age.replace("29", "28") if shuffled_auth_age.endswith("29") else shuffled_auth_age

            # Determine shared institution (exact same logic as original)
            shared_inst = None
            max_institution = None

            if coauthor_data['institutions'] and target_institution:
                # Find the most common institution for this coauthor
                max_institution = max(coauthor_data['institutions'], key=coauthor_data['institutions'].get)
                # Only mark as shared if coauthor's most common institution matches target's institution
                if max_institution == target_institution:
                    shared_inst = max_institution

            # Create coauthor record (exact same as original)
            coauthors.append((
                target_aid,
                author_date, int(author_date[0:4]),
                coauthor_aid, coauthor_name, subtype,
                coauthor_data['count'], all_time_collabo[coauthor_name],
                shared_inst, max_institution
            ))
    
    return coauthors, dates_in_year, new_collabs_this_year, time_collabo


def process_single_author(df_pap, target_aid, target_name, target2info, coaut2info, existing_records):
    """
    Process all coauthor relationships for a single target author across all years.
    EXACT REPRODUCTION of original process_single_author function
    """
    if pd.isna(target_name):
        print(f"Warning: Name is missing for author {target_aid}, using ID as name")
        target_name = target_aid
        
    print(f"Processing {target_name} ({target_aid})")

    # Get publication years (exact same as original)
    years = get_author_publication_years(df_pap, target_aid)
    if not years:
        print(f"No publication years found for {target_name}, skipping")
        return []
        
    print(f"Found publications in years: {years}")

    # Initialize tracking variables (exact same as original)
    all_coauthors = []
    set_all_collabs = set()
    all_time_collabo = {}
    set_collabs_of_collabs_never_worked_with = set()

    # Process each year sequentially (exact same as original)
    for yr in years:
        # Get target author info for this year
        target_info = target2info.get((target_aid, yr))
        if target_info is None:
            print(f"Missing info for {target_name} in {yr}")
            continue
        
        # Process this year's collaborations
        coauthors, dates_in_year, new_collabs_this_year, time_collabo = process_author_year(
            df_pap, target_aid, target_name, yr, target_info, 
            coaut2info, set_all_collabs, all_time_collabo, 
            set_collabs_of_collabs_never_worked_with
        )
        
        # Filter out existing records (exact same as original)
        new_coauthors = []
        force_update = DEV_CONFIG.get("force_update", False)
        for coauthor in coauthors:
            coauthor_aid = coauthor[3]  # coauthor_aid is at index 3
            if force_update or (target_aid, coauthor_aid, yr) not in existing_records:
                new_coauthors.append(coauthor)
        
        all_coauthors.extend(new_coauthors)
        
        # Update all-time collaborators for next year (exact same as original)
        set_all_collabs.update(new_collabs_this_year)

    return all_coauthors


@dg.asset(deps=["paper_preprocessing"])  # String dependency reference
def timeline_coauthor_main(duckdb: DuckDBResource):  # 🆕 UPDATED: Use DuckDB resource
    """
    UPDATED to use DuckDB resource, but all business logic remains identical
    
    Main processing pipeline:
    1. Load paper and author data with validation
    2. Create optimization lookup tables
    3. Process each target author sequentially
    4. For each author/year: analyze coauthor relationships
    5. Save new coauthor records to database
    """
    
    print("🚀 Starting timeline-coauthor processing...")
    
    # 🆕 NEW: Use DuckDB resource with adapter
    with duckdb.get_connection() as conn:
        # Create adapter to maintain exact same interface
        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database via DuckDB resource")
        
        # === ALL BUSINESS LOGIC BELOW IS IDENTICAL TO ORIGINAL ===
        
        # Load and validate input data (updated to use resource)
        df_pap, df_auth = load_and_validate_data(db_exporter)
        
        # Create optimization lookups (exact same as original)
        target2info, coaut2info = create_optimization_lookups(df_auth)
        
        # Get list of target authors (exact same as original)
        targets = get_target_authors(df_pap)

        # DEVELOPMENT MODE: Filter to specific researcher
        target_researcher_id = DEV_CONFIG["target_researcher"]
        force_update = DEV_CONFIG.get("force_update", False)
        
        if target_researcher_id:
            # Filter to specific researcher
            targets = targets[targets['ego_aid'] == target_researcher_id]
            print(f"\n🎯 DEVELOPMENT MODE: Processing specific researcher {target_researcher_id}")
            if len(targets) == 0:
                print(f"❌ Target researcher {target_researcher_id} not found in data")
                return f"Target researcher {target_researcher_id} not found"
        else:
            # Process all researchers (remove this if you always want to specify one)
            print(f"\n🔧 PROCESSING ALL {len(targets)} RESEARCHERS")
        
        print(f"Selected {len(targets)} target authors for processing")

        # 🆕 UPDATED FORCE UPDATE DELETION LOGIC - DuckDB compatible
        if force_update:
            print(f"\n🔄 FORCE UPDATE MODE: Will clear existing coauthor records before processing")
            
            # Clear coauthor records for all target researchers
            target_aids = targets['ego_aid'].tolist()
            total_deleted = 0
            for target_aid in target_aids:
                print(f"  🗑️  Clearing existing coauthor records for {target_aid}")
                
                # DuckDB compatible approach - count first, then delete
                count_result = db_exporter.con.execute(
                    "SELECT COUNT(*) FROM coauthor2 WHERE ego_aid = ?", 
                    (target_aid,)
                ).fetchone()
                deleted_count = count_result[0] if count_result else 0
                
                # Then delete the records
                db_exporter.con.execute(
                    "DELETE FROM coauthor2 WHERE ego_aid = ?", 
                    (target_aid,)
                )
                
                print(f"    Deleted {deleted_count} existing records")
                total_deleted += deleted_count
            
            db_exporter.con.commit()
            print(f"✅ Cleared {total_deleted} existing records for {len(target_aids)} researchers")

        # Process each target author (exact same loop structure as original)
        total_new_records = 0
        
        for i, row in tqdm(targets.iterrows(), total=len(targets), desc="Processing authors"):
            target_aid, target_name = row['ego_aid'], row['name']
            
            # Get existing coauthor records to avoid duplicates (exact same as original)
            # Note: If force_update=True, this will be empty due to deletion above
            _, cache_coauthor = db_exporter.get_author_cache(target_aid)
            existing_records = set([(aid, caid, yr) for aid, caid, yr in cache_coauthor])
            
            if i % PROGRESS_REPORT_INTERVAL == 0 or DEV_CONFIG["enable_debug"]:
                print(f"\n--- Processing author {i+1}/{len(targets)}: {target_name} ---")
                print(f"Found {len(existing_records):,} existing coauthor records")
            
            # Process this author's coauthor relationships (exact same as original)
            coauthors = process_single_author(
                df_pap, target_aid, target_name, target2info, coaut2info, existing_records
            )
            
            # Save new records to database (exact same as original)
            if len(coauthors) > 0:
                if i % PROGRESS_REPORT_INTERVAL == 0 or DEV_CONFIG["enable_debug"]:
                    print(f"Inserting {len(coauthors):,} new coauthor records for {target_name}")
                db_exporter.save_coauthors(coauthors)
                total_new_records += len(coauthors)
            else:
                if i % PROGRESS_REPORT_INTERVAL == 0 or DEV_CONFIG["enable_debug"]:
                    print(f"No new coauthor records to insert for {target_name}")

        # Print final summary (exact same as original)
        print(f"\n=== Processing Complete ===")
        print(f"Total authors processed: {len(targets):,}")
        print(f"Total new coauthor records created: {total_new_records:,}")
        
        print("🔐 Database connection closed automatically by DuckDB resource")
        
        return f"Processed {len(targets)} authors, created {total_new_records:,} new coauthor records"


# Simple definitions - faithful to original script structure
defs = dg.Definitions(
    assets=[
        timeline_coauthor_main
    ]
)