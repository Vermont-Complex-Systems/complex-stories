"""
Paper processing module for the coauthorship analysis pipeline
"""
import logging
import os
import sys
from collections import Counter

# Add the project root to the path
# This makes imports work regardless of how the script is called
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    # Import modules
    from scripts.modules.utils import shuffle_date_within_month
except ImportError as e:
    # Fallback to direct import
    try:
        # Get the path to the modules directory
        modules_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules'))
        sys.path.insert(0, modules_dir)
        from utils import shuffle_date_within_month
    except ImportError as e2:
        print(f"Failed to import modules: {e2}")
        print("Current sys.path:", sys.path)
        print("Make sure the modules directory is correctly set up.")
        raise

logger = logging.getLogger(__name__)

class PaperProcessor:
    """Class to process paper information for an author"""
    
    def __init__(self, db_exporter):
        """
        Initialize with database exporter.
        
        Args:
            db_exporter (DatabaseExporter): Database connection handler
        """
        self.db_exporter = db_exporter
    
    def process_publications(self, author_id, display_name, year_range, paper_cache, openAlex_fetcher):
        """
        Process all publications for an author within a year range.
        
        Args:
            author_id (str): OpenAlex author ID
            display_name (str): Author display name
            year_range (tuple): (min_year, max_year)
            paper_cache (list): List of existing papers in database
            openAlex_fetcher (OpenAlexFetcher): API fetcher
            
        Returns:
            list: Processed paper tuples
        """
        min_yr, max_yr = year_range
        papers = []
        
        # Process each year in range
        for yr in range(min_yr, max_yr + 1):
            logger.info(f"Processing year {yr} for {display_name}")
            
            # Each year, ego can have multiple institutions
            ego_institutions_this_year = []
            
            # Query OpenAlex for publications in this year
            publications = openAlex_fetcher.get_publications(author_id, yr)
            
            if not publications:
                logger.info(f"No publications found for {display_name} in {yr}")
                continue
                
            logger.info(f"Found {len(publications)} publications for {display_name} in {yr}")
            
            # Process each publication
            for work in publications:
                # Find author position and institutions
                target_position = None
                
                for authorship in work['authorships']:
                    coauthor_name = authorship['author']['display_name']
                    
                    if coauthor_name == display_name or authorship['author']['id'].split("/")[-1] == author_id:
                        ego_institutions_this_year += [i['display_name'] for i in authorship['institutions']]
                        target_position = authorship['author_position']
                
                # Determine target institution through majority vote
                target_institution = None
                if len(ego_institutions_this_year) > 0:
                    target_institution = Counter(ego_institutions_this_year).most_common(1)[0][0]
                
                # Extract work ID and check if already in database
                wid = work['id'].split("/")[-1]
                if (author_id, wid) in paper_cache:
                    continue
                
                # Add some noise within year for visualization purpose
                shuffled_date = shuffle_date_within_month(work['publication_date'])
                
                # Extract other metadata
                doi = work['ids']['doi'] if 'doi' in work['ids'] else None
                fos = work['primary_topic'].get('display_name') if work.get('primary_topic') else None
                coauthors = ', '.join([a['author']['display_name'] for a in work['authorships']])
                
                # Create paper record
                papers.append((
                    author_id, display_name, wid,
                    shuffled_date, int(work['publication_year']),
                    doi, work['title'], work['type'], fos,
                    coauthors,
                    work['cited_by_count'],
                    target_position,
                    target_institution
                ))
        
        return papers
    
    def filter_publications(self, papers):
        """
        Filter out publications that don't meet criteria.
        
        Args:
            papers (list): List of paper tuples
            
        Returns:
            list: Filtered paper tuples
        """
        filtered_papers = []
        
        for paper in papers:
            # Unpack for easier access
            _, _, _, _, _, _, title, work_type, _, _, _, _, _ = paper
            
            # Filter based on work type
            accepted_work_types = ['article', 'preprint', 'book-chapter', 'book', 'report']
            if work_type not in accepted_work_types:
                continue
            
            # Filter out works mislabeled as articles
            if title and title.lower():
                lower_title = title.lower()
                skip = False
                
                for pattern in [
                    "^table", "appendix", "issue cover", "this week in science",
                    "^figure ", "^data for ", "^author correction: ",
                    "supporting information", "^supplementary material",
                    "^list of contributors"
                ]:
                    if pattern in lower_title:
                        skip = True
                        break
                
                if skip:
                    continue
            
            filtered_papers.append(paper)
        
        return filtered_papers
    
    def process(self, author_id, display_name, year_range, openAlex_fetcher):
        """
        Process and save all paper data for an author.
        
        Args:
            author_id (str): OpenAlex author ID
            display_name (str): Author display name
            year_range (tuple): (min_year, max_year)
            openAlex_fetcher (OpenAlexFetcher): API fetcher
            
        Returns:
            list: Processed paper tuples
        """
        # Get existing papers from database
        paper_cache, _ = self.db_exporter.get_author_cache(author_id)
        
        # Process publications
        papers = self.process_publications(
            author_id, display_name, year_range, paper_cache, openAlex_fetcher
        )
        
        # Filter publications
        filtered_papers = self.filter_publications(papers)
        
        # Save to database
        self.db_exporter.save_papers(filtered_papers)
        
        return filtered_papers