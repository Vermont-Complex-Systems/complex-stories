"""
Export field-metrics from DuckLake to PostgreSQL.

This creates a precomputed dimensional aggregation table that makes API queries
much faster. Instead of computing counts on-demand, we precompute field x year x metric_type
counts and store them in PostgreSQL.

Supported metrics:
- total: Total number of papers
- has_abstract: Papers with abstract available
- has_fulltext: Papers with full text available
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

def compute_field_metrics(conn):
    """Compute field-year-metric combinations from s2_papers."""
    logger.info("Computing field metrics from s2_papers...")

    # Get total papers for context
    total_papers = conn.execute("SELECT COUNT(*) FROM s2_papers WHERE s2fieldsofstudy IS NOT NULL").fetchone()[0]
    logger.info(f"Processing {total_papers:,} papers with field-of-study data")

    start_time = time.time()

    # Compute all metrics in a single query using conditional aggregation
    logger.info("Computing field-year metrics...")
    result = conn.execute("""
        WITH field_papers AS (
            SELECT
                list_filter(s2fieldsofstudy, x -> x.source = 's2-fos-model')[1].category as field,
                year,
                has_abstract,
                has_fulltext
            FROM s2_papers
            WHERE s2fieldsofstudy IS NOT NULL
              AND year IS NOT NULL
              AND year >= 1900
              AND year <= 2025
        )
        SELECT
            field,
            year,
            'total' as metric_type,
            COUNT(*) as count
        FROM field_papers
        WHERE field IS NOT NULL
        GROUP BY field, year

        UNION ALL

        SELECT
            field,
            year,
            'has_abstract' as metric_type,
            COUNT(*) as count
        FROM field_papers
        WHERE field IS NOT NULL
          AND has_abstract = true
        GROUP BY field, year

        UNION ALL

        SELECT
            field,
            year,
            'has_fulltext' as metric_type,
            COUNT(*) as count
        FROM field_papers
        WHERE field IS NOT NULL
          AND has_fulltext = true
        GROUP BY field, year

        ORDER BY field, year, metric_type
    """).fetchall()

    elapsed = time.time() - start_time
    logger.info(f"Computed {len(result):,} field-year-metric combinations in {elapsed:.1f} seconds")

    # Convert to list of dicts for easier handling
    field_metrics = [
        {
            "field": row[0],
            "year": row[1],
            "metric_type": row[2],
            "count": row[3]
        }
        for row in result
        if row[0] is not None  # Skip rows where field extraction failed
    ]

    logger.info(f"Returning {len(field_metrics):,} valid field-metric records")
    return field_metrics

def upload_to_postgresql(data, batch_size=10000):
    """Upload field metrics to PostgreSQL via FastAPI."""
    api_base = os.getenv('API_BASE', 'http://localhost:8000')

    logger.info(f"Uploading {len(data):,} records to PostgreSQL via {api_base}")

    # Upload in batches
    total_batches = (len(data) + batch_size - 1) // batch_size

    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        batch_num = (i // batch_size) + 1

        logger.info(f"Uploading batch {batch_num}/{total_batches} ({len(batch):,} records)")

        try:
            response = requests.post(
                f"{api_base}/scisciDB/field-metrics/bulk",
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

def export_field_metrics():
    """Main function to export field metrics."""
    logger.info("Starting field-metrics export...")

    # Get DuckDB connection
    conn = get_duckdb_connection()

    try:
        # Compute the metrics
        field_metrics = compute_field_metrics(conn)

        if not field_metrics:
            logger.error("No field metrics computed!")
            return False

        # Upload to PostgreSQL
        success = upload_to_postgresql(field_metrics)

        if success:
            logger.info("✓ Field-metrics export completed successfully!")

            # Show some sample stats
            metrics_by_type = {}
            for record in field_metrics:
                metric_type = record['metric_type']
                if metric_type not in metrics_by_type:
                    metrics_by_type[metric_type] = 0
                metrics_by_type[metric_type] += record['count']

            unique_fields = len(set(record['field'] for record in field_metrics))
            year_range = (
                min(record['year'] for record in field_metrics),
                max(record['year'] for record in field_metrics)
            )

            logger.info(f"📊 Export stats:")
            logger.info(f"   Unique fields: {unique_fields}")
            logger.info(f"   Year range: {year_range[0]}-{year_range[1]}")
            for metric_type, total_count in metrics_by_type.items():
                logger.info(f"   {metric_type}: {total_count:,} papers")

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
    success = export_field_metrics()
    if not success:
        exit(1)