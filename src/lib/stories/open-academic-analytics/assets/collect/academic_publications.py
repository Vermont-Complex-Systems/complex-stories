"""
data_collection.py

Stage 1: Collect raw academic data from external sources
"""
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from dagster import asset, get_dagster_logger
from dagster import MaterializeResult, MetadataValue
from dagster_duckdb import DuckDBResource

from config import config

from shared.database.database_adapter import DatabaseExporterAdapter
from shared.clients.openalex_api_client import OpenAlexFetcher
from shared.utils.utils import shuffle_date_within_month


def _create_paper_record(w, target_aid, target_name):
    """Extract paper data from OpenAlex work object."""
    wid = w['id'].split("/")[-1]
    shuffled_date = shuffle_date_within_month(w['publication_date'])
    
    # Process authorships to get target author's institution and position
    author_institution, author_position = _get_author_details(w['authorships'], target_aid)
    
    # Extract paper metadata
    doi = w['ids'].get('doi') if 'ids' in w else None
    fos = w['primary_topic'].get('display_name') if w.get('primary_topic') else None
    coauthors = ', '.join([a['author']['display_name'] for a in w['authorships']])
    
    return (
        target_aid, target_name, wid, shuffled_date, int(w['publication_year']),
        doi, w['title'], w['type'], fos, coauthors, w['cited_by_count'],
        author_position, author_institution
    )

def _get_author_details(authorships, target_aid):
    """Extract institution and position for the target author."""
    for authorship in authorships:
        if authorship['author']['id'].split("/")[-1] == target_aid:
            institution = authorship['institutions'][0]['display_name'] if authorship.get('institutions') else ''
            position = authorship['author_position']
            return institution, position
    return None, None

def _get_researcher_info(fetcher, target_aid, known_first_pub_years):
    """Get researcher display name and publication year range."""
    try:
        author_obj = fetcher.get_author_info(target_aid)
        target_name = author_obj['display_name']
    except Exception as e:
        print(f"Error getting name for {target_aid}: {e}")
        return None, None, None, None
    
    # Get publication year range
    min_yr = known_first_pub_years.get(target_aid)
    if min_yr is None:
        try:
            min_yr, _ = fetcher.get_publication_range(target_aid)
        except Exception as e:
            print(f"Error getting first publication year: {e}")
            return None, None, None, None
    
    try:
        max_yr = author_obj['counts_by_year'][0]['year']
    except Exception as e:
        print(f"Error getting latest publication year: {e}")
        max_yr = datetime.now().year
    
    return target_name, min_yr, max_yr, author_obj

def _should_skip_researcher(db_exporter, target_aid, target_name, min_yr, max_yr):
    """Check if researcher should be skipped (force update or up to date check)."""
    if config.force_update:
        print(f"🔄 FORCE UPDATE: Clearing existing papers for {target_name}")
        db_exporter.con.execute("DELETE FROM paper WHERE ego_aid = ?", (target_aid,))
        db_exporter.con.execute("DELETE FROM author WHERE aid = ?", (target_aid,))
        db_exporter.con.commit()
        return False
    elif db_exporter.is_up_to_date(target_aid, min_yr, max_yr):
        print(f"✅ {target_name} papers are up to date")
        return True
    return False

def _collect_papers_for_researcher(fetcher, target_aid, target_name, min_yr, max_yr, existing_papers):
    """Collect all papers for a researcher across their publication years."""
    papers = []
    
    for yr in range(min_yr, max_yr + 1):
        print(f"  📅 Fetching papers for {yr}...")
        
        publications = fetcher.get_publications(target_aid, yr)
        if not publications:
            continue
            
        print(f"  Found {len(publications)} publications")
        
        for w in publications:
            if w.get('language') != 'en':
                continue
                
            wid = w['id'].split("/")[-1]
            
            if not config.force_update and (target_aid, wid) in existing_papers:
                continue
            
            paper_record = _create_paper_record(w, target_aid, target_name)
            papers.append(paper_record)
    
    return papers

