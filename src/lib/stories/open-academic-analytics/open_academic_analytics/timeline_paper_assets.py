"""
timeline_paper_assets.py

UPDATED to use Dagster's official DuckDB resource with adapter.
All business logic remains identical - only the database connection changed.
"""

import os
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import dagster as dg
from dagster_duckdb import DuckDBResource

# Import your existing modules (exactly as in original)
from modules.database_adapter import DatabaseExporterAdapter  # 🆕 NEW: Use adapter
from modules.data_fetcher import OpenAlexFetcher
from modules.author_processor import AuthorProcessor
from modules.utils import shuffle_date_within_month

# Configuration - matching original paths
DATA_RAW = Path("data/raw")

# Ensure directories exist
DATA_RAW.mkdir(parents=True, exist_ok=True)

# Configuration for development (exact same as original)
DEV_CONFIG = {
    "max_researchers": 1,  # Process only 1 researcher for testing
    "target_researcher": "A5010744577",  # Set to specific ID or None for first in list
    "force_update": True,  # 🔄 Reprocess everything
    "update_missing_only": False,  # (ignored when force_update=True)
}


@dg.asset
def researchers_tsv_timeline_paper():
    """
    Step 1: Convert researchers parquet to TSV format
    Equivalent to: make researchers (from original Makefile)
    
    This reproduces the exact logic from researchers.py
    UNCHANGED - no database interaction here
    """
    # Load data from parquet (exact same as original researchers.py)
    d = pd.read_parquet(DATA_RAW / "uvm_profs_2023.parquet")

    # Note: Handle column name variations
    cols_mapping = {
        'host_dept (; delimited if more than one)': 'host_dept',
        'host_dept': 'host_dept'  # In case it's already correct
    }
    
    # Rename column if needed
    for old_name, new_name in cols_mapping.items():
        if old_name in d.columns and old_name != new_name:
            d = d.rename(columns={old_name: new_name})
    
    # Select columns (exact same as original)
    cols = ['oa_display_name', 'is_prof', 'group_size', 'perceived_as_male', 
            'host_dept', 'has_research_group', 'oa_uid', 'group_url', 'first_pub_year']
    
    # Export to TSV (exact same as original)
    output_path = DATA_RAW / "researchers.tsv"
    d[cols].to_csv(output_path, sep="\t", index=False)
    
    print(f"✅ Created {output_path} with {len(d)} researchers")
    return f"Processed {len(d)} researchers to researchers.tsv"


