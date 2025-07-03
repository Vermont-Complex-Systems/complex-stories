"""
data_collection.py

Stage 1: Collect raw academic data from external sources
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
from modules.utils import shuffle_date_within_month

@dg.asset(
    group_name="data_collection",
    description="📋 Load list of UVM researchers to analyze for collaboration patterns"
)
def researcher_list():
    """Convert researchers parquet to TSV format for processing"""
    input_file = config.data_raw_path / config.researchers_input_file
    output_file = config.data_raw_path / config.researchers_tsv_file

    # Load and process
    d = pd.read_parquet(input_file)
    
    # Handle column name variations
    if 'host_dept (; delimited if more than one)' in d.columns:
        d = d.rename(columns={'host_dept (; delimited if more than one)': 'host_dept'})
    
    # Select and save
    cols = ['oa_display_name', 'is_prof', 'group_size', 'perceived_as_male', 
            'host_dept', 'has_research_group', 'oa_uid', 'group_url', 'first_pub_year']
    
    d[cols].to_csv(output_file, sep="\t", index=False)
    
    print(f"✅ Created researcher list with {len(d)} researchers")
    
    return MaterializeResult(
        metadata={
            "researchers_loaded": MetadataValue.int(len(d)),
            "output_file": MetadataValue.path(str(output_file)),
            "research_value": MetadataValue.md(
                "**Foundation dataset** for academic collaboration analysis. "
                "Contains UVM faculty with OpenAlex IDs for paper retrieval."
            )
        }
    )

@dg.asset(
    deps=["researcher_list"],
    group_name="data_collection",
    description="📚 Fetch all academic papers for researchers from OpenAlex database"
)
def academic_publications(duckdb: DuckDBResource):
    """
    Fetch papers from OpenAlex for target researchers and save to database.
    This is the core data acquisition step that enables collaboration analysis.
    """
    print("🚀 Starting paper collection from OpenAlex...")
    
    with duckdb.get_connection() as conn:
        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database")
        
        # Load researchers
        researchers_file = config.data_raw_path / config.researchers_tsv_file
        target_aids = pd.read_csv(researchers_file, sep="\t")
        target_aids = target_aids[~target_aids['oa_uid'].isna()]
        target_aids['oa_uid'] = target_aids['oa_uid'].str.upper()
        
        print(f"Found {len(target_aids)} researchers with OpenAlex IDs")
        
        # Extract known first publication years if available
        known_years_df = target_aids[['oa_uid', 'first_pub_year']].dropna()
        known_first_pub_years = {k.upper(): int(v) for k, v in known_years_df.values}
        
        # Development mode filtering
        if config.target_researcher:
            target_aids = target_aids[target_aids['oa_uid'] == config.target_researcher]
            print(f"🎯 DEV MODE: Processing {config.target_researcher}")
        elif config.max_researchers:
            target_aids = target_aids.head(config.max_researchers)
            print(f"🔧 DEV MODE: Processing first {config.max_researchers} researchers")
        
        if len(target_aids) == 0:
            return MaterializeResult(
                metadata={"status": MetadataValue.text("No researchers found matching criteria")}
            )

        # Initialize fetcher
        fetcher = OpenAlexFetcher()
        
        total_papers_saved = 0
        total_researchers_processed = 0
        year_range = [float('inf'), 0]  # Track min/max years
        
        for i, row in tqdm(target_aids.iterrows(), total=len(target_aids), desc="Fetching papers"):
            target_aid = row['oa_uid']
            
            # Get display name
            try:
                author_obj = fetcher.get_author_info(target_aid)
                target_name = author_obj['display_name']
            except Exception as e:
                print(f"Error getting name for {target_aid}: {e}")
                target_name = target_aid
                
            print(f"\n👤 Fetching papers for {target_name} ({target_aid})")

            # Get publication year range
            min_yr = known_first_pub_years.get(target_aid)
            if min_yr is None:
                try:
                    min_yr, _ = fetcher.get_publication_range(target_aid)
                    print(f"First publication year: {min_yr}")
                except Exception as e:
                    print(f"Error getting first publication year: {e}")
                    continue
            
            try:
                author_info = fetcher.get_author_info(target_aid)
                max_yr = author_info['counts_by_year'][0]['year']
                print(f"Latest publication year: {max_yr}")
            except Exception as e:
                print(f"Error getting latest publication year: {e}")
                max_yr = datetime.now().year
            
            # Update year range tracking
            year_range[0] = min(year_range[0], min_yr)
            year_range[1] = max(year_range[1], max_yr)
            
            # Check if up to date (skip if not forcing update)
            if not config.force_update and db_exporter.is_up_to_date(target_aid, min_yr, max_yr):
                print(f"✅ {target_name} papers are up to date")
                total_researchers_processed += 1
                continue
            
            # If force_update=True, we skip the up-to-date check and always process
            if config.force_update:
                print(f"🔄 FORCE UPDATE: Will reprocess all papers for {target_name}")
            
            # If force_update=True, we skip the up-to-date check and always process
            if config.force_update:
                print(f"🔄 FORCE UPDATE: Clearing existing papers for {target_name}")
                # Clear all existing papers for this researcher
                db_exporter.con.execute("DELETE FROM paper WHERE ego_aid = ?", (target_aid,))
                # Clear all existing author records for this researcher  
                db_exporter.con.execute("DELETE FROM author WHERE aid = ?", (target_aid,))
                db_exporter.con.commit()
                print(f"  Cleared existing data for {target_name}")
            
            # Get existing papers to avoid duplicates (will be empty if force_update=True)
            paper_cache, _ = db_exporter.get_author_cache(target_aid)
            existing_papers = set([(aid, wid) for aid, wid in paper_cache])
            
            # Fetch papers for each year
            papers = []
            for yr in range(min_yr, max_yr + 1):
                print(f"  📅 Fetching papers for {yr}...")
                
                publications = fetcher.get_publications(target_aid, yr)
                if not publications:
                    continue
                    
                print(f"  Found {len(publications)} publications")
                ego_institutions_this_year = []
                
                for w in publications:
                    if w.get('language') != 'en':
                        continue
                        
                    wid = w['id'].split("/")[-1]
                    
                    if not config.force_update and (target_aid, wid) in existing_papers:
                        continue
                    
                    # Add date noise for visualization
                    shuffled_date = shuffle_date_within_month(w['publication_date'])
                    
                    # Process authorships to get target author's institution and position
                    author_position = None
                    for authorship in w['authorships']:
                        if authorship['author']['id'].split("/")[-1] == target_aid:
                            ego_institutions_this_year += [i['display_name'] for i in authorship['institutions']]
                            author_position = authorship['author_position']
                    
                    # Determine most common institution for this year
                    from collections import Counter
                    target_institution = None
                    if ego_institutions_this_year:
                        target_institution = Counter(ego_institutions_this_year).most_common(1)[0][0]
                    
                    # Extract paper metadata
                    doi = w['ids'].get('doi') if 'ids' in w else None
                    fos = w['primary_topic'].get('display_name') if w.get('primary_topic') else None
                    coauthors = ', '.join([a['author']['display_name'] for a in w['authorships']])
                    
                    # Create paper record
                    papers.append((
                        target_aid, target_name, wid,
                        shuffled_date, int(w['publication_year']),
                        doi, w['title'], w['type'], fos,
                        coauthors, w['cited_by_count'],
                        author_position, target_institution
                    ))
            
            # Save papers to database
            if papers:
                print(f"💾 Saving {len(papers)} papers for {target_name}")
                db_exporter.save_papers(papers)
                total_papers_saved += len(papers)
            else:
                print(f"No new papers to save for {target_name}")

            total_researchers_processed += 1

        print(f"\n🎉 Paper collection completed!")
        print(f"  📊 Researchers processed: {total_researchers_processed}")
        print(f"  📄 Papers saved: {total_papers_saved}")
        
        return MaterializeResult(
            metadata={
                "researchers_processed": MetadataValue.int(total_researchers_processed),
                "papers_collected": MetadataValue.int(total_papers_saved),
                "years_covered": MetadataValue.text(f"{year_range[0]}-{year_range[1]}"),
                "data_source": MetadataValue.url("https://openalex.org"),
                "research_value": MetadataValue.md(
                    "**Core dataset** enabling analysis of academic collaboration patterns "
                    "across career stages, institutions, and time periods. Each paper contains "
                    "coauthor information essential for network analysis."
                )
            }
        )