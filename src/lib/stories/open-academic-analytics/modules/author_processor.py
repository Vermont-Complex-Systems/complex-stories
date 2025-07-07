"""
Author processing module for the coauthorship analysis pipeline
"""
import logging
import pandas as pd


logger = logging.getLogger(__name__)

class AuthorProcessor:
    """Class to process author information"""
    
    def __init__(self):
        self.publication_year_cache = {}  
    
    def load_cache_from_file(self, cache_file):
        """Load persistent cache into memory at start of processing"""
        if cache_file.exists():
            cache_df = pd.read_parquet(cache_file)
            for _, row in cache_df.iterrows():
                if pd.notna(row['first_pub_year']) and pd.notna(row['last_pub_year']):
                    self.publication_year_cache[row['aid']] = (
                        int(row['first_pub_year']), 
                        int(row['last_pub_year'])
                    )
            print(f"Loaded {len(self.publication_year_cache)} entries from cache")


    def save_cache_to_file(self, cache_file):
        """Save in-memory cache to persistent file at end of processing"""
        cache_data = []
        for aid, (first_year, last_year) in self.publication_year_cache.items():
            cache_data.append({
                'aid': aid,
                'first_pub_year': first_year,
                'last_pub_year': last_year
            })
        
        if cache_data:
            cache_df = pd.DataFrame(cache_data)
            cache_file.parent.mkdir(exist_ok=True)
            cache_df.to_parquet(cache_file)
            print(f"Saved {len(cache_data)} entries to cache")
    
    def collect_author_info(self, target_id, target_name, year_range, papers, coauthors, openAlex_fetcher):
        """
        Process author information from papers and coauthorships.
        
        Args:
            target_id (str): OpenAlex author ID for target researcher
            target_name (str): Display name for target researcher
            year_range (tuple): (min_year, max_year)
            papers (list): Processed paper tuples
            coauthors (list): Processed coauthor tuples
            openAlex_fetcher (OpenAlexFetcher): API fetcher
            
        Returns:
            list: Processed author info tuples
        """
        min_yr, max_yr = year_range
        authors = {}
        
        # Make sure we have the current author in the cache
        self.publication_year_cache[target_id] = (min_yr, max_yr)
        
        # Extract author info from papers
        paper_authors = []
        for paper in papers:
            # Extract relevant fields from paper tuple
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
        
        # Extract author info from coauthors
        coauth_authors = []
        for coauthor in coauthors:
            # Extract relevant fields from coauthor tuple
            # Structure: (ego_aid, pub_date, pub_year, coauthor_aid, coauthor_name, ...)
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
            
            # For the target author, we already know min_yr and max_yr
            if aid == target_id:
                author_age = year - min_yr
                authors[(aid, year)] = (
                    aid, display_name, institution,
                    year, min_yr, max_yr, author_age
                )
                continue
            
            # For other authors, try to get from cache first
            if aid in self.publication_year_cache:
                coauthor_min_yr, coauthor_max_yr = self.publication_year_cache[aid]
                author_age = year - coauthor_min_yr if coauthor_min_yr is not None else None
                
                authors[(aid, year)] = (
                    aid, display_name, institution,
                    year, coauthor_min_yr, coauthor_max_yr, author_age
                )
                continue
            
            # If not in cache, try to fetch from OpenAlex
            try:
                # Get publication range
                coauthor_min_yr, coauthor_max_yr = openAlex_fetcher.get_publication_range(aid)
                
                # Calculate author age
                author_age = year - coauthor_min_yr if coauthor_min_yr is not None else None
                
                # Update in-memory cache (fast lookups during this run)
                self.publication_year_cache[aid] = (coauthor_min_yr, coauthor_max_yr)
                
                # Add to authors dictionary
                authors[(aid, year)] = (
                    aid, display_name, institution,
                    year, coauthor_min_yr, coauthor_max_yr, author_age
                )
                
            except Exception as e:
                logger.warning(f"Failed to get publication range for {display_name} ({aid}): {str(e)}")
                failed_authors.append(aid)
                
                # Add with None values for min/max years and age
                authors[(aid, year)] = (
                    aid, display_name, institution,
                    year, None, None, None
                )
        
        return list(authors.values())