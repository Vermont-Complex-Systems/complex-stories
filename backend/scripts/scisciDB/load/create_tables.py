#!/usr/bin/env python3
"""
CREATE TABLES: Load parquet data into DuckDB tables with proper schemas

This script creates tables from parquet files using explicit schemas from openalex_schema.py
to avoid type casting issues when reading multiple files.
"""
import argparse
import sys
import duckdb
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def get_duckdb_connection():
    """Get DuckDB connection with DuckLake attached."""
    conn = duckdb.connect()

    # Attach DuckLake
    postgres_password = os.getenv('POSTGRES_PASSWORD')
    if not postgres_password:
        raise ValueError("POSTGRES_PASSWORD environment variable not set")

    print("Attaching DuckLake...")
    conn.execute(f"""
        ATTACH 'ducklake:postgres:dbname=complex_stories host=localhost user=jstonge1 password={postgres_password}'
        AS scisciDB (DATA_PATH '/netfiles/compethicslab/scisciDB/');
    """)

    conn.execute("USE scisciDB;")
    return conn
    
def create_oa_sources_table(conn, force=False):
    """Create oa_sources table from OpenAlex sources parquet files."""
    print("Creating oa_sources table...")

    if force:
        conn.execute("DROP TABLE IF EXISTS oa_sources;")

    # reverse ordering so that first parquet file is most recent schema
    # we got rid of a single file updated_date=2023-08-02/part_000.parquet because the schema was just differnet from the res
    files = conn.execute(f"SELECT * FROM glob('{os.getenv('OA_DATA_ROOT')}/sources/**/*parquet')").fetchall()
    files = sorted([x[0] for x in files], reverse=True)

    print("Loading data from parquet files...")
    try:
        conn.execute(f"""
            CREATE TABLE oa_sources AS SELECT
                * EXCLUDE(is_indexed_in_scopus),
            FROM read_parquet({files});
        """)

        # Get count for verification
        result = conn.execute("SELECT COUNT(*) FROM oa_sources;").fetchone()
        print(f"✓ oa_sources table created with {result[0]:,} records")

    except Exception as e:
        print(f"✗ Error loading data: {e}")
        raise

def create_oa_works_table(conn, force=False):
    """Create oa_works view from OpenAlex sources parquet files."""
    print("Creating oa_works view...")

    if force:
        conn.execute("DROP VIEW IF EXISTS oa_works;")

    # reverse ordering so that first parquet file is most recent schema
    # we got rid of 3 papers with different schema: 
    #   updated_date=2023-05-29/part_000.parquet
    #   updated_date=2023-05-17/part_000.parquet
    files = conn.execute(f"SELECT * FROM glob('{os.getenv('OA_DATA_ROOT')}/works/**/*parquet')").fetchall()
    files = sorted([x[0] for x in files], reverse=True)
    len(files)

    print("Loading data from parquet files...")
    try:
        conn.execute(f"""
            CREATE OR REPLACE TABLE oa_works AS SELECT * 
            FROM read_parquet({files}, union_by_name=True);
        """)

        # Get count for verification
        result = conn.execute("SELECT COUNT(*) FROM oa_works;").fetchone()
        print(f"✓ oa_sources table created with {result[0]:,} records")

    except Exception as e:
        print(f"✗ Error loading data: {e}")
        raise



def main():
    parser = argparse.ArgumentParser(description='Create tables from parquet data with proper schemas')
    parser.add_argument('--tables', nargs='+',
                       choices=['oa_sources', 'papersLookup', 'all'],
                       default=['all'],
                       help='Which tables to create')
    parser.add_argument('--force', action='store_true',
                       help='Drop existing tables before creating')

    args = parser.parse_args()

    try:
        conn = get_duckdb_connection()

        tables_to_create = args.tables
        
        for table in tables_to_create:
            if table == 'oa_sources':
                create_oa_sources_table(conn, force=args.force)
            elif table == 'papersLookup':
                print("❌ papersLookup has been moved to enrich/sync_db.py")
                print("Use: python enrich/sync_db.py --operation lookup")

        print("\n✅ Table creation completed!")

    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()