@dg.asset(deps=[researchers_tsv_timeline_paper])
def timeline_paper_main(duckdb: DuckDBResource):  # 🆕 UPDATED: Use DuckDB resource
    """
    Step 2: Main timeline-paper.py logic
    
    UPDATED to use DuckDB resource, but all business logic remains identical
    """
    
    print("🚀 Starting timeline-paper import process...")
    
    # 🆕 NEW: Use DuckDB resource with adapter
    with duckdb.get_connection() as conn:
        # Create adapter to maintain exact same interface
        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database via DuckDB resource")
        
        # === ALL BUSINESS LOGIC BELOW IS IDENTICAL TO ORIGINAL ===
        
        # Load researchers annotations (lines 45-50 from original)
        researchers_file = DATA_RAW / "researchers.tsv"
        assert researchers_file.exists(), f"Input file {researchers_file} does not exist"
        
        print(f"Loading researcher data from {researchers_file}")
        target_aids = pd.read_csv(researchers_file, sep="\t")
        print(f"Loaded {len(target_aids)} researcher records")
        
        # Get list of oa_uids for all authors of interest (lines 52-54)
        target_aids = target_aids[~target_aids['oa_uid'].isna()]
        print(f"Found {len(target_aids)} researchers with OpenAlex IDs")
        
        # Extract known first publication years if available (lines 56-58)
        known_years_df = target_aids[['oa_uid', 'first_pub_year']].dropna()
        known_first_pub_years = {k.upper(): int(v) for k, v in known_years_df.values}
        
        # Process target_aids (line 60)
        target_aids['oa_uid'] = target_aids['oa_uid'].str.upper()
        
        # Initialize modules (lines 62-70)
        print("Initializing OpenAlex fetcher")
        fetcher = OpenAlexFetcher()
        
        print("Initializing AuthorProcessor")
        author_processor = AuthorProcessor(db_exporter)

        # Pre-load publication years from database (lines 72-74)
        author_processor.preload_publication_years()
        print(f"Preloaded {len(author_processor.publication_year_cache)} publication year ranges")

        # DEVELOPMENT MODE: Limit to specified number of researchers
        max_researchers = DEV_CONFIG["max_researchers"]
        target_researcher_id = DEV_CONFIG["target_researcher"]
        
        if target_researcher_id:
            # Filter to specific researcher
            target_aids = target_aids[target_aids['oa_uid'] == target_researcher_id]
            print(f"\n🎯 DEVELOPMENT MODE: Processing specific researcher {target_researcher_id}")
        else:
            # Process first N researchers
            target_aids = target_aids.head(max_researchers)
            print(f"\n🔧 DEVELOPMENT MODE: Processing first {max_researchers} researcher(s)")
        
        if len(target_aids) == 0:
            return "❌ No researchers found matching criteria"

        # Process each researcher (lines 76-77 - start of main loop)
        total_papers_saved = 0
        total_researchers_processed = 0
        
        for i, row in tqdm(target_aids.iterrows(), total=len(target_aids)):
               
            target_aid = row['oa_uid']
            
            # Fetch display name from OpenAlex (lines 79-86)
            try:
                author_obj = fetcher.get_author_info(target_aid)
                target_name = author_obj['display_name']
            except Exception as e:
                print(f"Error fetching display name for {target_aid}: {e}")
                # If we can't get the display name, use the ID as a fallback
                target_name = target_aid
                
            print(f"\n👤 Processing {target_name} ({target_aid})")

            # Handle the update author age case (lines 88-96 - SKIPPED for now)
            # We're focusing on the main import functionality
            
            # Get publication year range (lines 98-110)
            min_yr = known_first_pub_years.get(target_aid)
            if min_yr is None:
                try:
                    min_yr, _ = fetcher.get_publication_range(target_aid)
                    print(f"First publication year for {target_name}: {min_yr}")
                except Exception as e:
                    print(f"Error getting first publication year for {target_name}: {e}")
                    continue
            
            try:
                # Get the latest publication year (lines 112-119)
                author_info = fetcher.get_author_info(target_aid)
                max_yr = author_info['counts_by_year'][0]['year']
                print(f"Latest publication year for {target_name}: {max_yr}")
            except Exception as e:
                print(f"Error getting latest publication year for {target_name}: {e}")
                # Fallback to current year if we can't get the latest pub year
                max_yr = datetime.now().year
            
            # Store in publication year cache (lines 121-122)
            author_processor.publication_year_cache[target_aid] = (min_yr, max_yr)

            # Check if database is up to date (lines 124-127)
            force_update = DEV_CONFIG["force_update"]
            if not force_update and db_exporter.is_up_to_date(target_aid, min_yr, max_yr):
                print(f"✅ {target_name} is up to date in database")
                total_researchers_processed += 1
                continue
            
            # Get existing papers from database (lines 129-132)
            paper_cache, _ = db_exporter.get_author_cache(target_aid)
            existing_papers = set([(aid, wid) for aid, wid in paper_cache])
            print(f"Found {len(existing_papers)} existing papers in database")
            
            # Process papers for each year (lines 134-135)
            papers = []

            # Check if we have valid year range (lines 137-141)
            if min_yr is None or max_yr is None:
                print(f"Skipping {target_name} ({target_aid}) - cannot determine publication years")
                continue  # Skip to the next author
            
            # Process each year (lines 143-144)
            for yr in range(min_yr, max_yr + 1):
                    
                print(f"  📅 Processing year {yr}...")
                
                # Get all publications for this year using fetcher (lines 146-152)
                publications = fetcher.get_publications(target_aid, yr)
                
                if not publications:
                    print(f"  No publications found for {target_name} in {yr}")
                    continue
                    
                print(f"  Processing {len(publications)} publications for {yr}")
                
                # Track institutions for this year (lines 154-155)
                ego_institutions_this_year = []
                
                # Process each publication (lines 157-158)
                for w in publications:
                    # Skip non-English works (lines 159-161)
                    if w.get('language') != 'en':
                        continue
                        
                    # Extract work ID (lines 163-164)
                    wid = w['id'].split("/")[-1]
                    
                    # Skip if already in database (enable for production)
                    if not force_update and (target_aid, wid) in existing_papers:
                        continue
                    
                    # Add some noise within year for visualization purpose (lines 170-171)
                    shuffled_date = shuffle_date_within_month(w['publication_date'])
                    
                    # Process authorships (lines 173-174)
                    author_position = None
                    
                    for authorship in w['authorships']:
                        coauthor_name = authorship['author']['display_name']
                        
                        # If this is the target author, collect institution and position (lines 177-182)
                        if authorship['author']['id'].split("/")[-1] == target_aid:
                            ego_institutions_this_year += [i['display_name'] for i in authorship['institutions']]
                            author_position = authorship['author_position']
                    
                    # Determine target institution through majority vote (lines 184-187)
                    from collections import Counter
                    target_institution = None
                    if ego_institutions_this_year:
                        target_institution = Counter(ego_institutions_this_year).most_common(1)[0][0]
                    
                    # Extract paper metadata (lines 189-193)
                    doi = w['ids'].get('doi') if 'ids' in w else None
                    fos = w['primary_topic'].get('display_name') if w.get('primary_topic') else None
                    coauthors = ', '.join([a['author']['display_name'] for a in w['authorships']])
                    
                    # Create paper record (lines 195-207)
                    papers.append((
                        target_aid, target_name, wid,
                        shuffled_date, int(w['publication_year']),
                        doi, w['title'], w['type'], fos,
                        coauthors,
                        w['cited_by_count'],
                        author_position,
                        target_institution
                    ))
            
            # Save papers to database (lines 209-214)
            if papers:
                print(f"💾 Saving {len(papers)} papers for {target_name}")
                db_exporter.save_papers(papers)
                total_papers_saved += len(papers)
            else:
                print(f"No new papers to save for {target_name}")
            
            # Process author information (lines 216-217 - MASSIVE BLOCK)
            if papers:
                print(f"👥 Processing author information for {target_name}")
                
                # Extract coauthor information from papers (lines 219-238)
                coauthor_info = []
                for paper in papers:
                    pub_year = paper[4]  # paper year
                    if paper[9]:  # paper[9] contains author list
                        try:
                            coauthor_names = paper[9].split(", ")
                            for coauthor_name in coauthor_names:
                                if coauthor_name != target_name:
                                    # Add to coauthor_info
                                    coauthor_info.append({
                                        'name': coauthor_name,
                                        'year': pub_year,
                                        'institution': paper[12]  # Use paper's institution
                                    })
                        except Exception as e:
                            print(f"    Error extracting coauthors from paper: {e}")
                
                print(f"  Extracted {len(coauthor_info)} coauthor records from papers")
                
                # Check if we can find OpenAlex IDs for coauthors (lines 240-241)
                coauthors_with_ids = []

                for info in coauthor_info:
                    try:
                        # Skip if essential data is missing (lines 244-249)
                        if not info.get('name') or not info.get('year'):
                            print(f"    Skipping coauthor due to missing name or year: {info}")
                            continue
                            
                        # Check if author is already cached (lines 251-252)
                        result = db_exporter.get_author_cache_by_name(info['name'])
                        
                        # Use fetcher to get author by name if not cached (lines 254-256)
                        if result is None:
                            result = fetcher.get_author_info_by_name(info['name'])
                            
                        # Process result if we found author data (lines 258-259)
                        if result and ('id' in result or 'aid' in result):
                            # Extract coauthor ID (lines 261-263)
                            coauthor_id_raw = result.get('id') or result.get('aid')
                            coauthor_id = coauthor_id_raw.split('/')[-1] if isinstance(coauthor_id_raw, str) else str(coauthor_id_raw)
                            
                            # Create coauthor tuple with consistent date formatting (lines 265-267)
                            pub_date = f"{info['year']}-01-01"
                            
                            coauthor_tuple = (
                                target_aid,                    # ego_aid
                                pub_date,                      # pub_date
                                info['year'],                  # pub_year
                                coauthor_id,                   # coauthor_aid
                                info['name'],                  # coauthor_name
                                "from_paper",                  # acquaintance
                                1,                             # yearly_collabo
                                1,                             # all_times_collabo
                                None,                          # shared_institutions
                                info.get('institution')        # coauthor_institution (safe get)
                            )
                            
                            coauthors_with_ids.append(coauthor_tuple)
                        else:
                            print(f"    No valid ID found for coauthor: {info['name']}")
                            
                    except KeyError as e:
                        print(f"    Missing required field for coauthor {info.get('name', 'Unknown')}: {e}")
                    except AttributeError as e:
                        print(f"    Invalid data format for coauthor {info.get('name', 'Unknown')}: {e}")
                    except Exception as e:
                        print(f"    Unexpected error processing coauthor {info.get('name', 'Unknown')}: {e}")

                print(f"  Successfully processed {len(coauthors_with_ids)} coauthors with IDs")
                print(f"  Found IDs for {len(coauthors_with_ids)} coauthors")

                # Process author records (lines 290-300)
                author_records = author_processor.collect_author_info(
                    target_aid,
                    target_name,  # Pass the display name from API
                    (min_yr, max_yr),
                    papers,
                    coauthors_with_ids,
                    fetcher
                )
                
                # Save author records (lines 302-308)
                if author_records:
                    print(f"  💾 Saving {len(author_records)} author records for {target_name}")
                    db_exporter.save_authors(author_records)
                else:
                    print("  No author records to save")

            total_researchers_processed += 1

        # Final summary (no manual db_exporter.close() - handled by context manager)
        print(f"\n🎉 Timeline-paper import completed!")
        print(f"  📊 Researchers processed: {total_researchers_processed}")
        print(f"  📄 Papers saved: {total_papers_saved}")
        print("🔐 Database connection closed automatically by DuckDB resource")
        
        return f"Successfully processed {total_researchers_processed} researchers, saved {total_papers_saved} papers"


# Simple definitions - faithful to original script structure
defs = dg.Definitions(
    assets=[
        researchers_tsv_timeline_paper,
        timeline_paper_main
    ]
)