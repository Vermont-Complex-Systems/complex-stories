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

def s2_has_abstract(conn):
    conn.execute("""
        ALTER TABLE s2_papers ADD COLUMN has_abstract BOOLEAN;
        UPDATE s2_papers AS p
        SET has_abstract = EXISTS (
            SELECT 1 FROM abstracts AS o
            WHERE o.corpusid = p.corpusid
        );
    """)

def oa_completeness_score(conn):
    """Add completeness score column to oa_works table."""
    logger.info("Adding completeness score to oa_works...")

    conn.execute("""
        ALTER TABLE oa_works ADD COLUMN IF NOT EXISTS completeness_score INTEGER DEFAULT 0;

        UPDATE oa_works
        SET completeness_score = (
            CASE WHEN id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN title IS NOT NULL AND title != '' THEN 1 ELSE 0 END +
            CASE WHEN display_name IS NOT NULL AND display_name != '' THEN 1 ELSE 0 END +
            CASE WHEN publication_year IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN publication_date IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN ids IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN language IS NOT NULL AND language != '' THEN 1 ELSE 0 END +
            CASE WHEN primary_location IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN type IS NOT NULL AND type != '' THEN 1 ELSE 0 END +
            CASE WHEN type_crossref IS NOT NULL AND type_crossref != '' THEN 1 ELSE 0 END +
            CASE WHEN indexed_in IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN open_access IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN authorships IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN institution_assertions IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN countries_distinct_count IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN institutions_distinct_count IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN corresponding_author_ids IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN corresponding_institution_ids IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN apc_list IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN apc_paid IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN fwci IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN has_fulltext IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN fulltext_origin IS NOT NULL AND fulltext_origin != '' THEN 1 ELSE 0 END +
            CASE WHEN cited_by_count IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN biblio IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN is_retracted IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN is_paratext IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN abstract_inverted_index IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN cited_by_api_url IS NOT NULL AND cited_by_api_url != '' THEN 1 ELSE 0 END +
            CASE WHEN counts_by_year IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN updated_date IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN created_date IS NOT NULL THEN 1 ELSE 0 END
        );
    """)

    # Report some stats
    stats = conn.execute("""
        SELECT
            COUNT(*) as total_works,
            AVG(completeness_score) as avg_completeness,
            MIN(completeness_score) as min_completeness,
            MAX(completeness_score) as max_completeness
        FROM oa_works
    """).fetchone()

    logger.info(f"Completeness scores: avg={stats[1]:.1f}, min={stats[2]}, max={stats[3]} (total: {stats[0]:,} works)")

def oa_primary_doi(conn):
    """Mark primary DOI as most cited work for each DOI."""
    logger.info("Marking primary DOIs using most cited strategy...")

    conn.execute("""
        ALTER TABLE oa_works ADD COLUMN IF NOT EXISTS primary_doi BOOLEAN DEFAULT NULL;

        -- Reset all primary_doi flags
        UPDATE oa_works SET primary_doi = NULL;

        -- Mark most cited work as primary for each DOI
        WITH ranked_works AS (
            SELECT id,
                   ROW_NUMBER() OVER (
                       PARTITION BY doi
                       ORDER BY
                           COALESCE(cited_by_count, 0) DESC,
                           id ASC  -- tie-breaker for deterministic results
                   ) AS rank_in_doi
            FROM oa_works
            WHERE doi IS NOT NULL AND doi != ''
        )
        UPDATE oa_works
        SET primary_doi = true
        WHERE id IN (
            SELECT id FROM ranked_works WHERE rank_in_doi = 1
        );
    """)

    # Report results
    stats = conn.execute("""
        SELECT
            COUNT(*) as total_primary_dois,
            COUNT(DISTINCT doi) as unique_dois
        FROM oa_works
        WHERE primary_doi = true
    """).fetchone()

    logger.info(f"Marked {stats[0]:,} primary works for {stats[1]:,} unique DOIs")

def s2_has_fulltext(conn):
    conn.execute("""
        ALTER TABLE s2_papers ADD COLUMN has_fulltext BOOLEAN;
        UPDATE s2_papers AS p
        SET has_fulltext = EXISTS (
            SELECT 1 FROM s2orc_v2 AS o
            WHERE o.corpusid = p.corpusid
        );
    """)


def main():
    parser = argparse.ArgumentParser(
        description="ENRICH step: Add derived fields"
    )
    parser.add_argument("--operation",
                       choices=["has_abstract", "has_fulltext", "openalex_topics", "topic_categories", "completeness_score", "primary_doi", "all"],
                       default="all",
                       help="Which enrichment operation to run")

    args = parser.parse_args()

    try:
        conn = get_duckdb_connection()

        if args.operation == 'has_abstract':
            logger.info("Adding has_abstract field...")
            s2_has_abstract(conn)
        elif args.operation == 'has_fulltext':
            logger.info("Adding has_fulltext field...")
            s2_has_fulltext(conn)
        elif args.operation == 'completeness_score':
            logger.info("Adding completeness score...")
            oa_completeness_score(conn)
        elif args.operation == 'primary_doi':
            logger.info("Adding primary_doi field...")
            oa_primary_doi(conn)
        elif args.operation == 'all':
            logger.info("Running all enrichment operations...")
            s2_has_abstract(conn)
            s2_has_fulltext(conn)
            oa_completeness_score(conn)
            oa_primary_doi(conn)

        logger.info("Enrichment completed successfully!")

    except Exception as e:
        logger.error(f"Enrichment failed: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()