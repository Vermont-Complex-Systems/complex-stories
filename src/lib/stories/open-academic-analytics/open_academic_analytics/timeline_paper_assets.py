"""
Simplified timeline_paper_assets.py
"""
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import dagster as dg
from dagster_duckdb import DuckDBResource

from config import config
from modules.database_adapter import DatabaseExporterAdapter
from modules.data_fetcher import OpenAlexFetcher
from modules.author_processor import AuthorProcessor
from modules.utils import shuffle_date_within_month

@dg.asset
def researchers_tsv_timeline_paper():
    """Convert researchers parquet to TSV format"""
    input_file = config.DATA_RAW_DIR / config.RESEARCHERS_INPUT_FILE
    output_file = config.DATA_RAW_DIR / config.RESEARCHERS_TSV_FILE

    # Load and process
    d = pd.read_parquet(input_file)
    
    # Handle column name variations
    if 'host_dept (; delimited if more than one)' in d.columns:
        d = d.rename(columns={'host_dept (; delimited if more than one)': 'host_dept'})
    
    # Select and save
    cols = ['oa_display_name', 'is_prof', 'group_size', 'perceived_as_male', 
            'host_dept', 'has_research_group', 'oa_uid', 'group_url', 'first_pub_year']
    
    d[cols].to_csv(output_file, sep="\t", index=False)
    
    print(f"✅ Created {output_file} with {len(d)} researchers")
    return f"Processed {len(d)} researchers"

@dg.asset(deps=[researchers_tsv_timeline_paper])
def timeline_paper_main(duckdb: DuckDBResource):
    """Main timeline-paper processing"""
    
    print("🚀 Starting timeline-paper import...")
    
    with duckdb.get_connection() as conn:
        db_exporter = DatabaseExporterAdapter(conn)
        print(f"✅ Connected to database")
        
        # Load researchers
        researchers_file = config.DATA_RAW_DIR / config.RESEARCHERS_TSV_FILE
        target_aids = pd.read_csv(researchers_file, sep="\t")
        target_aids = target_aids[~target_aids['oa_uid'].isna()]
        target_aids['oa_uid'] = target_aids['oa_uid'].str.upper()
        
        print(f"Found {len(target_aids)} researchers with OpenAlex IDs")
        
        # Development mode: limit to specific researcher
        if config.TARGET_RESEARCHER:
            target_aids = target_aids[target_aids['oa_uid'] == config.TARGET_RESEARCHER]
            print(f"🎯 DEV MODE: Processing {config.TARGET_RESEARCHER}")
        elif config.MAX_RESEARCHERS:
            target_aids = target_aids.head(config.MAX_RESEARCHERS)
            print(f"🔧 DEV MODE: Processing first {config.MAX_RESEARCHERS} researchers")
        
        if len(target_aids) == 0:
            return "❌ No researchers found"

        # Initialize modules
        fetcher = OpenAlexFetcher()
        author_processor = AuthorProcessor(db_exporter)
        author_processor.preload_publication_years()

        total_papers_saved = 0
        total_researchers_processed = 0
        
        for i, row in tqdm(target_aids.iterrows(), total=len(target_aids)):
            target_aid = row['oa_uid']
            
            # Get display name
            try:
                author_obj = fetcher.get_author_info(target_aid)
                target_name = author_obj['display_name']
            except Exception as e:
                print(f"Error getting name for {target_aid}: {e}")
                target_name = target_aid
                
            print(f"\n👤 Processing {target_name} ({target_aid})")

            # Get publication year range
            try:
                min_yr, _ = fetcher.get_publication_range(target_aid)
                author_info = fetcher.get_author_info(target_aid)
                max_yr = author_info['counts_by_year'][0]['year']
                print(f"Years: {min_yr}-{max_yr}")
            except Exception as e:
                print(f"Error getting years for {target_name}: {e}")
                continue
            
            # Store in cache
            author_processor.publication_year_cache[target_aid] = (min_yr, max_yr)

            # Check if up to date (skip if not forcing update)
            if not config.FORCE_UPDATE and db_exporter.is_up_to_date(target_aid, min_yr, max_yr):
                print(f"✅ {target_name} is up to date")
                total_researchers_processed += 1
                continue
            
            # Get existing papers
            paper_cache, _ = db_exporter.get_author_cache(target_aid)
            existing_papers = set([(aid, wid) for aid, wid in paper_cache])
            
            # Process papers for each year
            papers = []
            for yr in range(min_yr, max_yr + 1):
                print(f"  📅 Processing {yr}...")
                
                publications = fetcher.get_publications(target_aid, yr)
                if not publications:
                    continue
                    
                print(f"  Found {len(publications)} publications")
                ego_institutions_this_year = []
                
                for w in publications:
                    if w.get('language') != 'en':
                        continue
                        
                    wid = w['id'].split("/")[-1]
                    
                    if not config.FORCE_UPDATE and (target_aid, wid) in existing_papers:
                        continue
                    
                    # Add date noise for visualization
                    shuffled_date = shuffle_date_within_month(w['publication_date'])
                    
                    # Process authorships
                    author_position = None
                    for authorship in w['authorships']:
                        if authorship['author']['id'].split("/")[-1] == target_aid:
                            ego_institutions_this_year += [i['display_name'] for i in authorship['institutions']]
                            author_position = authorship['author_position']
                    
                    # Determine institution
                    from collections import Counter
                    target_institution = None
                    if ego_institutions_this_year:
                        target_institution = Counter(ego_institutions_this_year).most_common(1)[0][0]
                    
                    # Extract metadata
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
            
            # Save papers
            if papers:
                print(f"💾 Saving {len(papers)} papers")
                db_exporter.save_papers(papers)
                total_papers_saved += len(papers)
                
                # Process author information
                print(f"👥 Processing author info")
                coauthor_info = []
                for paper in papers:
                    pub_year = paper[4]
                    if paper[9]:  # coauthors
                        coauthor_names = paper[9].split(", ")
                        for coauthor_name in coauthor_names:
                            if coauthor_name != target_name:
                                coauthor_info.append({
                                    'name': coauthor_name,
                                    'year': pub_year,
                                    'institution': paper[12]
                                })
                
                # Get coauthor IDs
                coauthors_with_ids = []
                for info in coauthor_info:
                    try:
                        if not info.get('name') or not info.get('year'):
                            continue
                            
                        # Check cache first
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

                print(f"  Found {len(coauthors_with_ids)} coauthors with IDs")

                # Process author records
                author_records = author_processor.collect_author_info(
                    target_aid, target_name, (min_yr, max_yr),
                    papers, coauthors_with_ids, fetcher
                )
                
                if author_records:
                    print(f"  💾 Saving {len(author_records)} author records")
                    db_exporter.save_authors(author_records)

            total_researchers_processed += 1

        print(f"\n🎉 Complete! Processed {total_researchers_processed} researchers, saved {total_papers_saved} papers")
        return f"Processed {total_researchers_processed} researchers, saved {total_papers_saved} papers"