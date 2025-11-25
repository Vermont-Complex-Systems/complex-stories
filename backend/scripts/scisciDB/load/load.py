#!/usr/bin/env python3
"""
LOAD: Create tables and views in DuckLake from parquet data

Loads parquet datasets into DuckLake as queryable tables and views.
Supports both automatic view creation and manual table creation with schema handling.
"""
import argparse
import sys
import duckdb
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class LoadError(Exception):
    """Exception raised when loading fails"""
    pass


def get_ducklake_connection() -> duckdb.DuckDBPyConnection:
    """Get DuckDB connection with DuckLake attached"""
    postgres_password = os.getenv('POSTGRES_PASSWORD')
    if not postgres_password:
        raise LoadError("POSTGRES_PASSWORD environment variable not set")
    
    conn = duckdb.connect()
    
    print(f"[LOAD] Attaching DuckLake...")
    conn.execute(f"""
        ATTACH 'ducklake:postgres:dbname={os.getenv("POSTGRES_DB")} 
                host={os.getenv('POSTGRES_HOST')} 
                user={os.getenv("POSTGRES_USER")}' AS scisciDB
        (DATA_PATH '{os.getenv("SCISCIDB_DATA_ROOT")}');
    """)
    conn.execute("USE scisciDB;")
    print(f"[LOAD] ✓ Connected to DuckLake")
    
    return conn

def create_view(conn: duckdb.DuckDBPyConnection, db_name: str, dataset_name: str, force: bool = False) -> None:
    """
    Create view for dataset in DuckLake
    
    This is the simple, automatic approach - just creates a view over parquet files.
    Use this for most datasets unless you need special schema handling.
    Always drops existing view/table with the same name.
    """
    # Determine data root and view name
    if db_name == 'openalex':
        data_root = os.getenv("OA_DATA_ROOT")
        view_name = f"oa_{dataset_name}"
    elif db_name == 's2':
        data_root = os.getenv("S2_DATA_ROOT")
        view_name = f"s2_{dataset_name}"
    else:
        raise LoadError(f"Unknown database: {db_name}")
    
    if not data_root:
        raise LoadError(f"Data root not configured for {db_name}")
    
    print(f"[LOAD] Creating view: {view_name}")
    print(f"[LOAD] Data source: {data_root}/{dataset_name}")
    
    # Always drop existing view/table
    conn.execute(f"DROP VIEW IF EXISTS {view_name};")
    conn.execute(f"DROP TABLE IF EXISTS {view_name};")
    print(f"[LOAD] Dropped existing view/table (if any)")
    
    # Create new view
    conn.execute(f"""
        CREATE VIEW {view_name} AS
        SELECT * FROM read_parquet(
            '{data_root}/{dataset_name}/**/*.parquet',
            union_by_name=true
        );
    """)
    print(f"[LOAD] ✓ Created view: {view_name}")
    
    # Verify view
    count = conn.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()[0]
    print(f"[LOAD] Record count: {count:,}")

