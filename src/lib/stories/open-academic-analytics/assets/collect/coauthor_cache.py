"""
research_analysis.py

Stage 2: Core research analysis - career profiles and collaboration networks
"""
from tqdm import tqdm
import dagster as dg
from dagster import MaterializeResult, MetadataValue
from dagster_duckdb import DuckDBResource

from config import config
from modules.database_adapter import DatabaseExporterAdapter
from modules.data_fetcher import OpenAlexFetcher
from modules.author_processor import AuthorProcessor

@dg.asset(
    deps=["academic_publications"],
    group_name="collect",
    description="👩‍🎓 Build researcher career profiles: publication history, ages, institutional affiliations"
)
def coauthor_cache(duckdb: DuckDBResource):
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