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

def compute_metrics(conn, group_by='field'):
    """Compute metrics by specified grouping dimension from s2_papers.

    Args:
        conn: DuckDB connection
        group_by: Grouping dimension ('field' or 'venue')
    """
    if group_by not in ['field', 'venue']:
        raise ValueError(f"Invalid group_by parameter: {group_by}. Must be 'field' or 'venue'.")

    logger.info(f"Computing {group_by} metrics from s2_papers...")

    if group_by == 'field':
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

        # Convert to list of dicts for easier handling
        metrics = [
            {
                "field": row[0],
                "year": row[1],
                "metric_type": row[2],
                "count": row[3]
            }
            for row in result
            if row[0] is not None  # Skip rows where field extraction failed
        ]

    elif group_by == 'venue':
        # Get total papers for context
        total_papers = conn.execute("SELECT COUNT(*) FROM s2_papers WHERE venue IS NOT NULL").fetchone()[0]
        logger.info(f"Processing {total_papers:,} papers with venue data")

        start_time = time.time()

        # Compute venue-year metrics
        logger.info("Computing venue-year metrics...")
        result = conn.execute("""
            SELECT
                venue,
                year,
                'total' as metric_type,
                COUNT(*) as count
            FROM s2_papers
            WHERE venue IS NOT NULL
              AND year IS NOT NULL
              AND year >= 1900
              AND year <= 2025
            GROUP BY venue, year

            UNION ALL

            SELECT
                venue,
                year,
                'has_abstract' as metric_type,
                COUNT(*) as count
            FROM s2_papers
            WHERE venue IS NOT NULL
              AND year IS NOT NULL
              AND year >= 1900
              AND year <= 2025
              AND has_abstract = true
            GROUP BY venue, year

            UNION ALL

            SELECT
                venue,
                year,
                'has_fulltext' as metric_type,
                COUNT(*) as count
            FROM s2_papers
            WHERE venue IS NOT NULL
              AND year IS NOT NULL
              AND year >= 1900
              AND year <= 2025
              AND has_fulltext = true
            GROUP BY venue, year

            ORDER BY venue, year, metric_type
        """).fetchall()

        # Convert to list of dicts for easier handling
        metrics = [
            {
                "venue": row[0],
                "year": row[1],
                "metric_type": row[2],
                "count": row[3]
            }
            for row in result
            if row[0] is not None  # Skip rows where venue is null
        ]

    elapsed = time.time() - start_time
    logger.info(f"Computed {len(result):,} {group_by}-year-metric combinations in {elapsed:.1f} seconds")
    logger.info(f"Returning {len(metrics):,} valid {group_by}-metric records")
    return metrics

# Backward compatibility function
def compute_field_metrics(conn):
    """Compute field-year-metric combinations from s2_papers. (Backward compatibility)"""
    return compute_metrics(conn, group_by='field')

def upload_to_postgresql(data, group_by='field', batch_size=10000):
    """Upload metrics to PostgreSQL via FastAPI.

    Args:
        data: List of metric records
        group_by: Grouping dimension ('field' or 'venue')
        batch_size: Number of records per batch
    """
    api_base = os.getenv('API_BASE', 'http://localhost:8000')

    if group_by not in ['field', 'venue']:
        raise ValueError(f"Invalid group_by parameter: {group_by}")

    endpoint = f"{api_base}/scisciDB/metrics/bulk?group_by={group_by}"

    logger.info(f"Uploading {len(data):,} {group_by} records to PostgreSQL via {api_base}")

    # Upload in batches
    total_batches = (len(data) + batch_size - 1) // batch_size

    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        batch_num = (i // batch_size) + 1

        logger.info(f"Uploading batch {batch_num}/{total_batches} ({len(batch):,} records)")

        try:
            response = requests.post(
                endpoint,
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

def export_metrics(group_by='field'):
    """Main function to export metrics by specified grouping."""
    logger.info(f"Starting {group_by}-metrics export...")

    # Get DuckDB connection
    conn = get_duckdb_connection()

    try:
        # Compute the metrics
        metrics = compute_metrics(conn, group_by=group_by)

        if not metrics:
            logger.error(f"No {group_by} metrics computed!")
            return False

        # Upload to PostgreSQL
        success = upload_to_postgresql(metrics, group_by=group_by)

        if success:
            logger.info(f"✓ {group_by.title()}-metrics export completed successfully!")

            # Show some sample stats
            metrics_by_type = {}
            for record in metrics:
                metric_type = record['metric_type']
                if metric_type not in metrics_by_type:
                    metrics_by_type[metric_type] = 0
                metrics_by_type[metric_type] += record['count']

            group_key = 'field' if group_by == 'field' else 'venue'
            unique_groups = len(set(record[group_key] for record in metrics))
            year_range = (
                min(record['year'] for record in metrics),
                max(record['year'] for record in metrics)
            )

            logger.info(f"📊 Export stats:")
            logger.info(f"   Unique {group_by}s: {unique_groups}")
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

# Backward compatibility function
def export_field_metrics():
    """Export field metrics. (Backward compatibility)"""
    return export_metrics(group_by='field')

def export_venue_metrics():
    """Export venue metrics."""
    return export_metrics(group_by='venue')

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export metrics by field or venue")
    parser.add_argument(
        "--group-by",
        choices=['field', 'venue'],
        default='field',
        help="Group metrics by field or venue (default: field)"
    )

    args = parser.parse_args()

    success = export_metrics(group_by=args.group_by)
    if not success:
        exit(1)