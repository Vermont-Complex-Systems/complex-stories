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

def create_papers_lookup(conn):
    """Create DOI-based lookup table between S2 papers and OpenAlex works."""
    logger.info("Creating papers lookup table (S2 ↔ OpenAlex via DOI)...")

    try:
        conn.execute(f"""
            CREATE TABLE papersLookup (
                corpusid INT32,
                oa_id VARCHAR,
                publication_year INT16,
                match_method VARCHAR,
                match_confidence FLOAT,
                created_at TIMESTAMP
            );
        """)
        
        conn.execute(f"""
            ALTER TABLE papersLookup SET PARTITIONED BY (publication_year, match_method);
        """)
        
        conn.execute(f"""
            INSERT INTO papersLookup
            SELECT 
                s2.corpusid::INT32,
                oa.id,
                oa.publication_year::INT16,
                'doi' as match_method,
                1.0 as match_confidence,
                CURRENT_TIMESTAMP as created_at
            FROM s2_papers s2
            JOIN oa_works oa
                ON s2.externalids.DOI = REPLACE(oa.doi, 'https://doi.org/', '')
                AND s2.externalids.DOI IS NOT NULL
                AND oa.doi IS NOT NULL
                AND oa.publication_year BETWEEN 1900 AND 2025;
        """)
        logger.info("✓ Papers lookup table created successfully")

    except Exception as e:
        logger.error(f"✗ Error creating papers lookup: {e}")
        raise

def add_openalex_workid_to_s2papers(conn):
    """Add OpenAlex work ID column directly to s2_papers table."""
    logger.info("Adding OpenAlex work ID to s2_papers...")

    conn.execute("ALTER TABLE s2_papers ADD COLUMN IF NOT EXISTS oa_work_id VARCHAR;")

    conn.execute("""
        UPDATE s2_papers s2
        SET oa_work_id = oa.id
        FROM oa_works oa
        WHERE s2.externalids.DOI = REPLACE(oa.doi, 'https://doi.org/', '')
            AND s2.externalids.DOI IS NOT NULL
            AND oa.doi IS NOT NULL;
    """)

    # Get stats
    total = conn.execute("SELECT COUNT(*) FROM s2_papers").fetchone()[0]
    matched = conn.execute("SELECT COUNT(*) FROM s2_papers WHERE oa_work_id IS NOT NULL").fetchone()[0]

    logger.info(f"Added OpenAlex IDs to {matched:,} out of {total:,} papers ({matched/total*100:.1f}%)")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sync S2 papers with OpenAlex works")
    parser.add_argument("--operation",
                       choices=["lookup", "workid", "all"],
                       default="all",
                       help="Which sync operation to run")

    args = parser.parse_args()

    try:
        conn = get_duckdb_connection()

        if args.operation == "lookup":
            create_papers_lookup(conn)
        elif args.operation == "workid":
            add_openalex_workid_to_s2papers(conn)
        elif args.operation == "all":
            logger.info("Running all sync operations...")
            create_papers_lookup(conn)
            add_openalex_workid_to_s2papers(conn)

        logger.info("Sync operations completed successfully!")

    except Exception as e:
        logger.error(f"Sync failed: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()