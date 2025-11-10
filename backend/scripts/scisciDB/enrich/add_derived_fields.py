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
        ALTER TABLE papers ADD COLUMN has_abstract BOOLEAN;
        UPDATE papers AS p
        SET has_abstract = EXISTS (
            SELECT 1 FROM abstracts AS o
            WHERE o.corpusid = p.corpusid
        );
    """)

def s2_has_fulltext(conn):
    conn.execute("""
        ALTER TABLE papers ADD COLUMN has_fulltext BOOLEAN;
        UPDATE papers AS p
        SET has_fulltext = EXISTS (
            SELECT 1 FROM s2orc_v2 AS o
            WHERE o.corpusid = p.corpusid
        );
    """)

def s2_add_openalex_topics(conn):
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

    # Update the columns via the lookup table in batches by year
    logger.info("Updating s2_papers with OpenAlex data (batched by year)...")

    total_updated = 0
    years = range(2020, 2025)  # Process recent years first (most data)

    for year in years:
        logger.info(f"Processing year {year}...")

        result = conn.execute(f"""
            UPDATE s2_papers AS s2
            SET
                oa_topics = oa.topics,
                oa_concepts = oa.concepts,
                oa_primary_topic = oa.primary_topic
            FROM (
                SELECT DISTINCT ON (corpusid) corpusid, oa_id
                FROM read_parquet('/netfiles/compethicslab/scisciDB/mapping/papers/by_doi/publication_year={year}/*.parquet')
                ORDER BY corpusid, oa_id
            ) lookup
            JOIN oa_works oa ON lookup.oa_id = oa.id
            WHERE s2.corpusid = lookup.corpusid AND s2.year = {year};
        """)

        # Count updated rows for this batch
        batch_count = conn.execute(f"""
            SELECT COUNT(*) FROM s2_papers
            WHERE year = {year} AND oa_topics IS NOT NULL
        """).fetchone()[0]

        total_updated += batch_count
        logger.info(f"  Updated {batch_count:,} papers for {year}")

    # Process older years (1900-2019) in larger chunks
    logger.info("Processing older years...")
    conn.execute("""
        UPDATE s2_papers AS s2
        SET
            oa_topics = oa.topics,
            oa_concepts = oa.concepts,
            oa_primary_topic = oa.primary_topic
        FROM (
            SELECT DISTINCT ON (corpusid) corpusid, oa_id
            FROM (
                SELECT corpusid, oa_id
                FROM read_parquet('/netfiles/compethicslab/scisciDB/mapping/papers/by_doi/publication_year=19*/*.parquet')
                UNION ALL
                SELECT corpusid, oa_id
                FROM read_parquet('/netfiles/compethicslab/scisciDB/mapping/papers/by_doi/publication_year=200*/*.parquet')
                UNION ALL
                SELECT corpusid, oa_id
                FROM read_parquet('/netfiles/compethicslab/scisciDB/mapping/papers/by_doi/publication_year=201*/*.parquet')
            ) all_lookup
            ORDER BY corpusid, oa_id
        ) lookup
        JOIN oa_works oa ON lookup.oa_id = oa.id
        WHERE s2.corpusid = lookup.corpusid AND s2.year < 2020;
    """)

    total_updated += conn.execute("""
        SELECT COUNT(*) FROM s2_papers
        WHERE year < 2020 AND oa_topics IS NOT NULL
    """).fetchone()[0]

    # Get enrichment stats
    total_s2 = conn.execute("SELECT COUNT(*) FROM s2_papers").fetchone()[0]
    enriched = conn.execute("SELECT COUNT(*) FROM s2_papers WHERE oa_topics IS NOT NULL").fetchone()[0]

    logger.info(f"Enriched {enriched:,} out of {total_s2:,} S2 papers ({enriched/total_s2*100:.1f}%)")
    return enriched, total_s2

def s2_extract_topic_categories(conn):
    """Extract top-level topic categories for easier analysis."""
    logger.info("Extracting topic categories...")

    conn.execute("""
        CREATE OR REPLACE TABLE s2_topic_categories AS
        WITH topic_extraction AS (
            SELECT
                corpusid,
                oa_primary_topic.domain.display_name as primary_domain,
                oa_primary_topic.field.display_name as primary_field,
                oa_primary_topic.subfield.display_name as primary_subfield,
                list_transform(oa_topics, t -> t.domain.display_name) as all_domains,
                list_transform(oa_topics, t -> t.field.display_name) as all_fields,
                list_transform(oa_concepts, c -> c.display_name) as all_concepts
            FROM s2_papers_enriched
            WHERE oa_topics IS NOT NULL
        )
        SELECT
            corpusid,
            primary_domain,
            primary_field,
            primary_subfield,
            list_distinct(list_flatten([all_domains])) as unique_domains,
            list_distinct(list_flatten([all_fields])) as unique_fields,
            list_slice(list_distinct(list_flatten([all_concepts])), 1, 10) as top_concepts
        FROM topic_extraction;
    """)

    # Get category stats
    categories = conn.execute("""
        SELECT primary_domain, COUNT(*) as papers
        FROM s2_topic_categories
        WHERE primary_domain IS NOT NULL
        GROUP BY primary_domain
        ORDER BY papers DESC
        LIMIT 10
    """).fetchall()

    logger.info("Top domains:")
    for domain, count in categories:
        logger.info(f"  {domain}: {count:,} papers")

    return categories


def main():
    parser = argparse.ArgumentParser(
        description="ENRICH step: Add derived fields"
    )
    parser.add_argument("--dataset", default="papers", help="Dataset name")
    parser.add_argument("--input", type=Path, default=Path("import"))
    parser.add_argument("--output", type=Path, default=Path("enrich"))
    parser.add_argument("--operation",
                       choices=["has_abstract", "has_fulltext", "openalex_topics", "topic_categories", "all"],
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
        elif args.operation == 'openalex_topics':
            logger.info("Adding OpenAlex topics and concepts...")
            s2_add_openalex_topics(conn)
        elif args.operation == 'topic_categories':
            logger.info("Extracting topic categories...")
            s2_extract_topic_categories(conn)
        elif args.operation == 'all':
            logger.info("Running all enrichment operations...")
            s2_has_abstract(conn)
            s2_has_fulltext(conn)
            s2_add_openalex_topics(conn)
            s2_extract_topic_categories(conn)

        logger.info("Enrichment completed successfully!")

    except Exception as e:
        logger.error(f"Enrichment failed: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()