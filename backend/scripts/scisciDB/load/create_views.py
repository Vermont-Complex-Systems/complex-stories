#!/usr/bin/env python3
"""
Create views and tables in DuckLake with proper schema handling.

Handles schema conflicts and creates optimized views for querying.
"""
import argparse
import sys
import duckdb
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


def get_ducklake_connection():
    """Get DuckDB connection with DuckLake attached."""
    postgres_password = os.getenv('POSTGRES_PASSWORD')
    if not postgres_password:
        raise ValueError("POSTGRES_PASSWORD environment variable not set")

    conn = duckdb.connect()

    # Attach DuckLake
    logger.info("Attaching DuckLake...")
    conn.execute(f"""
        ATTACH 'ducklake:postgres:dbname=complex_stories host=localhost user=jstonge1 password={postgres_password}'
        AS scisciDB (DATA_PATH '/netfiles/compethicslab/scisciDB/');
    """)
    conn.execute("USE scisciDB;")
    logger.info("✓ Connected to DuckLake")

    return conn


def create_openalex_works_view(conn: duckdb.DuckDBPyConnection, data_path: str):
    """
    Create oa_works view with correct schema, handling JSON/VARCHAR conflicts.

    The issue: OpenAlex works parquet files have schema conflicts between older
    and newer files (title as JSON vs VARCHAR). This forces the correct schema.
    """
    logger.info("Creating oa_works view with schema enforcement...")

    # Use a recent file to establish the correct VARCHAR schema
    template_file = f"{data_path}/works/updated_date=2025-09-20/part_001.parquet"

    try:
        # First verify the template file exists and has correct schema
        schema_check = conn.execute(f"""
            SELECT typeof(title) as title_type
            FROM '{template_file}'
            LIMIT 1
        """).fetchone()

        if schema_check[0] != 'VARCHAR':
            logger.warning(f"Template file has title type: {schema_check[0]}, expected VARCHAR")

        # Create view with explicit casting to ensure VARCHAR types for problematic fields
        conn.execute(f"""
            CREATE OR REPLACE VIEW oa_works AS
            SELECT
                id,
                doi,
                doi_registration_agency,
                CAST(display_name AS VARCHAR) as display_name,
                CAST(title AS VARCHAR) as title,
                publication_year,
                publication_date,
                CAST(language AS VARCHAR) as language,
                language,
                ids,
                primary_location,
                best_oa_location,
                type,
                type_crossref,
                type_id,
                indexed_in,
                open_access,
                authorships,
                institution_assertions,
                countries_distinct_count,
                institutions_distinct_count,
                is_retracted,
                is_paratext,
                concepts,
                mesh,
                locations_count,
                locations,
                referenced_works,
                referenced_works_count,
                sustainable_development_goals,
                keywords,
                grants,
                apc_list,
                apc_paid,
                cited_by_percentile_year,
                related_works,
                counts_by_year,
                cited_by_count,
                cited_by_api_url,
                updated_date,
                created_date,
                updated,
                authors_count,
                concepts_count,
                topics_count,
                has_fulltext,
                fulltext_origin,
                authorships_truncated,
                CAST(abstract_inverted_index AS VARCHAR) as abstract_inverted_index
            FROM read_parquet('{data_path}/works/**/*.parquet')
        """)

        # Test the view
        count = conn.execute("SELECT COUNT(*) FROM oa_works").fetchone()[0]
        logger.info(f"✓ Created oa_works view with {count:,} rows")

        # Verify schema is correct
        title_types = conn.execute("""
            SELECT typeof(title) as title_type, COUNT(*)
            FROM oa_works
            WHERE title IS NOT NULL
            GROUP BY typeof(title)
            LIMIT 5
        """).fetchall()

        logger.info(f"✓ Title field types in view: {title_types}")

    except Exception as e:
        logger.error(f"Failed to create oa_works view: {e}")
        # Fallback: create a simple view without the problematic template
        logger.info("Creating fallback view with basic casting...")
        conn.execute(f"""
            CREATE OR REPLACE VIEW oa_works AS
            SELECT
                id,
                CAST(title AS VARCHAR) as title,
                CAST(display_name AS VARCHAR) as display_name,
                publication_year,
                has_fulltext,
                CAST(abstract_inverted_index AS VARCHAR) as abstract_inverted_index
            FROM read_parquet('{data_path}/works/**/*.parquet')
        """)
        logger.info("✓ Created fallback oa_works view")


def list_available_views(conn: duckdb.DuckDBPyConnection):
    """List all available views in the database."""
    logger.info("Available views:")

    try:
        views = conn.execute("""
            SELECT table_name, table_type
            FROM information_schema.tables
            WHERE table_type = 'VIEW'
            ORDER BY table_name
        """).fetchall()

        for view_name, view_type in views:
            logger.info(f"  - {view_name} ({view_type})")

    except Exception as e:
        logger.error(f"Failed to list views: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Create views and tables in DuckLake"
    )
    parser.add_argument(
        "--openalex-works",
        action="store_true",
        help="Create oa_works view with proper schema handling"
    )
    parser.add_argument(
        "--s2-papers",
        action="store_true",
        help="Create s2_papers view"
    )
    parser.add_argument(
        "--list-views",
        action="store_true",
        help="List all available views"
    )
    parser.add_argument(
        "--data-path",
        default="/netfiles/compethicslab/scisciDB",
        help="Base path to data files (default: /netfiles/compethicslab/scisciDB)"
    )

    args = parser.parse_args()

    if not any([args.openalex_works, args.s2_papers, args.list_views]):
        parser.print_help()
        print("\nERROR: Must specify at least one action")
        sys.exit(1)

    try:
        conn = get_ducklake_connection()

        try:
            if args.openalex_works:
                # data_path=Path"/netfiles/compethicslab/scisciDB"
                openalex_data_path = f"{args.data_path}/openalex/data"
                create_openalex_works_view(conn, openalex_data_path)

            if args.list_views:
                list_available_views(conn)

            print(f"\n🎉 SUCCESS!")
            print(f"\n💡 Query your views:")
            print(f"   duckdb")
            print(f"   > ATTACH 'ducklake:postgres:...' AS scisciDB (...);")
            print(f"   > USE scisciDB;")
            if args.openalex_works:
                print(f"   > SELECT title FROM oa_works WHERE title IS NOT NULL LIMIT 5;")
            if args.s2_papers:
                print(f"   > SELECT title FROM s2_papers LIMIT 5;")

        finally:
            conn.close()

    except Exception as e:
        print(f"❌ View creation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()