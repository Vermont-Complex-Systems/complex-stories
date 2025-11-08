"""
Export field-year counts from DuckLake to PostgreSQL.

This creates a precomputed aggregation table that makes API queries much faster.
Instead of computing counts on-demand from millions of papers, we precompute
field x year counts and store them in PostgreSQL.
"""

import duckdb
import logging
import os
import time
import requests

from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def get_duckdb_connection():
    """Get DuckDB connection with DuckLake attached and optimized settings."""
    # Create temp directory first
    temp_dir = os.getenv('DUCKDB_TEMP', '/tmp/duckdb_temp')
    os.makedirs(temp_dir, exist_ok=True)

    # Connect with optimized settings
    conn = duckdb.connect()
    conn.execute(f"PRAGMA temp_directory='{temp_dir}';")
    conn.execute("PRAGMA memory_limit='40GB';")
    conn.execute("PRAGMA max_temp_directory_size='100GB';")
    conn.execute("SET threads=8;")
    conn.execute("SET preserve_insertion_order=false;")

    # Attach DuckLake
    postgres_password = os.getenv('POSTGRES_PASSWORD')
    if not postgres_password:
        raise ValueError("POSTGRES_PASSWORD environment variable not set")

    logger.info("Attaching DuckLake...")
    conn.execute(f"""
        ATTACH 'ducklake:postgres:dbname=complex_stories host=localhost user=jstonge1 password={postgres_password}'
        AS scisciDB (DATA_PATH '/netfiles/compethicslab/scisciDB/');
    """)

    conn.execute("USE scisciDB;")
    return conn

def compute_field_year_counts(conn):
    """Compute field-year counts from s2_papers."""
    logger.info("Computing field-year counts from s2_papers...")

    # Get total papers for context
    total_papers = conn.execute("SELECT COUNT(*) FROM s2_papers WHERE s2fieldsofstudy IS NOT NULL").fetchone()[0]
    logger.info(f"Processing {total_papers:,} papers with field-of-study data")

    # Compute the aggregation
    logger.info("Computing field-year counts...")
    start_time = time.time()

    result = conn.execute("""
        SELECT
            list_filter(s2fieldsofstudy, x -> x.source = 's2-fos-model')[1].category as field,
            year,
            COUNT(*) as count
        FROM s2_papers
        WHERE s2fieldsofstudy IS NOT NULL
          AND year IS NOT NULL
          AND year >= 1900  
          AND year <= 2025
        GROUP BY field, year
        ORDER BY year DESC, count DESC
    """).fetchall()

    elapsed = time.time() - start_time

    logger.info(f"Computed {len(result):,} field-year combinations in {elapsed:.1f} seconds")

    # Convert to list of dicts for easier handling
    field_year_counts = [
        {
            "field": row[0],
            "year": row[1],
            "count": row[2]
        }
        for row in result
        if row[0] is not None  # Skip rows where field extraction failed
    ]

    logger.info(f"Returning {len(field_year_counts):,} valid field-year count records")
    return field_year_counts

def upload_to_postgresql(data, batch_size=10000):
    """Upload field-year counts to PostgreSQL via FastAPI."""
    api_base = os.getenv('API_BASE', 'http://localhost:8000')

    logger.info(f"Uploading {len(data):,} records to PostgreSQL via {api_base}")

    # Note: Table will be auto-created by SQLAlchemy on first insert

    # Upload in batches
    total_batches = (len(data) + batch_size - 1) // batch_size

    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        batch_num = (i // batch_size) + 1

        logger.info(f"Uploading batch {batch_num}/{total_batches} ({len(batch):,} records)")

        try:
            response = requests.post(
                f"{api_base}/scisciDB/field-year-counts/bulk",
                json=batch,
                timeout=300  # 5 minute timeout for large batches
            )

            if response.status_code == 200:
                logger.info(f"✓ Batch {batch_num} uploaded successfully")
            else:
                logger.error(f"✗ Batch {batch_num} failed: {response.status_code} - {response.text}")
                return False

        except requests.RequestException as e:
            logger.error(f"✗ Batch {batch_num} failed: {e}")
            return False

    logger.info("✓ All batches uploaded successfully!")
    return True

def export_field_year_counts():
    """Main function to export field-year counts."""
    logger.info("Starting field-year counts export...")

    # Get DuckDB connection
    conn = get_duckdb_connection()

    try:
        # Compute the counts
        field_year_counts = compute_field_year_counts(conn)

        if not field_year_counts:
            logger.error("No field-year counts computed!")
            return False

        # Upload to PostgreSQL
        success = upload_to_postgresql(field_year_counts)

        if success:
            logger.info("✓ Field-year counts export completed successfully!")

            # Show some sample stats
            total_papers = sum(record['count'] for record in field_year_counts)
            unique_fields = len(set(record['field'] for record in field_year_counts))
            year_range = (
                min(record['year'] for record in field_year_counts),
                max(record['year'] for record in field_year_counts)
            )

            logger.info(f"📊 Export stats:")
            logger.info(f"   Total papers: {total_papers:,}")
            logger.info(f"   Unique fields: {unique_fields}")
            logger.info(f"   Year range: {year_range[0]}-{year_range[1]}")

            return True
        else:
            logger.error("✗ Failed to upload to PostgreSQL")
            return False

    except Exception as e:
        logger.error(f"Export failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = export_field_year_counts()
    if not success:
        exit(1)