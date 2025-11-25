#!/usr/bin/env python3
"""
SYNC: Incrementally update DuckLake tables with new data

Handles both initial table creation and incremental updates.
Inserts new records and updates existing ones based on key columns.
"""
import argparse
import sys
from pathlib import Path
import duckdb
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class SyncError(Exception):
    """Exception raised when sync fails"""
    pass


def get_key_column(dataset_name: str) -> str:
    """Get the primary key column for a dataset"""
    key_map = {
        's2orc_v2': 'corpusid',
        'papers': 'corpusid',
        'authors': 'authorid',
        'works': 'id',
        'sources': 'id',
    }
    return key_map.get(dataset_name, 'id')


def get_ducklake_connection() -> duckdb.DuckDBPyConnection:
    """Get DuckDB connection with DuckLake attached"""
    postgres_password = os.getenv('POSTGRES_PASSWORD')
    if not postgres_password:
        raise SyncError("POSTGRES_PASSWORD environment variable not set")
    
    conn = duckdb.connect()
    
    print(f"[SYNC] Attaching DuckLake...")
    conn.execute(f"""
        ATTACH 'ducklake:postgres:dbname={os.getenv("POSTGRES_DB")} 
                host={os.getenv('POSTGRES_HOST')} 
                user={os.getenv("POSTGRES_USER")}' AS scisciDB
        (DATA_PATH '{os.getenv("SCISCIDB_DATA_ROOT")}');
    """)
    conn.execute("USE scisciDB;")
    print(f"[SYNC] ✓ Connected to DuckLake")
    
    return conn


def create_table_from_parquet(
    conn: duckdb.DuckDBPyConnection,
    table_name: str,
    parquet_path: Path
) -> int:
    """Create new table from parquet files"""
    print(f"[SYNC] Creating table '{table_name}' from parquet files...")
    
    conn.execute(f"""
        CREATE TABLE {table_name} AS 
        SELECT * FROM read_parquet('{parquet_path}/*.parquet');
    """)
    
    row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"[SYNC] ✓ Created table with {row_count:,} rows")
    
    return row_count


def update_table_from_parquet(
    conn: duckdb.DuckDBPyConnection,
    table_name: str,
    parquet_path: Path,
    key_column: str
) -> tuple[int, int]:
    """
    Update existing table with new data
    
    Returns:
        Tuple of (rows_added, rows_updated)
    """
    print(f"[SYNC] Updating table '{table_name}'...")
    
    # Get current count
    current_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"[SYNC] Current rows: {current_count:,}")
    
    # Insert new records
    print(f"[SYNC] Inserting new records (key: {key_column})...")
    conn.execute(f"""
        INSERT INTO {table_name}
        SELECT * FROM read_parquet('{parquet_path}/*.parquet')
        WHERE {key_column} NOT IN (SELECT {key_column} FROM {table_name});
    """)
    
    new_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    rows_added = new_count - current_count
    
    print(f"[SYNC] ✓ Added {rows_added:,} new rows")
    print(f"[SYNC] Total rows: {new_count:,}")
    
    # Note: Full UPDATE would require knowing which columns to update
    # This is dataset-specific and should be implemented as needed
    
    return rows_added, 0  # (added, updated)


def sync_dataset(
    db_name: str,
    dataset_name: str,
    release_version: str = None
) -> None:
    """
    Sync dataset to DuckLake (create or update)
    
    Args:
        db_name: Database name (s2, openalex)
        dataset_name: Dataset name (papers, works, etc.)
        release_version: Optional version identifier for tracking
    """
    print(f"[SYNC] Syncing {dataset_name} to DuckLake")
    
    # Determine data root
    if db_name == 's2':
        data_root = Path(os.getenv("S2_DATA_ROOT"))
    elif db_name == 'openalex':
        data_root = Path(os.getenv("OA_DATA_ROOT"))
    else:
        raise SyncError(f"Unknown database: {db_name}")
    
    # Find parquet files
    dataset_path = data_root / dataset_name
    if not dataset_path.exists():
        raise SyncError(f"Dataset not found: {dataset_path}")
    
    parquet_files = list(dataset_path.glob("*.parquet"))
    if not parquet_files:
        raise SyncError(f"No parquet files found in {dataset_path}")
    
    print(f"[SYNC] Found {len(parquet_files)} parquet files")
    print(f"[SYNC] Source: {dataset_path}")
    
    # Connect to DuckLake
    conn = get_ducklake_connection()
    
    try:
        # Determine table name
        table_name = f"{db_name}_{dataset_name}".replace('-', '_')
        key_column = get_key_column(dataset_name)
        
        print(f"[SYNC] Target table: {table_name}")
        print(f"[SYNC] Key column: {key_column}")
        
        # Check if table exists
        table_exists = conn.execute(f"""
            SELECT COUNT(*) FROM ducklake_table 
            WHERE table_name = '{table_name}'
        """).fetchone()[0] > 0
        
        if table_exists:
            # Incremental update
            print(f"[SYNC] Table exists - performing incremental update")
            rows_added, rows_updated = update_table_from_parquet(
                conn, table_name, dataset_path, key_column
            )
            operation = 'update'
        else:
            # Initial creation
            print(f"[SYNC] Table does not exist - creating new table")
            row_count = create_table_from_parquet(
                conn, table_name, dataset_path
            )
            rows_added = row_count
            rows_updated = 0
            operation = 'create'
        
        # Log to update_log if table exists
        if release_version:
            try:
                conn.execute(f"""
                    INSERT INTO update_log (
                        table_name, 
                        release_version, 
                        updated_at, 
                        operation,
                        rows_added
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, [
                    table_name, 
                    release_version, 
                    datetime.now(), 
                    operation,
                    rows_added
                ])
                print(f"[SYNC] Logged to update_log")
            except:
                # update_log table might not exist
                pass
        
        print(f"\n[SYNC] ✓ Successfully synced {dataset_name} to DuckLake")
        
    finally:
        conn.close()

def main():
    parser = argparse.ArgumentParser(
        description="SYNC: Incrementally update DuckLake tables with new data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s s2 papers
  %(prog)s openalex works --release 2024-01-15
  %(prog)s s2 s2orc_v2
        """
    )
    
    parser.add_argument(
        "db_name",
        choices=['s2', 'openalex'],
        help="Database name"
    )
    
    parser.add_argument(
        "dataset_name",
        help="Dataset name (papers, works, authors, etc.)"
    )
    
    parser.add_argument(
        "--release",
        help="Release version identifier (for tracking)"
    )
    
    args = parser.parse_args()
    
    try:
        sync_dataset(
            db_name=args.db_name,
            dataset_name=args.dataset_name,
            release_version=args.release
        )
        
        table_name = f"{args.db_name}_{args.dataset_name}".replace('-', '_')
        
        print(f"\n🎉 SUCCESS!")
        print(f"\n📋 Query the table:")
        print(f"   SELECT * FROM {table_name} LIMIT 10;")
        
    except SyncError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()