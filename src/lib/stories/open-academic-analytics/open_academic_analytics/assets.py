import os
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import dagster as dg

# Import your existing modules
from modules.database_exporter import DatabaseExporter
from modules.data_fetcher import OpenAlexFetcher
from modules.author_processor import AuthorProcessor

# Configuration
DATA_RAW = Path("data/raw")
DATA_PROCESSED = Path("data/processed")
DATABASE_PATH = DATA_RAW / "oa_data_raw.db"

# Ensure directories exist
DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)


@dg.asset
def researchers_tsv():
    """Convert researchers parquet to TSV format."""
    df = pd.read_parquet("data/raw/uvm_profs_2023.parquet")
    
    cols = [
        'oa_display_name', 'is_prof', 'group_size', 'perceived_as_male',
        'host_dept', 'has_research_group', 'oa_uid', 'group_url', 'first_pub_year'
    ]
    
    df[cols].to_csv("data/raw/researchers.tsv", sep='\t', index=False)
    return f"Processed {len(df)} researchers successfully"


@dg.asset
def database_setup():
    """Initialize the DuckDB database with required tables."""
    try:
        db_exporter = DatabaseExporter(str(DATABASE_PATH))
        db_exporter.close()
        return f"Database initialized at {DATABASE_PATH}"
    except Exception as e:
        return f"Database setup failed: {e}"


@dg.asset(deps=[researchers_tsv, database_setup])
def fetch_researcher_papers():
    """Fetch papers for researchers from OpenAlex API."""
    # Load researchers data
    researchers_df = pd.read_csv("data/raw/researchers.tsv", sep="\t")
    researchers_df = researchers_df[~researchers_df['oa_uid'].isna()]
    researchers_df['oa_uid'] = researchers_df['oa_uid'].str.upper()
    
    print(f"Processing {len(researchers_df)} researchers with OpenAlex IDs")
    
    # Extract known first publication years
    known_years_df = researchers_df[['oa_uid', 'first_pub_year']].dropna()
    known_first_pub_years = {k.upper(): int(v) for k, v in known_years_df.values}
    
    # Initialize modules
    db_exporter = DatabaseExporter(str(DATABASE_PATH))
    fetcher = OpenAlexFetcher()
    author_processor = AuthorProcessor(db_exporter)
    
    papers_processed = 0
    authors_processed = 0
    
    # Process first 3 researchers for development
    for i, row in tqdm(researchers_df.head(3).iterrows(), total=3):
        target_aid = row['oa_uid']
        
        try:
            # Get author info from OpenAlex
            author_obj = fetcher.get_author_info(target_aid)
            target_name = author_obj['display_name'] if author_obj else target_aid
            
            print(f"Processing {target_name} ({target_aid})")
            
            # Get publication year range
            min_yr = known_first_pub_years.get(target_aid)
            if min_yr is None:
                min_yr, _ = fetcher.get_publication_range(target_aid)
            
            # Get latest publication year
            author_info = fetcher.get_author_info(target_aid)
            max_yr = (author_info['counts_by_year'][0]['year'] 
                     if author_info and author_info.get('counts_by_year') 
                     else datetime.now().year)
            
            # Check if database is up to date
            if db_exporter.is_up_to_date(target_aid, min_yr, max_yr):
                print(f"{target_name} is up to date in database")
                continue
            
            # Process papers for each year
            papers = []
            for yr in range(min_yr, max_yr + 1):
                publications = fetcher.get_publications(target_aid, yr)
                
                if not publications:
                    continue
                
                for w in publications:
                    if w.get('language') != 'en':
                        continue
                    
                    wid = w['id'].split("/")[-1]
                    
                    papers.append((
                        target_aid, target_name, wid,
                        w['publication_date'], int(w['publication_year']),
                        w['ids'].get('doi') if 'ids' in w else None,
                        w['title'], w['type'], 
                        w['primary_topic'].get('display_name') if w.get('primary_topic') else None,
                        ', '.join([a['author']['display_name'] for a in w['authorships']]),
                        w['cited_by_count'],
                        None,  # author_position
                        None   # target_institution
                    ))
            
            # Save papers to database
            if papers:
                print(f"Saving {len(papers)} papers for {target_name}")
                db_exporter.save_papers(papers)
                papers_processed += len(papers)
            
            authors_processed += 1
            
        except Exception as e:
            print(f"Error processing {target_aid}: {e}")
            continue
    
    db_exporter.close()
    return f"Processed {authors_processed} researchers, saved {papers_processed} papers"


@dg.asset(deps=[fetch_researcher_papers])
def export_papers_from_db():
    """Export papers from database to parquet."""
    db_exporter = DatabaseExporter(str(DATABASE_PATH))
    
    query = """
        SELECT p.ego_aid, a.display_name as name, p.pub_date, p.pub_year, p.title,
               p.cited_by_count, p.doi, p.wid, p.authors, p.work_type, 
               a.author_age as ego_age
        FROM paper p
        LEFT JOIN author a ON p.ego_aid = a.aid AND p.pub_year = a.pub_year
    """
    
    df = db_exporter.con.sql(query).fetchdf()
    db_exporter.close()
    
    if len(df) == 0:
        return "No papers found in database"
    
    # Basic filtering
    df = df[~df.title.isna()]
    df['nb_coauthors'] = df.authors.apply(
        lambda x: len(x.split(", ")) if isinstance(x, str) else 0
    )
    
    df.to_parquet("data/processed/paper.parquet")
    return f"Exported {len(df)} papers"