def create_oa_sources_table(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Create oa_sources table from OpenAlex sources parquet files
    
    Uses reverse ordering so most recent schema is used first.
    Excludes is_indexed_in_scopus column which has schema conflicts.
    Always drops and recreates the table.
    """
    print("[LOAD] Creating oa_sources table...")
    
    # Always drop existing table
    conn.execute("DROP TABLE IF EXISTS oa_sources;")
    print("[LOAD] Dropped existing table (if any)")
    
    # Get files in reverse order (newest schema first)
    data_root = os.getenv('OA_DATA_ROOT')
    files = conn.execute(f"SELECT * FROM glob('{data_root}/sources/**/*.parquet')").fetchall()
    files = sorted([x[0] for x in files], reverse=True)
    
    print(f"[LOAD] Loading {len(files)} parquet files...")
    
    conn.execute(f"""
        CREATE TABLE oa_sources AS 
        SELECT * EXCLUDE(is_indexed_in_scopus)
        FROM read_parquet({files});
    """)
    
    # Verify
    count = conn.execute("SELECT COUNT(*) FROM oa_sources;").fetchone()[0]
    print(f"[LOAD] ✓ oa_sources table created with {count:,} records")


def create_oa_works_table(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Create oa_works table from OpenAlex works parquet files
    
    Uses reverse ordering and union_by_name to handle schema evolution.
    Always drops and recreates the table.
    """
    print("[LOAD] Creating oa_works table...")
    
    # Always drop existing table
    conn.execute("DROP TABLE IF EXISTS oa_works;")
    print("[LOAD] Dropped existing table (if any)")
    
    # Get files in reverse order (newest schema first)
    data_root = os.getenv('OA_DATA_ROOT')
    files = conn.execute(f"SELECT * FROM glob('{data_root}/works/**/*.parquet')").fetchall()
    files = sorted([x[0] for x in files], reverse=True)
    
    print(f"[LOAD] Loading {len(files)} parquet files...")
    
    conn.execute(f"""
        CREATE TABLE oa_works AS 
        SELECT * FROM read_parquet({files}, union_by_name=true);
    """)
    
    # Verify
    count = conn.execute("SELECT COUNT(*) FROM oa_works;").fetchone()[0]
    print(f"[LOAD] ✓ oa_works table created with {count:,} records")


def create_oa_authors_table(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Create oa_authors table from OpenAlex authors parquet files
    
    Always drops and recreates the table.
    """
    print("[LOAD] Creating oa_authors table...")
    
    # Always drop existing table
    conn.execute("DROP TABLE IF EXISTS oa_authors;")
    print("[LOAD] Dropped existing table (if any)")
    
    # Get files in reverse order (newest schema first)
    data_root = os.getenv('OA_DATA_ROOT')
    files = conn.execute(f"SELECT * FROM glob('{data_root}/authors/**/*.parquet')").fetchall()
    files = sorted([x[0] for x in files], reverse=True)
    
    # Only use first 600 files (schema conflicts in older files)
    print(f"[LOAD] Loading {len(files)}/{len(files)} parquet files...")
    
    conn.execute(f"""
        CREATE TABLE oa_authors AS 
        SELECT * FROM read_parquet({files});
    """)
    
    # Verify
    count = conn.execute("SELECT COUNT(*) FROM oa_authors;").fetchone()[0]
    print(f"[LOAD] ✓ oa_authors table created with {count:,} records")


def main():
    parser = argparse.ArgumentParser(
        description="LOAD: Create tables and views in DuckLake from parquet data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create simple views (recommended for most datasets)
  %(prog)s view openalex works
  %(prog)s view s2 papers --force
  
  # Create specialized tables (always drops existing table)
  %(prog)s table oa_sources
  %(prog)s table oa_works
  %(prog)s table oa_authors
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # VIEW subcommand
    view_parser = subparsers.add_parser('view', help='Create a view over parquet files')
    view_parser.add_argument('db_name', choices=['openalex', 's2'], help='Database name')
    view_parser.add_argument('dataset_name', help='Dataset name')
    view_parser.add_argument('--force', action='store_true', help='Drop existing view before creating')
    
    # TABLE subcommand (always drops existing)
    table_parser = subparsers.add_parser('table', help='Create a table with special schema handling (always drops existing)')
    table_parser.add_argument(
        'table_name',
        choices=['oa_sources', 'oa_works', 'oa_authors'],
        help='Table to create'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        conn = get_ducklake_connection()
        
        try:
            if args.command == 'view':
                create_view(conn, args.db_name, args.dataset_name, args.force)
                print(f"\n🎉 SUCCESS!")
                print(f"\n📋 Query the view:")
                view_name = f"{args.db_name}_{args.dataset_name}"
                print(f"   SELECT * FROM {view_name} LIMIT 10;")
            
            elif args.command == 'table':
                if args.table_name == 'oa_sources':
                    create_oa_sources_table(conn)
                elif args.table_name == 'oa_works':
                    create_oa_works_table(conn)
                elif args.table_name == 'oa_authors':
                    create_oa_authors_table(conn)
                
                print(f"\n🎉 SUCCESS!")
                print(f"\n📋 Query the table:")
                print(f"   SELECT * FROM {args.table_name} LIMIT 10;")
        
        finally:
            conn.close()
    
    except LoadError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()