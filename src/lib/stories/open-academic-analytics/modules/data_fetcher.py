"""
Module for extracting researcher data from OpenAlex API
"""
from itertools import chain
import logging
import time
from pyalex import Works, Authors

logger = logging.getLogger(__name__)

class OpenAlexFetcher:
    """Class to handle all OpenAlex API interactions"""
    
    def __init__(self, rate_limit=10):
        """
        Initialize the fetcher with rate limiting.
        
        Args:
            rate_limit (int): Maximum requests per second
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Apply rate limiting to API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.rate_limit
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_publication_range(self, author_id, known_first_pub_year=None):
        """
        Get the first and last publication year for an author.
        
        Args:
            author_id (str): OpenAlex author ID
            known_first_pub_year (int, optional): Manually verified first pub year
            
        Returns:
            tuple: (min_year, max_year)
        """
        # Apply rate limiting
        self._rate_limit()
        
        # If known_first_pub_year is provided, use it
        if known_first_pub_year is not None:
            min_yr = known_first_pub_year
        else:
            # Otherwise query OpenAlex for earliest publication
            try:
                earliest_work = Works().filter(authorships={"author": {"id": author_id}})\
                                      .sort(publication_date="asc")\
                                      .get()[0]
                min_yr = earliest_work['publication_year']
            except Exception as e:
                logger.error(f"Failed to get first publication year for {author_id}: {str(e)}")
                return None, None
        
        # Get latest publication year
        try:
            author_info = self.get_author_info(author_id)
            if not author_info or 'counts_by_year' not in author_info or not author_info['counts_by_year']:
                logger.error(f"No publication year data for {author_id}")
                return min_yr, None
                
            max_yr = author_info['counts_by_year'][0]['year']
        except Exception as e:
            logger.error(f"Failed to get latest publication year for {author_id}: {str(e)}")
            return min_yr, None
            
        return min_yr, max_yr
    
    def get_publications(self, author_id, year):
        """
        Get all publications for an author in a specific year.
        
        Args:
            author_id (str): OpenAlex author ID
            year (int): Publication year
            
        Returns:
            list: List of publication objects
        """
        # Apply rate limiting
        self._rate_limit()
        
        query = Works().filter(
            publication_year=year,
            authorships={"author": {"id": author_id}}
        )
        
        try:
            # Use pagination to get all results
            publications = list(chain(*query.paginate(per_page=200)))
            # Filter to English publications only
            publications = [p for p in publications if p.get('language') == 'en']
            return publications
        except Exception as e:
            logger.error(f"Failed to get publications for {author_id} in {year}: {str(e)}")
            return []
    
    def get_author_info(self, author_id):
        """
        Get basic author information from OpenAlex.
        
        Args:
            author_id (str): OpenAlex author ID
            
        Returns:
            dict: Author details
        """
        # Apply rate limiting
        self._rate_limit()
        
        try:
            return Authors()[author_id]
        except Exception as e:
            logger.error(f"Failed to get author info for {author_id}: {str(e)}")
            return None
    
    def get_most_recent_work(self, author_id):
        """
        Get the most recent work of an author.
        
        Args:
            author_id (str): OpenAlex author ID
            
        Returns:
            dict: Work details
        """
        # Apply rate limiting
        self._rate_limit()
        
        try:
            return Works().filter(authorships={"author": {"id": author_id}})\
                        .sort(publication_date="desc")\
                        .get()[0]
        except Exception as e:
            logger.error(f"Failed to get most recent work for {author_id}: {str(e)}")
            return None
        

    def get_author_info_by_name(self, author_name):
        """
        Get author information by name from OpenAlex.
        
        Args:
            author_name (str): Name of the author to search for
            
        Returns:
            dict: Author details or None if not found
        """
        # Apply rate limiting
        self._rate_limit()
        
        try:
            # The search parameter is used for searching by name
            # And results are sorted by cited_by_count to get the most relevant author
            authors = Authors().search_filter(display_name=author_name).sort(cited_by_count="desc").get()
            
            # Return the first result (most cited author with that name)
            if authors and len(authors) > 0:
                return authors[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get author info for name {author_name}: {e}")
            return None