@dg.asset(deps=[export_papers_from_db])
def process_coauthor_relationships():
    """Extract coauthor relationships from papers."""
    # Load papers
    papers_df = pd.read_parquet("data/processed/paper.parquet")
    
    if len(papers_df) == 0:
        return "No papers to process"
    
    db_exporter = DatabaseExporter(str(DATABASE_PATH))
    
    # Load author data for lookups
    df_auth = db_exporter.con.sql("SELECT * from author").fetchdf()
    
    # Create lookup tables
    target2info = df_auth[['aid', 'pub_year', 'institution', 'author_age']]\
                        .set_index(['aid', 'pub_year'])\
                        .apply(tuple, axis=1).to_dict()
    
    coaut2info = df_auth[['display_name', 'pub_year', 'institution', 'aid']]\
                        .set_index(['display_name', 'pub_year'])\
                        .apply(tuple, axis=1).to_dict()
    
    # Get target authors
    targets = papers_df[['ego_aid', 'name']].drop_duplicates()
    total_new_records = 0
    
    # Process first 2 authors for development
    for i, row in tqdm(targets.head(2).iterrows(), total=2):
        target_aid, target_name = row['ego_aid'], row['name']
        
        if pd.isna(target_name):
            target_name = target_aid
        
        # Get existing records
        _, cache_coauthor = db_exporter.get_author_cache(target_aid)
        existing_records = set([(aid, caid, yr) for aid, caid, yr in cache_coauthor])
        
        # Get papers for this author
        author_papers = papers_df[papers_df['ego_aid'] == target_aid]
        years = sorted(author_papers['pub_year'].unique())
        
        if not years:
            continue
        
        # Track collaborations over time
        all_coauthors = []
        set_all_collabs = set()
        all_time_collabo = {}
        
        for yr in years:
            target_info = target2info.get((target_aid, yr))
            if target_info is None:
                continue
            
            year_papers = author_papers[author_papers['pub_year'] == yr]
            new_collabs_this_year = set()
            time_collabo = {}
            coauthName2aid = {}
            
            # Process each paper's coauthors
            for _, paper in year_papers.iterrows():
                if pd.isna(paper['authors']):
                    continue
                
                for coauthor_name in paper['authors'].split(", "):
                    if coauthor_name != target_name:
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
                        
                        if coauthor_name not in set_all_collabs:
                            new_collabs_this_year.add(coauthor_name)
            
            # Create coauthor records for this year
            for coauthor_name, coauthor_data in time_collabo.items():
                coauthor_aid = coauthName2aid[coauthor_name]
                
                if (target_aid, coauthor_aid, yr) in existing_records:
                    continue
                
                subtype = "new_collab" if coauthor_name in new_collabs_this_year else "existing_collab"
                
                all_coauthors.append((
                    target_aid, f"{yr}-01-01", yr, coauthor_aid, coauthor_name,
                    subtype, coauthor_data['count'], all_time_collabo[coauthor_name],
                    None, None
                ))
            
            set_all_collabs.update(new_collabs_this_year)
        
        # Save coauthor records
        if all_coauthors:
            db_exporter.save_coauthors(all_coauthors)
            total_new_records += len(all_coauthors)
    
    db_exporter.close()
    return f"Created {total_new_records} new coauthor records"


@dg.asset(deps=[process_coauthor_relationships])
def export_coauthors_from_db():
    """Export coauthor relationships from database."""
    db_exporter = DatabaseExporter(str(DATABASE_PATH))
    
    query = """
        SELECT 
            c.pub_year, c.pub_date::CHAR as pub_date,
            ego_a.aid, ego_a.institution, ego_a.display_name as name, 
            ego_a.author_age, c.yearly_collabo, c.all_times_collabo, 
            c.acquaintance, coauth.aid as coauth_aid, 
            coauth.display_name as coauth_name, coauth.author_age as coauth_age,
            (coauth.author_age - ego_a.author_age) AS age_diff
        FROM coauthor2 c
        LEFT JOIN author coauth ON c.coauthor_aid = coauth.aid AND c.pub_year = coauth.pub_year
        LEFT JOIN author ego_a ON c.ego_aid = ego_a.aid AND c.pub_year = ego_a.pub_year
        WHERE c.pub_year < 2024
    """
    
    df = db_exporter.con.sql(query).fetchdf()
    db_exporter.close()
    
    if len(df) == 0:
        return "No coauthor relationships found"
    
    # Filter valid records
    df = df[~df.author_age.isna()].reset_index(drop=True)
    df['author_age'] = df.author_age.astype(int)
    
    # Create age buckets
    df['age_bucket'] = pd.cut(
        df['age_diff'], 
        bins=[-float('inf'), -15, -7, 7, 15, float('inf')],
        labels=['much_younger', 'younger', 'same_age', 'older', 'much_older']
    )
    
    # Create age standardization
    df['age_std'] = df['author_age'].apply(
        lambda age: f"1{str(age).zfill(3)}-01-01"
    )
    
    df.to_parquet("data/processed/coauthor.parquet")
    return f"Exported {len(df)} coauthor relationships"


@dg.asset(deps=[process_coauthor_relationships])
def export_authors_from_db():
    """Export author records from database."""
    db_exporter = DatabaseExporter(str(DATABASE_PATH))
    
    df = db_exporter.con.sql("SELECT * FROM author").fetchdf()
    db_exporter.close()
    
    if len(df) == 0:
        return "No author records found"
    
    # Create age standardization
    df['age_std'] = df['author_age'].apply(
        lambda age: f"1{str(int(age)).zfill(3)}-01-01" if not pd.isna(age) else None
    )
    
    df.to_parquet("data/processed/author.parquet")
    return f"Exported {len(df)} author records"


# Define the assets for Dagster
defs = dg.Definitions(
    assets=[
        researchers_tsv,
        database_setup,
        fetch_researcher_papers,
        export_papers_from_db,
        process_coauthor_relationships,
        export_coauthors_from_db,
        export_authors_from_db
    ]
)