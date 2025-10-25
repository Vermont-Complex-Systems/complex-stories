"""
Google Scholar venue scraping asset.

Scrapes Google Scholar's top venues by field and combines them into a unified dataset.
"""

import pandas as pd
import dagster as dg
from dagster_duckdb import DuckDBResource

logger = dg.get_dagster_logger()

@dg.asset(
        kinds={"duckdb"}, 
        group_name="ingestion"
)
def gscholar_venues(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """Scrape Google Scholar top venues by academic field"""
    
    # Define field categories and their URLs
    fields = {
        'Business Economics Management': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=bus',
        'Chemistry Material Science': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=chm',
        'Engineering Computer Science': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=eng',
        'Health Medicine': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=med',
        'Humanities Literature Arts': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=hum',
        'Life Earth Sciences': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=bio',
        'Physics Mathematics': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=phy',
        'Social Sciences': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=soc'
    }
    
    # Scrape data from each field
    field_dataframes = []
    field_stats = {}

    logger.info(f"Starting to scrape {len(fields)} fields")

    for field_name, url in fields.items():
        try:
            logger.info(f"Requesting {field_name} ({url})")
            df_list = pd.read_html(url)
            df = df_list[0]  # Take the first table
            df['field'] = field_name  # Add field identifier
            logger.info(f"Got {len(df)} hits")
            field_dataframes.append(df)
            field_stats[field_name] = len(df)
        except Exception as e:
            logger.error(f"Error scraping {field_name}: {e}")
            logger.error(f"URL: {url}")
            field_stats[field_name] = 0
    
    # Log summary of scraping results
    logger.info(f"Scraping complete. Successfully scraped {len(field_dataframes)} out of {len(fields)} fields")
    logger.info(f"Field stats: {field_stats}")

    # Combine all fields
    if field_dataframes:
        combined_data = pd.concat(field_dataframes, axis=0, ignore_index=True)
        
        # Create simple schema
        df_simple = pd.DataFrame({
            'source': 'gscholar_venues',
            'venue': combined_data.Publication,  # First column is typically the venue name
            'field': combined_data.field,
            'h5_index': combined_data['h5-index'],
            'h5_median': combined_data['h5-median']
        })
        
        with duckdb.get_connection() as conn:
            conn.execute("create or replace table raw.gscholar_venues as select * from df_simple")
        
        # Calculate metadata
        total_venues = len(df_simple)
        unique_fields = len(field_stats)
        successful_fields = len([f for f, count in field_stats.items() if count > 0])
        
        return dg.MaterializeResult(
            metadata={
                "total_venues": total_venues,
                "unique_fields": unique_fields,
                "successful_fields": successful_fields,
                "field_breakdown": field_stats,
                "columns": list(df_simple.columns)
            }
        )
    else:
        # Create empty table if no data was scraped
        df_simple = pd.DataFrame({
            'source': [],
            'venue': [],
            'field': [],
            'h5_index': [],
            'h5_median': []
        })
        
        with duckdb.get_connection() as conn:
            conn.execute("create or replace table raw.gscholar_venues as select * from df_simple")
        
        return dg.MaterializeResult(
            metadata={
                "total_venues": 0,
                "unique_fields": 0,
                "successful_fields": 0,
                "field_breakdown": field_stats,
                "error": "No data was successfully scraped"
            }
        )