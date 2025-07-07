"""
research_analysis.py

Stage 2: Core research analysis - career profiles and collaboration networks
"""
from tqdm import tqdm
import dagster as dg
from dagster import MaterializeResult, MetadataValue
import pandas as pd
import duckdb
import logging

from config import config
from modules.data_fetcher import OpenAlexFetcher

logger = logging.getLogger(__name__)


def extract_coauthor_info(papers_list, target_name):
    """Extract coauthor information from paper author lists."""
    coauthor_info = []
    
    for paper in papers_list:
        pub_year = paper[4]
        author_list = paper[9]  # authors column
        institution = paper[12] if len(paper) > 12 else None
        
        if not author_list:
            continue
            
        try:
            author_names = author_list.split(", ")
            for author_name in author_names:
                if author_name.strip() != target_name.strip():
                    coauthor_info.append({
                        'name': author_name.strip(),
                        'year': pub_year,
                        'institution': institution
                    })
        except Exception as e:
            print(f"      Error extracting coauthors: {e}")
    
    return coauthor_info

def resolve_coauthor_ids(coauthor_info, target_aid, existing_authors_df, fetcher):
    """Resolve coauthor names to OpenAlex IDs using cache + API."""
    coauthors_with_ids = []
    
    # Build name lookup from existing author profiles
    name_to_aid = {}
    if existing_authors_df is not None:
        name_to_aid = existing_authors_df.groupby('display_name')['aid'].first().to_dict()
        print(f"      📋 Loaded {len(name_to_aid)} name-to-ID mappings from cache")
    
    for info in coauthor_info:
        try:
            coauthor_name = info['name']
            
            # Check cache first
            coauthor_aid = name_to_aid.get(coauthor_name)
            
            # If not in cache, fetch from OpenAlex API
            if coauthor_aid is None:
                try:
                    result = fetcher.get_author_info_by_name(coauthor_name)
                    if result and ('id' in result or 'aid' in result):
                        coauthor_id_raw = result.get('id') or result.get('aid')
                        coauthor_aid = coauthor_id_raw.split('/')[-1] if isinstance(coauthor_id_raw, str) else str(coauthor_id_raw)
                        name_to_aid[coauthor_name] = coauthor_aid  # Cache for this run
                except Exception as e:
                    print(f"      Failed to fetch {coauthor_name}: {e}")
                    continue
            
            if coauthor_aid:
                pub_date = f"{info['year']}-01-01"
                coauthor_tuple = (
                    target_aid, pub_date, info['year'],
                    coauthor_aid, coauthor_name, "from_paper",
                    1, 1, None, info.get('institution')
                )
                coauthors_with_ids.append(coauthor_tuple)
                
        except Exception as e:
            print(f"      Error processing coauthor {info.get('name', 'Unknown')}: {e}")
    
    return coauthors_with_ids


