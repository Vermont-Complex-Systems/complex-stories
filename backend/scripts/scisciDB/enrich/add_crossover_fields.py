#!/usr/bin/env python3
"""
ENRICH step: Add derived fields and computed columns
Replaces MongoDB aggregation pipelines with DuckDB transformations
"""
import argparse
import duckdb
from pathlib import Path
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

def s2_add_oa_topics(conn):
    """Add OpenAlex topics and concepts columns to s2_papers table."""
    logger.info("Adding OpenAlex topic columns to s2_papers...")

    # Add the new columns with full struct definitions
    conn.execute("""
        ALTER TABLE s2_papers ADD COLUMN IF NOT EXISTS oa_topics
            STRUCT(id VARCHAR, display_name VARCHAR, subfield STRUCT(id VARCHAR, display_name VARCHAR), field STRUCT(id VARCHAR, display_name VARCHAR), "domain" STRUCT(id VARCHAR, display_name VARCHAR), score DOUBLE)[];

        ALTER TABLE s2_papers ADD COLUMN IF NOT EXISTS oa_concepts
            STRUCT(id VARCHAR, wikidata VARCHAR, display_name VARCHAR, "level" BIGINT, score DOUBLE)[];

        ALTER TABLE s2_papers ADD COLUMN IF NOT EXISTS oa_primary_topic
            STRUCT(id VARCHAR, display_name VARCHAR, subfield STRUCT(id VARCHAR, display_name VARCHAR), field STRUCT(id VARCHAR, display_name VARCHAR), "domain" STRUCT(id VARCHAR, display_name VARCHAR), score DOUBLE);
    """)

    logger.info("Processing older years...")
    conn.execute("""
        UPDATE s2_papers AS s2
        SET
            oa_topics = oa.topics,
            oa_concepts = oa.concepts,
            oa_primary_topic = oa.primary_topic
        FROM (
            SELECT corpusid, oa_id
            FROM papersLookup
            ORDER BY corpusid, oa_id
        ) lookup
        JOIN oa_works oa ON lookup.oa_id = oa.id
            WHERE s2.corpusid = lookup.corpusid;
    """)

    # Get enrichment stats
    total_s2 = conn.execute("SELECT COUNT(*) FROM s2_papers").fetchone()[0]
    enriched = conn.execute("SELECT COUNT(*) FROM s2_papers WHERE oa_topics IS NOT NULL").fetchone()[0]

    logger.info(f"Enriched {enriched:,} out of {total_s2:,} S2 papers ({enriched/total_s2*100:.1f}%)")
    return enriched, total_s2


def main():
    parser = argparse.ArgumentParser(
        description="ENRICH step: Add derived fields"
    )
    parser.add_argument("--dataset", default="papers", help="Dataset name")
    parser.add_argument("--input", type=Path, default=Path("import"))
    parser.add_argument("--output", type=Path, default=Path("enrich"))
    parser.add_argument("--operation", help="Which enrichment operation to run")

    args = parser.parse_args()

    try:
        conn = get_duckdb_connection()

        if args.operation == 'oa_topics':
            logger.info("Adding OpenAlex topics and concepts...")
            s2_add_oa_topics(conn)
        
        logger.info("Enrichment completed successfully!")

    except Exception as e:
        logger.error(f"Enrichment failed: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()