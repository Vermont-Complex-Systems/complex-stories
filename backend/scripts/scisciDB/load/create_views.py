#!/usr/bin/env python3
"""
Create views and tables in DuckLake with proper schema handling.

Handles schema conflicts and creates optimized views for querying.
"""
import argparse
from pathlib import Path
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

    logger.info(f"[EXPORT] Attaching DuckLake...")
    conn.execute(f"""
            ATTACH 'ducklake:postgres:dbname={os.getenv("POSTGRES_DB")} host={os.getenv('POSTGRES_HOST')} user={os.getenv("POSTGRES_USER")}' AS scisciDB
            (DATA_PATH '{os.getenv("SCISCIDB_DATA_ROOT")}');
        """)
    conn.execute("USE scisciDB;")
    logger.info(f"[EXPORT] ✓ Connected to DuckLake")

    return conn


def main():
    parser = argparse.ArgumentParser(
        description="Create views and tables in DuckLake"
    )
    parser.add_argument(
        "db_name",
        help="openalex or semanticscholar"
    )
    parser.add_argument(
        "dataset_name",
        help="papers, works, authors, etc..."
    )

    args = parser.parse_args()

    try:
        conn = get_ducklake_connection()
        try:
            if args.db_name == 'openalex':
                print(f"Dropping {args.dataset_name}")
                conn.execute(f"""
                    DROP VIEW IF EXISTS oa_{args.dataset_name};
                """)

                conn.execute(f"""
                    CREATE VIEW oa_{args.dataset_name} AS                                                                                                       
                    SELECT * FROM read_parquet('{os.getenv("OA_DATA_ROOT")}/{args.dataset_name}/**/*.parquet', union_by_name=True);
                """)

            print(f"\n🎉 SUCCESS!")

        finally:
            conn.close()

    except Exception as e:
        print(f"❌ View creation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()