@dg.asset(
    deps=["academic_publications"],
    group_name="collect",
    description="👩‍🎓 Build researcher career profiles: publication history, ages, institutional affiliations"
)
def coauthor_cache():
    """
    Build comprehensive author profiles from papers.
    author_profiles.parquet serves as our single cache of all authors ever encountered.
    """
    print("🚀 Starting researcher career analysis...")
    
    # File paths - clear HRDAG flow
    papers_file = config.data_raw_path / config.paper_output_file
    output_file = config.data_raw_path / config.author_output_file
    
    # Load papers from previous stage
    print(f"📖 Loading papers from {papers_file}")
    papers_df = pd.read_parquet(papers_file)
    print(f"   Found {len(papers_df)} papers")
    
    # Load existing author profiles
    existing_authors_df = None
    publication_year_cache = {}
    if output_file.exists():
        print(f"📚 Loading existing author profiles from {output_file}")
        existing_authors_df = pd.read_parquet(output_file)
        print(f"   Found {len(existing_authors_df)} existing author records")
        print(f"   Covering {existing_authors_df['aid'].nunique()} unique authors")
        
        # Build publication year cache
        for _, row in existing_authors_df.iterrows():
            if pd.notna(row['first_pub_year']) and pd.notna(row['last_pub_year']):
                publication_year_cache[row['aid']] = (
                    int(row['first_pub_year']), 
                    int(row['last_pub_year'])
                )
        print(f"   Loaded {len(publication_year_cache)} entries into publication year cache")
    
    fetcher = OpenAlexFetcher()
    
    # Find all researchers with papers
    researchers = duckdb.sql("""
        SELECT DISTINCT ego_aid, ego_display_name, 
               MIN(pub_year) as min_year, MAX(pub_year) as max_year
        FROM papers_df 
        GROUP BY ego_aid, ego_display_name
    """).fetchall()
    
    print(f"🔍 Found {len(researchers)} researchers to process")
    
    # Development mode filtering
    if config.target_researcher:
        researchers = [r for r in researchers if r[0] == config.target_researcher]
        print(f"🎯 DEV MODE: Processing only {config.target_researcher}")
    elif config.max_researchers:
        researchers = researchers[:config.max_researchers]
        print(f"🔧 DEV MODE: Processing first {config.max_researchers} researchers")
    
    # Process each researcher
    all_author_records = []
    total_coauthors_found = 0
    
    for target_aid, target_name, min_year, max_year in tqdm(researchers, desc="Processing researchers"):
        print(f"\n👤 Processing {target_name} ({target_aid}) - {min_year} to {max_year}")
        
        # Add target author to cache
        publication_year_cache[target_aid] = (min_year, max_year)
        
        # Get papers for this researcher
        researcher_papers = duckdb.sql("""
            SELECT * FROM papers_df 
            WHERE ego_aid = $1 
            ORDER BY pub_year
        """, params=[target_aid]).df()
        
        papers_list = [tuple(row) for _, row in researcher_papers.iterrows()]
        print(f"   📄 {len(papers_list)} papers")
        
        # Extract coauthor information from paper author lists
        coauthor_info = extract_coauthor_info(papers_list, target_name)
        print(f"   👥 {len(coauthor_info)} coauthor instances found")
        
        # Resolve coauthor names to IDs
        coauthors_with_ids = resolve_coauthor_ids(coauthor_info, target_aid, existing_authors_df, fetcher)
        print(f"   🆔 {len(coauthors_with_ids)} coauthors with OpenAlex IDs")
        total_coauthors_found += len(coauthors_with_ids)
        
        # Collect all authors (target + coauthors) for processing
        authors = {}
        
        # Process papers to get author info
        for paper in papers_list:
            ego_aid = paper[0]
            ego_display_name = paper[1]
            pub_year = paper[4]
            ego_institution = paper[12]
            
            if (ego_aid, pub_year) not in authors:
                if ego_aid == target_aid:
                    author_age = pub_year - min_year
                    authors[(ego_aid, pub_year)] = (
                        ego_aid, ego_display_name, ego_institution,
                        pub_year, min_year, max_year, author_age
                    )
        
        # Process coauthors
        for coauthor in coauthors_with_ids:
            coauthor_aid = coauthor[3]
            coauthor_name = coauthor[4]
            pub_year = coauthor[2]
            coauthor_institution = coauthor[9]
            
            if (coauthor_aid, pub_year) not in authors:
                # Try to get from cache first
                if coauthor_aid in publication_year_cache:
                    coauthor_min_yr, coauthor_max_yr = publication_year_cache[coauthor_aid]
                    author_age = pub_year - coauthor_min_yr if coauthor_min_yr is not None else None
                    
                    authors[(coauthor_aid, pub_year)] = (
                        coauthor_aid, coauthor_name, coauthor_institution,
                        pub_year, coauthor_min_yr, coauthor_max_yr, author_age
                    )
                else:
                    # Fetch from OpenAlex
                    try:
                        coauthor_min_yr, coauthor_max_yr = fetcher.get_publication_range(coauthor_aid)
                        author_age = pub_year - coauthor_min_yr if coauthor_min_yr is not None else None
                        
                        # Update cache
                        publication_year_cache[coauthor_aid] = (coauthor_min_yr, coauthor_max_yr)
                        
                        authors[(coauthor_aid, pub_year)] = (
                            coauthor_aid, coauthor_name, coauthor_institution,
                            pub_year, coauthor_min_yr, coauthor_max_yr, author_age
                        )
                    except Exception as e:
                        logger.warning(f"Failed to get publication range for {coauthor_name} ({coauthor_aid}): {str(e)}")
                        
                        authors[(coauthor_aid, pub_year)] = (
                            coauthor_aid, coauthor_name, coauthor_institution,
                            pub_year, None, None, None
                        )
        
        author_records = list(authors.values())
        all_author_records.extend(author_records)
        print(f"   💾 Generated {len(author_records)} author profile records")
    
    # Save updated author profiles
    if all_author_records:
        author_columns = ['aid', 'display_name', 'institution', 'pub_year', 
                         'first_pub_year', 'last_pub_year', 'author_age']
        new_profiles_df = pd.DataFrame(all_author_records, columns=author_columns)
        
        print(f"💾 Saving {len(new_profiles_df)} author profile records to {output_file}")
        new_profiles_df.to_parquet(output_file)
    
    print(f"\n🎉 Career analysis completed!")
    print(f"   👥 {len(researchers)} researchers processed")
    print(f"   🤝 {total_coauthors_found} total coauthor relationships identified")
    print(f"   📊 {len(all_author_records)} author profile records generated")
    
    return MaterializeResult(
        metadata={
            "researchers_processed": MetadataValue.int(len(researchers)),
            "coauthor_relationships": MetadataValue.int(total_coauthors_found),
            "author_records_generated": MetadataValue.int(len(all_author_records)),
            "output_file": MetadataValue.path(str(output_file)),
            "input_file": MetadataValue.path(str(papers_file)),
            "unique_authors": MetadataValue.int(new_profiles_df['aid'].nunique() if all_author_records else 0),
            "research_value": MetadataValue.md(
                "**Author career database** - comprehensive profiles of all researchers and "
                "coauthors encountered, with age/career stage data for collaboration analysis."
            )
        }
    )