@asset(
    deps=["uvm_profs_2023"],
    group_name="import",
    description="📚 Fetch all academic papers for researchers from OpenAlex database"
)
def academic_publications(duckdb: DuckDBResource):
    """
    Fetch papers from OpenAlex for target researchers and save to database.
    This is the core data acquisition step that enables collaboration analysis.
    """
    logger = get_dagster_logger()

    logger.info("🚀 Starting paper collection from OpenAlex...")
    
    input_file = config.data_raw_path / config.uvm_profs_2023_file
    output_file = config.data_raw_path / config.paper_output_file

    with duckdb.get_connection() as conn:
        # import duckdb 
        # conn = duckdb.connect(":memory:")
        # Initialize database and load existing data
        db_exporter = DatabaseExporterAdapter(conn)
        db_exporter.load_existing_paper_data(output_file)
        
        # Load researchers
        target_aids = pd.read_parquet(input_file)
        logger.info(f"Found {len(target_aids)} researchers with OpenAlex IDs")
        
        # Extract known first publication years if available
        known_years_df = target_aids[['oa_uid', 'first_pub_year']].dropna()
        known_first_pub_years = {k.upper(): int(v) for k, v in known_years_df.values}
        
        # Development mode filtering
        if config.target_researcher:
            target_aids = target_aids[target_aids['oa_uid'] == config.target_researcher]
            logger.info(f"🎯 DEV MODE: Processing {config.target_researcher}")
        
        if config.update_age:
            # Make sure that for those we have known first_pub_year, no publication years come before that.
            query = """SELECT *
                        FROM paper p
                        WHERE NOT EXISTS (
                            SELECT 1 
                            FROM (SELECT unnest($1) as ego_aid, unnest($2) as first_pub_year) lookup
                            WHERE lookup.ego_aid = p.ego_aid 
                            AND p.pub_year < lookup.first_pub_year
                        )"""
            papers_df = db_exporter.con.execute(query, [
                list(known_first_pub_years.keys()),
                list(known_first_pub_years.values())
            ]).df()

            papers_df.to_parquet(output_file)

            return MaterializeResult(
                metadata={"status": MetadataValue.text("Age has been updated")}
            )
        
        # Initialize fetcher and tracking variables
        fetcher = OpenAlexFetcher()
        total_papers_saved = 0
        total_researchers_processed = 0
        year_range = [float('inf'), 0]  # Track min/max years
        

        if len(target_aids) == 0:
            return MaterializeResult(
                metadata={"status": MetadataValue.text("No researchers found matching criteria")}
            )

        # Process each researcher
        for i, row in tqdm(target_aids.iterrows(), total=len(target_aids), desc="Fetching papers"):
            target_aid = row['oa_uid']

            # Get researcher info and publication range
            target_name, min_yr, max_yr, _ = _get_researcher_info(fetcher, target_aid, known_first_pub_years)
            if target_name is None:  # Error occurred
                continue

            logger.info(f"\n👤 Fetching papers for {target_name} ({target_aid})")
            logger.info(f"Publication years: {min_yr}-{max_yr}")
            
            # Update year range tracking
            year_range[0] = min(year_range[0], min_yr)
            year_range[1] = max(year_range[1], max_yr)
            
            # Check if we should skip this researcher
            if _should_skip_researcher(db_exporter, target_aid, target_name, min_yr, max_yr):
                total_researchers_processed += 1
                continue

            # Get existing papers to avoid duplicates
            paper_cache, _ = db_exporter.get_author_cache(target_aid)
            existing_papers = set([(aid, wid) for aid, wid in paper_cache])

            # Collect papers for this researcher
            papers = _collect_papers_for_researcher(fetcher, target_aid, target_name, min_yr, max_yr, existing_papers)
            
            # Save papers to database - we use duckdb logic to ensure data integrity.
            if papers:
                logger.info(f"💾 Saving {len(papers)} papers for {target_name}")
                db_exporter.save_papers(papers)
                total_papers_saved += len(papers)
                # Update parquet file
                db_exporter.con.sql("SELECT * FROM paper").df().to_parquet(output_file)
            else:
                logger.info(f"No new papers to save for {target_name}")

            total_researchers_processed += 1

        return MaterializeResult(
            metadata={
                "researchers_processed": MetadataValue.int(total_researchers_processed),
                "papers_collected": MetadataValue.int(total_papers_saved),
                "years_covered": MetadataValue.text(f"{year_range[0]}-{year_range[1]}"),
                "data_source": MetadataValue.url("https://openalex.org"),
                "input_file": MetadataValue.path(str(input_file)),
                "output_file": MetadataValue.path(str(output_file)),
                "research_value": MetadataValue.md(
                    "Thin wrapper over OpenAlex API collecting information on a set of relevant authors."
                    "We don't do any data wrangling in this step."
                )
            }
        )