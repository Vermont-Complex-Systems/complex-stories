#!/usr/bin/env python3
"""
IMPORT step: Validate parsed data quality
Follows principled data processing - check before export
"""
import argparse
from pathlib import Path
import duckdb
import json
import sys

def validate_dataset(import_dir: Path, dataset_name: str):
    """Validate parsed Parquet files"""
    
    print(f"[VALIDATE] Checking {dataset_name} data quality")
    
    dataset_dir = import_dir / dataset_name
    parquet_files = list(dataset_dir.glob("*.parquet"))
    
    if not parquet_files:
        raise FileNotFoundError(f"No Parquet files in {dataset_dir}")
    
    print(f"[VALIDATE] Found {len(parquet_files)} files")
    
    # Run validation checks
    conn = duckdb.connect()
    
    checks = []
    
    # Check 1: Can read all files
    print(f"[VALIDATE] Check 1: File readability")
    try:
        result = conn.execute(f"""
            SELECT COUNT(*) as total_rows
            FROM read_parquet('{dataset_dir}/*.parquet')
        """).fetchone()
        total_rows = result[0]
        print(f"[VALIDATE]   ✓ All files readable: {total_rows:,} total rows")
        checks.append({"check": "readability", "passed": True, "rows": total_rows})
    except Exception as e:
        print(f"[VALIDATE]   ✗ Failed to read files: {e}")
        checks.append({"check": "readability", "passed": False, "error": str(e)})
        raise
    
    # Check 2: Schema consistency
    print(f"[VALIDATE] Check 2: Schema consistency")
    try:
        schema = conn.execute(f"""
            DESCRIBE SELECT * FROM read_parquet('{dataset_dir}/*.parquet')
        """).fetchdf()
        print(f"[VALIDATE]   ✓ Schema: {len(schema)} columns")
        checks.append({"check": "schema", "passed": True, "columns": len(schema)})
    except Exception as e:
        print(f"[VALIDATE]   ✗ Schema inconsistent: {e}")
        checks.append({"check": "schema", "passed": False, "error": str(e)})
        raise
    
    # Check 3: No nulls in key columns (dataset-specific)
    if dataset_name == "papers":
        print(f"[VALIDATE] Check 3: Key column integrity")
        try:
            nulls = conn.execute(f"""
                SELECT 
                    SUM(CASE WHEN corpusid IS NULL THEN 1 ELSE 0 END) as null_corpusid,
                    SUM(CASE WHEN title IS NULL THEN 1 ELSE 0 END) as null_title
                FROM read_parquet('{dataset_dir}/*.parquet')
            """).fetchone()
            
            if nulls[0] > 0:
                print(f"[VALIDATE]   ⚠ Warning: {nulls[0]} rows with null corpusid")
            if nulls[1] > 0:
                print(f"[VALIDATE]   ⚠ Warning: {nulls[1]} rows with null title")
            
            print(f"[VALIDATE]   ✓ Key columns checked")
            checks.append({"check": "keys", "passed": True, 
                          "null_corpusid": nulls[0], "null_title": nulls[1]})
        except Exception as e:
            print(f"[VALIDATE]   ⚠ Could not check keys: {e}")
            checks.append({"check": "keys", "passed": False, "error": str(e)})
    
    # Save validation report
    report = {
        "dataset_name": dataset_name,
        "total_files": len(parquet_files),
        "checks": checks,
        "passed": all(c["passed"] for c in checks)
    }
    
    report_file = dataset_dir / "validation_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n[VALIDATE] ✓ Validation complete!")
    print(f"[VALIDATE] Report: {report_file}")
    
    if not report["passed"]:
        raise RuntimeError("Validation failed - see report for details")


def main():
    parser = argparse.ArgumentParser(
        description="IMPORT step: Validate data quality"
    )
    parser.add_argument(
        "dataset_name",
        help="Dataset name (papers, authors, etc.)"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("import"),
        help="Input directory (default: import/)"
    )
    
    args = parser.parse_args()
    
    try:
        validate_dataset(args.input, args.dataset_name)
        print(f"\n🎉 Data quality checks passed!")
        print(f"\n📋 Next step: Run 'make export' to load into DuckLake")
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()