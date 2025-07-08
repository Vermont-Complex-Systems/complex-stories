"""
research_analysis.py

Stage 2: Core research analysis - career profiles and collaboration networks
"""
import pandas as pd
from tqdm import tqdm
import dagster as dg
from dagster import MaterializeResult, MetadataValue
from dagster_duckdb import DuckDBResource

from config import config
from shared.database.database_adapter import DatabaseExporterAdapter
from shared.clients.openalex_api_client import OpenAlexFetcher


@dg.asset(
    deps=["researcher_list","academic_publications"],
    group_name="import",
    description="👩‍🎓 Build researcher career profiles: publication history, ages, institutional affiliations"
)
def coauthor_cache(duckdb: DuckDBResource):
    """
    Extract and process researcher career information from collected papers.
    This creates the foundation for age-based collaboration analysis.
    """
    print("🚀 Starting researcher career analysis...")
    
    paper_file = config.data_raw_path / config.paper_output_file
    author_file = config.data_raw_path / config.author_output_file
    excel_file = config.data_raw_path / config.researchers_tsv_file
    output_file = config.data_raw_path / config.author_output_file

    # Load known corrections
    target_aids = pd.read_csv(excel_file, sep="\t")
    target_aids = target_aids[~target_aids['oa_uid'].isna()]
    known_years_df = target_aids[['oa_uid', 'first_pub_year']].dropna()
    known_first_pub_years = {k.upper(): int(v) for k, v in known_years_df.values}
    print(f"📝 Loaded {len(known_first_pub_years)} known publication year corrections")

    with duckdb.get_connection() as conn:
        print(f"✅ Connected to database")
        
        # Load papers from target authors
        df_pap = pd.read_parquet(paper_file)
        conn.execute("CREATE TABLE paper AS SELECT * FROM df_pap")

        # Load cached author information if exists
        if author_file.exists():
            df_author = pd.read_parquet(author_file)
                        
            conn.execute("""
                CREATE TABLE IF NOT EXISTS author (
                    aid VARCHAR,
                    display_name VARCHAR,
                    institution VARCHAR,
                    pub_year INT,
                    first_pub_year INT,
                    last_pub_year INT,
                    PRIMARY KEY(aid, pub_year)
                )
            """)
            
            conn.execute("INSERT INTO author SELECT * FROM df_author")
        
        # Initialize components
        db_exporter = DatabaseExporterAdapter(conn)
        fetcher = OpenAlexFetcher()
        
        # Build publication year cache from existing data
        print("Building publication year cache...")
        query = """
            SELECT aid, first_pub_year, last_pub_year 
            FROM author 
            WHERE first_pub_year IS NOT NULL AND last_pub_year IS NOT NULL
        """
        results = db_exporter.con.execute(query).fetchall()
        publication_year_cache = {}
        
        for result in results:
            aid, min_year, max_year = result
            publication_year_cache[aid] = (min_year, max_year)
        
        print(f"  📊 Cached publication years for {len(publication_year_cache)} authors")
        
        # Get researchers that have papers
        researchers_with_papers = db_exporter.con.execute("""
            SELECT DISTINCT ego_aid, ego_display_name, 
                   MIN(pub_year) as oa_min_year, 
                   MAX(pub_year) as oa_max_year
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
        
        for target_aid, target_name, oa_min_yr, oa_max_yr in tqdm(researchers_with_papers, desc="Processing careers"):    
            print(f"\n👥 Processing career data for {target_name} ({target_aid})")
            
            # Apply known corrections first
            if target_aid in known_first_pub_years:
                corrected_first_year = known_first_pub_years[target_aid]
                print(f"  ✏️  Using corrected first publication year: {corrected_first_year} (was {oa_min_yr})")
                
                # Use corrected year range
                actual_min_yr = corrected_first_year
                actual_max_yr = oa_max_yr
                
                # Update cache immediately
                publication_year_cache[target_aid] = (actual_min_yr, actual_max_yr)
                
                # Update database with correction
                db_exporter.con.execute("""
                    UPDATE author 
                    SET first_pub_year = ? 
                    WHERE aid = ?
                """, (corrected_first_year, target_aid))
                
            else:
                print(f"  📅 Using OA publication range: {oa_min_yr}-{oa_max_yr}")
                actual_min_yr = oa_min_yr
                actual_max_yr = oa_max_yr
                publication_year_cache[target_aid] = (actual_min_yr, actual_max_yr)
            
            # Get papers for this researcher - FILTERED by corrected year range
            papers_query = """
                SELECT * FROM paper 
                WHERE ego_aid = ? AND pub_year >= ?
                ORDER BY pub_year
            """
            papers_df = db_exporter.con.execute(papers_query, (target_aid, actual_min_yr)).fetchdf()
            papers = [tuple(row) for _, row in papers_df.iterrows()]
            
            print(f"  📄 Found {len(papers)} valid papers spanning {actual_min_yr}-{actual_max_yr}")
            
            # Extract coauthor information from valid papers
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
                        print(f"    ⚠️  Error extracting coauthors from paper: {e}")
            
            print(f"  🤝 Extracted {len(coauthor_info)} coauthor records from papers")
            
            # Get coauthor IDs from OpenAlex 
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
                    print(f"    ⚠️  Error processing coauthor {info.get('name', 'Unknown')}: {e}")

            print(f"  🔍 Found {len(coauthors_with_ids)} coauthors with OpenAlex IDs")
            total_coauthors_identified += len(coauthors_with_ids)

            # Build author records
            authors = {}
            
            # Process target author records
            paper_authors = []
            for paper in papers:
                ego_aid = paper[0]
                ego_display_name = paper[1]
                pub_year = paper[4]
                ego_institution = paper[12]
                
                paper_authors.append({
                    'aid': ego_aid,
                    'display_name': ego_display_name,
                    'institution': ego_institution,
                    'pub_year': pub_year
                })
            
            # Process coauthor records
            coauth_authors = []
            for coauthor in coauthors_with_ids:
                coauth_authors.append({
                    'aid': coauthor[3],  # coauthor_aid
                    'display_name': coauthor[4],  # coauthor_name
                    'institution': coauthor[9],  # coauthor_institution
                    'pub_year': coauthor[2]  # pub_year
                })
            
            # Combine and deduplicate
            all_authors_df = pd.DataFrame(paper_authors + coauth_authors).drop_duplicates()
            
            # Process each unique author
            failed_authors = []
            
            for _, row in all_authors_df.iterrows():
                aid = row['aid']
                year = row['pub_year']
                display_name = row['display_name']
                institution = row['institution']
                
                # Skip if we already have this author-year combination
                if (aid, year) in authors:
                    continue
                
                # For the target author, we know the corrected range
                if aid == target_aid:
                    authors[(aid, year)] = (
                        aid, display_name, institution,
                        year, actual_min_yr, actual_max_yr
                    )
                    continue
                
                # For other authors, try to get from cache first
                if aid in publication_year_cache:
                    coauthor_min_yr, coauthor_max_yr = publication_year_cache[aid]
                    
                    authors[(aid, year)] = (
                        aid, display_name, institution,
                        year, coauthor_min_yr, coauthor_max_yr
                    )
                    continue
                
                # If not in cache, fetch from OpenAlex
                try:
                    coauthor_min_yr, coauthor_max_yr = fetcher.get_publication_range(aid)
                    
                    # Update cache
                    publication_year_cache[aid] = (coauthor_min_yr, coauthor_max_yr)
                    
                    # Add to authors dictionary
                    authors[(aid, year)] = (
                        aid, display_name, institution,
                        year, coauthor_min_yr, coauthor_max_yr
                    )
                except Exception as e:
                    failed_authors.append(aid)
                    
                    # Add with None values for missing data
                    authors[(aid, year)] = (
                        aid, display_name, institution,
                        year, None, None
                    )
            
            author_records = list(authors.values())
            
            if author_records:
                print(f"  💾 Saving {len(author_records)} author career records")
                db_exporter.save_authors(author_records)
                total_author_records += len(author_records)
            else:
                print("  📭 No author career records to save")

        # Export final results
        db_exporter.con.sql("SELECT * FROM author").df().to_parquet(output_file)
        
        print(f"\n🎉 Career analysis completed!")
        print(f"  👥 Total author career records: {total_author_records}")
        print(f"  🤝 Total coauthors identified: {total_coauthors_identified}")
        print(f"  ✏️  Applied {len(known_first_pub_years)} publication year corrections")
        
        return MaterializeResult(
            metadata={
                "researchers_analyzed": MetadataValue.int(len(researchers_with_papers)),
                "career_records_created": MetadataValue.int(total_author_records),
                "coauthors_identified": MetadataValue.int(total_coauthors_identified),
                "corrections_applied": MetadataValue.int(len(known_first_pub_years)),
                "data_source": MetadataValue.url("https://openalex.org"),
                "input_file": MetadataValue.path(str(paper_file)),
                "output_file": MetadataValue.path(str(output_file)),
                "analysis_approach": MetadataValue.md(
                    "**Career stage analysis** using corrected publication timing. "
                    "Invalid papers before corrected first publication year are filtered out."
                ),
                "research_value": MetadataValue.md(
                    "**Critical foundation** for collaboration analysis with data quality corrections. "
                    "Maps researcher career trajectories using verified publication ranges."
                )
            }
        )