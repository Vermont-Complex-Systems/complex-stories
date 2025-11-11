#!/usr/bin/env python3
"""
EXPORT step: Create arXiv fulltext materialized view for API streaming
This creates a pre-computed table to avoid expensive JOINs in real-time
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

    # Aggressive memory settings since we have headroom
    conn.execute("PRAGMA memory_limit='42GB';")  # Use most available memory
    conn.execute("PRAGMA max_temp_directory_size='300GB';")  # More temp space
    conn.execute("SET threads=12;")  # More threads for faster processing
    conn.execute("SET preserve_insertion_order=false;")  # Save memory

    # Attach DuckLake (adjust password as needed)
    conn.execute("""
        ATTACH 'ducklake:postgres:dbname=complex_stories host=localhost user=jstonge1'
        AS scisciDB (DATA_PATH '/netfiles/compethicslab/scisciDB/');
    """)

    conn.execute("USE scisciDB;")
    return conn


def create_arxiv_fulltext_view(conn):
    """Create materialized view for arXiv papers with S2ORC full text."""
    logger.info("Creating arXiv fulltext materialized view...")

    # Drop existing table if it exists
    conn.execute("DROP TABLE IF EXISTS arxiv_fulltext;")

    # Create empty table with schema
    conn.execute("""
        CREATE TABLE arxiv_fulltext (
            corpusid BIGINT,
            year INTEGER,
            arxiv_id VARCHAR,
            text VARCHAR,
            annotations JSON,
            text_length BIGINT,
            created_at TIMESTAMP
        );
    """)

    # Get corpusid ranges for smaller batches
    min_max = conn.execute("""
        SELECT MIN(corpusid), MAX(corpusid)
        FROM s2_papers
        WHERE externalids.arxiv IS NOT NULL
          AND has_fulltext = true
    """).fetchone()

    min_id, max_id = min_max[0], min_max[1]
    batch_size = 5_000_000  # Process 5M corpusids at a time. Could do more.

    logger.info(f"Processing corpusids from {min_id} to {max_id} in batches of {batch_size}")

    total_inserted = 0
    current_id = min_id

    while current_id < max_id:
        end_id = min(current_id + batch_size, max_id + 1)
        logger.info(f"Processing corpusids {current_id} to {end_id}...")

        batch_count = conn.execute(f"""
            INSERT INTO arxiv_fulltext (corpusid, year, arxiv_id, text, annotations, text_length)
            SELECT
                s2.corpusid,
                s2.year,
                s2.externalids.arxiv as arxiv_id,
                s2orc.body.text as text,
                s2orc.body.annotations as annotations,
                LENGTH(s2orc.body.text) as text_length
            FROM s2_papers s2
            JOIN s2orc_v2 s2orc ON s2.corpusid = s2orc.corpusid
            WHERE s2.corpusid >= {current_id}
              AND s2.corpusid < {end_id}
              AND s2.externalids.arxiv IS NOT NULL
              AND s2.has_fulltext = true
              AND s2.year < 1991
              AND s2orc.body.text IS NOT NULL
              AND s2orc.body.text != '';
        """).rowcount

        total_inserted += batch_count
        logger.info(f"  Batch {current_id}-{end_id}: {batch_count:,} papers (total: {total_inserted:,})")

        current_id = end_id

    logger.info(f"✅ Completed batch processing: {total_inserted:,} total papers")

    # Get stats
    stats = conn.execute("""
        SELECT
            COUNT(*) as total_papers,
            COUNT(DISTINCT year) as unique_years,
            MIN(year) as earliest_year,
            MAX(year) as latest_year,
            AVG(text_length) as avg_text_length,
            MAX(text_length) as max_text_length,
            SUM(text_length) as total_text_size
        FROM arxiv_fulltext;
    """).fetchone()

    logger.info(f"✅ Created arxiv_fulltext table with {stats[0]:,} papers")
    logger.info(f"   Years: {stats[2]} - {stats[3]} ({stats[1]} unique)")
    logger.info(f"   Text length: avg={stats[4]:,.0f}, max={stats[5]:,}")
    logger.info(f"   Total text size: {stats[6]:,} characters (~{stats[6]/1e9:.1f} GB)")

    # Show year breakdown
    year_breakdown = conn.execute("""
        SELECT year, COUNT(*) as papers
        FROM arxiv_fulltext
        WHERE year >= 2015
        GROUP BY year
        ORDER BY year DESC
        LIMIT 10;
    """).fetchall()

    logger.info("Recent years breakdown:")
    for year, count in year_breakdown:
        logger.info(f"   {year}: {count:,} papers")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="EXPORT step: Create arXiv fulltext materialized view"
    )
    parser.add_argument("--force", action="store_true", help="Force recreation even if table exists")

    args = parser.parse_args()

    try:
        conn = get_duckdb_connection()

        # Check if table already exists
        existing = conn.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name = 'arxiv_fulltext'
        """).fetchone()[0]

        if existing and not args.force:
            logger.info("arxiv_fulltext table already exists. Use --force to recreate.")

            # Show current stats
            stats = conn.execute("""
                SELECT COUNT(*), MIN(year), MAX(year)
                FROM arxiv_fulltext
            """).fetchone()
            logger.info(f"Current table: {stats[0]:,} papers ({stats[1]} - {stats[2]})")
            return

        create_arxiv_fulltext_view(conn)
        logger.info("Export completed successfully!")

    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()