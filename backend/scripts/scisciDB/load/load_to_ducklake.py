#!/usr/bin/env python3
"""
EXPORT step: Load validated data into DuckLake
Following principled data processing - this is the final, auditable step
"""
import argparse
import sys
from pathlib import Path
import duckdb
from datetime import datetime
import logging
import os

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()



def create_ducklake_tables_if_not_exist(conn: duckdb.DuckDBPyConnection):
    """Create DuckLake tables if they don't exist"""

    # Check if tables exist
    tables = conn.execute("""
        SELECT table_name
        FROM ducklake_table
        WHERE table_name IN ('papers', 's2orc_v2')
    """).fetchall()

    existing_tables = [t[0] for t in tables]

    # Create papers table if needed
    if 'papers' not in existing_tables:
        logger.info("Creating papers table...")
        conn.execute("""
            CREATE TABLE papers AS
            SELECT * FROM read_parquet('dummy.parquet')
            WHERE 1=0
        """)
        logger.info("✓ Created papers table")

def update_ducklake(dataset_name: str, release_version: str = None):
    """
    Export validated data to DuckLake
    
    Args:
        dataset_name: Name of dataset (papers, s2orc_v2, etc.)
        release_version: Optional version identifier for tracking
    """
    logger.info(f"[EXPORT] Loading {dataset_name} into DuckLake")
    
    # Find the parsed data
    dataset_path = os.getenv("S2_DATA_ROOT") / dataset_name
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")
    
    parquet_files = list(dataset_path.glob("*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(f"No Parquet files found in {dataset_path}")
    
    logger.info(f"[EXPORT] Found {len(parquet_files)} Parquet files")
    logger.info(f"[EXPORT] Source: {dataset_path}")
    
    # Connect to DuckDB
    conn = duckdb.connect()
    
    try:
        # Attach DuckLake
        logger.info(f"[EXPORT] Attaching DuckLake...")
        conn.execute(f"""
            ATTACH 'ducklake:postgres:dbname={os.getenv("POSTGRES_DB")} host={os.getenv('POSTGRES_HOST')} user={os.getenv("POSTGRES_USER")}' AS scisciDB
            (DATA_PATH '{os.getenv("SCISCIDB_DATA_ROOT")}/');
        """)
        conn.execute("USE s2;")
        logger.info(f"[EXPORT] ✓ Connected to DuckLake")
        
        # Determine table name (use dataset_name as table name)
        table_name = dataset_name.replace('-', '_')  # SQL-safe name
        
        # Check if table exists
        table_exists = conn.execute(f"""
            SELECT COUNT(*) FROM ducklake_table WHERE table_name = '{table_name}'
        """).fetchone()[0] > 0
        
        if table_exists:
            # Table exists - do incremental update
            logger.info(f"[EXPORT] Table '{table_name}' exists - performing incremental update")
            
            current_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            logger.info(f"[EXPORT] Current rows: {current_count:,}")
            
            # Insert new records (assumes corpusid for s2orc, or id/paper_id for others)
            if dataset_name == 's2orc_v2':
                key_column = 'corpusid'
            elif dataset_name == 'papers':
                key_column = 'corpusid'
            elif dataset_name == 'authors':
                key_column = 'authorid'
            else:
                # Generic - assume 'id' column
                key_column = 'id'
            
            logger.info(f"[EXPORT] Inserting new records (key: {key_column})...")
            conn.execute(f"""
                INSERT INTO {table_name}
                SELECT * FROM read_parquet('{dataset_path}/*.parquet')
                WHERE {key_column} NOT IN (SELECT {key_column} FROM {table_name});
            """)
            
            logger.info(f"[EXPORT] Updating existing records...")
            # Note: This is a simplified update - adjust fields as needed
            conn.execute(f"""
                UPDATE {table_name}
                SET 
                    title = src.title,
                    authors = src.authors
                FROM read_parquet('{dataset_path}/*.parquet') as src
                WHERE {table_name}.{key_column} = src.{key_column};
            """)
            
            new_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            added = new_count - current_count
            logger.info(f"[EXPORT] ✓ Update complete")
            logger.info(f"[EXPORT]   Rows: {current_count:,} → {new_count:,} (+{added:,})")
            
        else:
            # Table doesn't exist - create from Parquet
            logger.info(f"[EXPORT] Creating table '{table_name}' from Parquet files...")
            
            conn.execute(f"""
                CREATE TABLE {table_name} AS 
                SELECT * FROM read_parquet('{dataset_path}/*.parquet');
            """)
            
            row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            logger.info(f"[EXPORT] ✓ Created table with {row_count:,} rows")
        
        # Record metadata (optional - requires update_log table)
        if release_version:
            try:
                conn.execute(f"""
                    INSERT INTO update_log (table_name, release_version, updated_at, operation)
                    VALUES (?, ?, ?, ?)
                """, [table_name, release_version, datetime.now(), 'update' if table_exists else 'create'])
                logger.info(f"[EXPORT] Logged update to update_log")
            except:
                # update_log table might not exist - that's ok
                pass
        
        logger.info(f"\n[EXPORT] ✓ Successfully loaded {dataset_name} into DuckLake")
        
    except Exception as e:
        logger.error(f"[EXPORT] Failed to update DuckLake: {e}")
        raise
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="EXPORT step: Load data into DuckLake"
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="Dataset name (papers, s2orc_v2, authors, etc.)"
    )
    parser.add_argument(
        "--release-version",
        help="Release version identifier (optional)"
    )
    
    args = parser.parse_args()

    try:
        update_ducklake(
            dataset_name=args.dataset,
            release_version=args.release_version
        )

        print(f"\n🎉 SUCCESS!")
        print(f"📋 Dataset '{args.dataset}' is now in DuckLake")
        print(f"\n💡 Query it:")
        print(f"   duckdb")
        print(f"   > ATTACH 'ducklake:postgres:...' AS scisciDB (...);")
        print(f"   > SELECT * FROM scisciDB.{args.dataset.replace('-', '_')} LIMIT 10;")

    except Exception as e:
        print(f"❌ Export failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()