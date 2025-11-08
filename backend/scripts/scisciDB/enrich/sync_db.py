"""
Sync and enrich s2_papers with OpenAlex metadata.

This module provides functions to match records between S2 papers and OpenAlex works
using normalized external identifiers (DOI, PMID, MAG, PMCID).
"""

import duckdb
from pathlib import Path
import logging
import os
import time
from tqdm import tqdm

from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def get_duckdb_connection():
    """Get DuckDB connection with DuckLake attached and optimized settings."""
    # Create temp directory first
    temp_dir = os.getenv('DUCKDB_TEMP')

    # Connect with temp directory set from the start
    conn = duckdb.connect()

    # Set temp directory FIRST before any operations
    conn.execute(f"PRAGMA temp_directory='{temp_dir}';")

    # Then optimize memory settings for large joins
    conn.execute("PRAGMA memory_limit='40GB';")  # Use most of your 46GB
    conn.execute("PRAGMA max_temp_directory_size='100GB';")  # Increase temp space
    conn.execute("SET threads=8;")  # Reduce threads to save memory
    conn.execute("SET preserve_insertion_order=false;")  # Save memory

    # Attach DuckLake (adjust password as needed)
    conn.execute("""
        ATTACH 'ducklake:postgres:dbname=complex_stories host=localhost user=jstonge1'
        AS scisciDB (DATA_PATH '/netfiles/compethicslab/scisciDB/');
    """)

    conn.execute("USE scisciDB;")
    return conn

def add_openalex_id_column(conn):
    """
    Add OpenAlex ID column to s2_papers table.

    This function:
    1. Adds oa_id column if it doesn't exist
    2. Matches records between s2_papers and oa_works using normalized external IDs
    3. Populates oa_id with OpenAlex identifier for matched records

    Args:
        conn: DuckDB connection with DuckLake attached
    """

    logger.info("Adding oa_id column to s2_papers...")

    # Add column if it doesn't exist
    try:
        conn.execute("ALTER TABLE s2_papers ADD COLUMN oa_id VARCHAR;")
        logger.info("Added oa_id column to s2_papers")
    except Exception as e:
        if "already exists" in str(e).lower():
            logger.info("oa_id column already exists")
        else:
            raise e

    logger.info("using doi to merge...")

    # Get total count for context
    total_papers = conn.execute("SELECT COUNT(*) FROM s2_papers WHERE externalids.DOI IS NOT NULL").fetchone()[0]
    logger.info(f"Found {total_papers:,} s2_papers with DOIs to match")

    # Show progress bar during the long-running query
    with tqdm(desc="Matching DOIs", unit=" papers", bar_format="{desc}: {elapsed} elapsed") as pbar:
        start_time = time.time()

        result = conn.execute("""
            UPDATE s2_papers AS s2
            SET oa_id = oa.ids.openalex
            FROM oa_works AS oa
            WHERE (
                s2.externalids.DOI IS NOT NULL
                AND oa.doi IS NOT NULL
                AND s2.externalids.DOI = regexp_replace(oa.doi, '^https://doi.org/', '')
            )
        """)

        elapsed = time.time() - start_time
        pbar.close()

    rows_affected = result.rowcount if hasattr(result, 'rowcount') else 'Unknown'
    logger.info(f"ID matching complete in {elapsed:.1f} seconds. Rows affected: {rows_affected}")

    if isinstance(rows_affected, int) and total_papers > 0:
        match_rate = (rows_affected / total_papers) * 100
        logger.info(f"Match rate: {match_rate:.1f}% ({rows_affected:,} / {total_papers:,})")

def sync_openalex_ids():
    """
    Main function to sync OpenAlex IDs with s2_papers.

    This is the primary entry point for establishing the ID mapping
    between S2 papers and OpenAlex works.
    """

    logger.info("Starting OpenAlex ID sync process...")

    # Get connection
    conn = get_duckdb_connection()

    try:
        # Add and populate oa_id column
        add_openalex_id_column(conn)

        logger.info("OpenAlex ID sync completed successfully!")
        return stats

    except Exception as e:
        logger.error(f"Error during sync process: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # Run the sync process
    stats = sync_openalex_ids()
    print(f"Sync complete! Matched {stats['matched_papers']:,} papers ({stats['match_rate']:.2%})")