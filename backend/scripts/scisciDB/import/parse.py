#!/usr/bin/env python3
"""
IMPORT step: Parse and convert raw JSON to Parquet
Follows principled data processing - converts input/ to import/
"""
import argparse
import sys
from pathlib import Path
import duckdb
import json
import os
from dotenv import load_dotenv

load_dotenv()

def convert_s2orc_v2(conn: duckdb.DuckDBPyConnection, json_file: Path, output_file: Path) -> None:
    """
    S2ORC v2 converter: Parse nested annotations to proper STRUCT arrays
    Converts VARCHAR JSON strings → STRUCT types for fast queries
    """
    conn.execute(f"""
        COPY (
            SELECT 
                corpusid,
                openaccessinfo,
                title,
                authors,
                STRUCT_PACK(
                    text := body.text,
                    annotations := STRUCT_PACK(
                        section_header := from_json(
                            body.annotations.section_header,
                            '[{{"start": "BIGINT", "end": "BIGINT", "attributes": "JSON"}}]'
                        ),
                        sentence := from_json(
                            body.annotations.sentence,
                            '[{{"start": "BIGINT", "end": "BIGINT"}}]'
                        ),
                        paragraph := from_json(
                            body.annotations.paragraph,
                            '[{{"start": "BIGINT", "end": "BIGINT"}}]'
                        ),
                        bib_ref := from_json(
                            body.annotations.bib_ref,
                            '[{{"start": "BIGINT", "end": "BIGINT", "ref_id": "VARCHAR"}}]'
                        )
                    )
                ) as body,
                STRUCT_PACK(
                    text := bibliography.text,
                    annotations := from_json(
                        bibliography.annotations,
                        '{{"bib_entry": "VARCHAR", "bib_id": "JSON", "bib_title": "VARCHAR", "bib_venue": "VARCHAR", "bib_author_first_name": "JSON", "bib_author_last_name": "JSON"}}'
                    )
                ) as bibliography
            FROM read_json_auto('{json_file}')
        )
        TO '{output_file}'
        (FORMAT PARQUET, COMPRESSION 'zstd')
    """)

def convert_generic(conn: duckdb.DuckDBPyConnection, json_file: Path, output_file: Path) -> None:
    """
    Generic converter: Read JSON as-is, write to Parquet
    Works for papers, authors, venues, etc.
    """
    conn.execute(f"""
        COPY (SELECT * FROM read_json_auto('{json_file}', ignore_errors=true))
        TO '{output_file}' (FORMAT PARQUET, COMPRESSION 'zstd')
    """)

def parse_json_to_parquet(dbname: str, dataset_name: str) -> Path:
    """
    Convert JSON/JSON.GZ files to Parquet format
    
    Args:
        dataset_name: Name of dataset (papers, authors, s2orc_v2, etc.)
        
    Returns:
        Path to output directory with Parquet files
    """
    # dbname="openalex"
    # dataset_name="works"
    data_root = Path(os.getenv("S2_DATA_ROOT") if dbname == 's2' else os.getenv("OA_DATA_ROOT") )
    
    print(f"[IMPORT] Parsing {dataset_name} dataset (from {data_root})")
    
    # Find input directory
    dataset_input_dir = data_root/ dataset_name
    if not dataset_input_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_input_dir}")
    
    dataset_output_dir = dataset_input_dir
    print(f"[IMPORT] Input:  {dataset_input_dir}")
    print(f"[IMPORT] Output: {dataset_output_dir}")
    
    # Find all JSON files
    json_files = list(dataset_input_dir.glob("*.json")) + \
                 list(dataset_input_dir.glob("*.json.gz")) + \
                 list(dataset_input_dir.glob("**/*.gz"))
    
    # Filter out metadata files
    json_files = [f for f in json_files 
                  if not f.name.startswith(('release_', 'download_', 'parse_manifest'))]
    
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {dataset_input_dir}")
    
    print(f"[IMPORT] Found {len(json_files)} files to parse")
    
    # Setup DuckDB
    conn = duckdb.connect()
    
    # Parse each file
    parsed_files = []
    for i, json_file in enumerate(sorted(json_files), 1):
        # json_file = sorted(json_files)[156]
        print(f"[IMPORT] Parsing {i}/{len(json_files)}: {json_file.name}")
        
        output_file = json_file.parent  / (json_file.stem.replace('.json', '') + '.parquet')
        
        try:
            # Choose converter based on dataset
            if dataset_name == 's2orc_v2':
                convert_s2orc_v2(conn, json_file, output_file)
                print(f"[IMPORT] Using s2orc_v2 converter (structured annotations)")
            else:
                convert_generic(conn, json_file, output_file)
                print(f"[IMPORT] Using generic converter")
                
            
            # Get file sizes
            input_size_mb = json_file.stat().st_size / 1024 / 1024
            output_size_mb = output_file.stat().st_size / 1024 / 1024
            compression_ratio = (1 - output_size_mb / input_size_mb) * 100
            
            print(f"[IMPORT]   ✓ {output_file.name}")
            print(f"[IMPORT]     {input_size_mb:.1f} MB → {output_size_mb:.1f} MB "
                  f"({compression_ratio:.0f}% smaller)")
            
            parsed_files.append(output_file.name)
            
            # Cleanup JSON file
            # json_file.unlink(missing_ok=True)
            # print(f"[IMPORT]     Deleted {json_file.name}")
            
        except Exception as e:
            print(f"[IMPORT]   ✗ Failed: {e}")
            continue
    
    if not parsed_files:
        raise RuntimeError("No files were successfully parsed")
    
    # Save manifest
    manifest = {
        "dataset_name": dataset_name,
        "converter": "s2orc_v2" if dataset_name == 's2orc_v2' else "generic",
        "input_files": len(json_files),
        "parsed_files": len(parsed_files),
        "files": parsed_files,
        "output_dir": str(dataset_output_dir)
    }
    
    if dataset_name == 's2orc_v2':
        manifest["annotation_types"] = {
            "section_header": "STRUCT(start BIGINT, end BIGINT, attributes JSON)[]",
            "sentence": "STRUCT(start BIGINT, end BIGINT)[]",
            "paragraph": "STRUCT(start BIGINT, end BIGINT)[]",
            "bib_ref": "STRUCT(start BIGINT, end BIGINT, ref_id VARCHAR)[]"
        }
    
    manifest_file = dataset_output_dir / "parse_manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n[IMPORT] ✓ Parse complete!")
    print(f"[IMPORT] Parsed: {len(parsed_files)}/{len(json_files)} files")
    print(f"[IMPORT] Location: {dataset_output_dir}/")
    
    return dataset_output_dir


def main():
    parser = argparse.ArgumentParser(
        description="IMPORT step: Parse JSON to Parquet"
    )
    parser.add_argument(
        "db_name",
        help="Database name (open-alex, semanticscholar.)"
    )
    parser.add_argument(
        "dataset_name",
        help="Dataset name (papers, authors, s2orc_v2, etc.)"
    )
    
    args = parser.parse_args()
    
    try:
        parse_json_to_parquet(args.db_name, args.dataset_name)
        
        print(f"\n🎉 SUCCESS!")
        print(f"\n📋 Next steps:")
        print(f"   1. Run 'make validate' to check data quality")
        print(f"   2. Run 'make export' to load into DuckLake")
        
    except Exception as e:
        print(f"❌ Parse failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()