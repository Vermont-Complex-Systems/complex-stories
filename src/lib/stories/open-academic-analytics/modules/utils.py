"""
Utility functions for the coauthorship analysis pipeline
"""
import calendar
from collections import Counter
from datetime import datetime
import random
from pyalex import Works, Authors

def shuffle_date_within_month(date_str):
    """
    Add random noise to the day within a month to improve visualization.
    
    Args:
        date_str (str or datetime): The date to shuffle
        
    Returns:
        str: New date with randomized day within the same month
    """
    # Parse the date string to a datetime object if it's not already
    if isinstance(date_str, str):
        date = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        date = date_str

    # Get the number of days in the month of the given date
    _, num_days_in_month = calendar.monthrange(date.year, date.month)

    # Generate a random day within the same month
    random_day = random.randint(1, num_days_in_month)

    # Create a new date with the randomly chosen day
    shuffled_date = date.replace(day=random_day)

    # Return the date in the desired format
    return shuffled_date.strftime("%Y-%m-%d")

def guess_min_pub_year(target_aid):
    """
    Get the first publication year for an author from OpenAlex.
    
    Args:
        target_aid (str): OpenAlex author ID
        
    Returns:
        int: First publication year
    """
    return Works().filter(authorships={"author": {"id": target_aid}})\
                  .sort(publication_date="asc")\
                  .get()[0]['publication_year']

def most_recent_work(aid):
    """
    Get the most recent work of an author from OpenAlex.
    
    Args:
        aid (str): OpenAlex author ID
        
    Returns:
        dict: Work details
    """
    return Works().filter(authorships={"author": {"id": aid}})\
                  .sort(publication_date="desc")\
                  .get()[0]

def determine_home_inst(aid, works):
    """
    Determine the most common institution for an author based on works.
    
    Args:
        aid (str): OpenAlex author ID
        works (list): List of works
        
    Returns:
        str: Most common institution name or None
    """
    all_inst_this_year = []
    for w in works:
        for a in w['authorships']:
            if a['author']['id'].split("/")[-1] == aid:
                all_inst_this_year += [i['display_name'] for i in a['institutions']]
    return Counter(all_inst_this_year).most_common(1)[0][0] if len(all_inst_this_year) > 0 else None

def is_db_up_to_date(con, target_aid, min_yr):
    """
    Check if the database records for an author are up to date.
    
    Args:
        con (duckdb.Connection): Database connection
        target_aid (str): OpenAlex author ID
        min_yr (int): First publication year
        
    Returns:
        bool: True if up to date, False otherwise
    """
    # Get date range from database
    query_min = "SELECT pub_date FROM paper WHERE ego_aid = ? ORDER BY pub_date DESC LIMIT 1"
    query_max = "SELECT pub_date FROM paper WHERE ego_aid = ? ORDER BY pub_date ASC LIMIT 1"
    min_db = con.execute(query_min, (target_aid,)).fetchall()
    max_db = con.execute(query_max, (target_aid,)).fetchall()
    
    if len(min_db) == 0 or len(max_db) == 0:
        return False
    
    # Get date range from OpenAlex
    max_oa = datetime.strptime(most_recent_work(target_aid)['publication_date'], "%Y-%m-%d").date()
    
    # Check if ranges match
    return (min_yr >= min_db[1].year) and (max_oa.year <= min_db[0].year)