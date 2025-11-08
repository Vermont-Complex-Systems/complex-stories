#!/usr/bin/env python3
"""
IMPORT step: Parse and convert raw JSON to Parquet
Follows principled data processing - converts input/ to import/
"""
import argparse
import sys
from pathlib import Path
import duckdb
from duckdb.sqltypes import *
import json
import os
from dotenv import load_dotenv

columns = {
    # --- Scalar fields ---
    "id": "VARCHAR",
    "doi": "VARCHAR",
    "title": "VARCHAR",
    "display_name": "VARCHAR",
    "publication_year": "INTEGER",
    "publication_date": "DATE",
    "created_date": "TIMESTAMP",
    "updated_date": "TIMESTAMP",
    "language": "VARCHAR",
    "type": "VARCHAR",
    "type_crossref": "VARCHAR",
    "is_retracted": "BOOLEAN",
    "is_paratext": "BOOLEAN",
    "has_fulltext": "BOOLEAN",
    "fulltext_origin": "VARCHAR",
    "license": "VARCHAR",
    "fwci": "DOUBLE",
    "cited_by_count": "INTEGER",
    "countries_distinct_count": "INTEGER",
    "institutions_distinct_count": "INTEGER",
    "locations_count": "INTEGER",

    # --- Arrays of simple values ---
    "corresponding_author_ids": "VARCHAR[]",
    "corresponding_institution_ids": "VARCHAR[]",
    "referenced_works": "VARCHAR[]",
    "related_works": "VARCHAR[]",

    # --- Structured objects ---
    "biblio": "STRUCT(volume VARCHAR, issue VARCHAR, first_page VARCHAR, last_page VARCHAR)",
    "apc_list": "STRUCT(value DOUBLE, currency VARCHAR, provenance VARCHAR, value_usd DOUBLE)",
    "apc_paid": "STRUCT(value DOUBLE, currency VARCHAR, provenance VARCHAR, value_usd DOUBLE)",
    "citation_normalized_percentile": "STRUCT(value DOUBLE, is_in_top_1_percent BOOLEAN, is_in_top_10_percent BOOLEAN)",
    "counts_by_year": "STRUCT(year INTEGER, cited_by_count INTEGER)[]",

    # --- Nested complex arrays ---
    "authorships": "STRUCT(author_position VARCHAR, author STRUCT(id VARCHAR, display_name VARCHAR, orcid VARCHAR), institutions STRUCT(id VARCHAR, display_name VARCHAR, country_code VARCHAR, ror VARCHAR)[], is_corresponding BOOLEAN)[]",

    "concepts": "STRUCT(id VARCHAR, wikidata VARCHAR, display_name VARCHAR, level INTEGER, score DOUBLE)[]",

    "topics": "STRUCT(id VARCHAR, display_name VARCHAR, subfield STRUCT(id VARCHAR, display_name VARCHAR), field STRUCT(id VARCHAR, display_name VARCHAR), domain STRUCT(id VARCHAR, display_name VARCHAR))[]",

    "keywords": "STRUCT(keyword VARCHAR, score DOUBLE)[]",

    "mesh": "STRUCT(descriptor_ui VARCHAR, descriptor_name VARCHAR, qualifier_ui VARCHAR, qualifier_name VARCHAR, is_major_topic BOOLEAN)[]",

    "grants": "STRUCT(funder VARCHAR, funder_display_name VARCHAR, award_id VARCHAR)[]",

    "sustainable_development_goals": "STRUCT(id VARCHAR, display_name VARCHAR, score DOUBLE)[]",

    "locations": "STRUCT(is_oa BOOLEAN, landing_page_url VARCHAR, pdf_url VARCHAR, source STRUCT(id VARCHAR, display_name VARCHAR, issn_l VARCHAR, is_oa BOOLEAN, type VARCHAR))[]",

    # --- Other JSON objects (simpler) ---
    "primary_location": "STRUCT(id VARCHAR, display_name VARCHAR, landing_page_url VARCHAR, pdf_url VARCHAR)",
    "best_oa_location": "STRUCT(id VARCHAR, display_name VARCHAR, landing_page_url VARCHAR, pdf_url VARCHAR)",
    "open_access": "STRUCT(is_oa BOOLEAN, oa_status VARCHAR, oa_url VARCHAR)",

    # --- Text-heavy ---
    "abstract_inverted_index": "VARCHAR"
}

# from openalex_schema import works_columns
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

def convert_openalex(conn: duckdb.DuckDBPyConnection, json_file: Path, output_file: Path) -> None:
    """
    OpenAlex converter: Explicit column types for all fields

    Defines precise schema to prevent any auto-inference conflicts between JSON files.
    Based on OpenAlex works API schema.
    """
    conn.execute(f"""
    COPY (
        SELECT * FROM read_json(
            '{json_file}',
            columns={columns},
            ignore_errors=true
        )
    )
    TO '{output_file}' 
    (FORMAT PARQUET, COMPRESSION 'zstd');
    """)

def convert_semantic_scholar(conn: duckdb.DuckDBPyConnection, json_file: Path, output_file: Path) -> None:
    """
    Semantic Scholar converter: Standard JSON to Parquet conversion
    """
    conn.execute(f"""
        COPY (SELECT * FROM read_json_auto('{json_file}', ignore_errors=true))
        TO '{output_file}' (FORMAT PARQUET, COMPRESSION 'zstd')
    """)

def parse_json_to_parquet(dbname: str, dataset_name: str, force: bool = False) -> Path:
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

    # Cleanup and validation
    cleanup_empty_parquet_files(dataset_input_dir)
    json_files = filter_valid_json_files(json_files)

    # Setup DuckDB
    conn = duckdb.connect()

    # Parse each file
    parsed_files = process_json_files(conn, json_files, dataset_name, dbname, force)

    if not parsed_files:
        raise RuntimeError("No files were successfully parsed")

    # Create manifest and finish
    return create_manifest_and_finish(dataset_name, dataset_output_dir, json_files, parsed_files)

def cleanup_empty_parquet_files(dataset_dir: Path) -> None:
    """Remove any existing empty or broken parquet files."""
    print(f"[IMPORT] Cleaning up empty parquet files...")
    parquet_files = list(dataset_dir.glob("*.parquet")) + list(dataset_dir.glob("**/*.parquet"))
    removed_count = 0

    for parquet_file in parquet_files:
        if parquet_file.stat().st_size < 130:  # Very small parquet files are likely empty/broken
            print(f"[IMPORT]   Removing empty parquet: {parquet_file.name} ({parquet_file.stat().st_size} bytes)")
            parquet_file.unlink()
            removed_count += 1

    if removed_count > 0:
        print(f"[IMPORT] Removed {removed_count} empty parquet files")
    else:
        print(f"[IMPORT] No empty parquet files found")

def filter_valid_json_files(json_files: list) -> list:
    """Filter out empty JSON files that would cause issues."""
    valid_files = []
    for json_file in json_files:
        file_size = json_file.stat().st_size
        if file_size < 50:  # Skip files smaller than 10 bytes (essentially empty)
            print(f"[IMPORT] ⚠️  Skipping empty JSON file: {json_file.name} ({file_size} bytes)")
        else:
            valid_files.append(json_file)

    print(f"[IMPORT] Valid JSON files: {len(valid_files)}/{len(json_files)}")
    return valid_files

def should_skip_conversion(json_file: Path, force: bool = False) -> tuple[bool, Path]:
    """Check if conversion should be skipped (parquet already exists)."""
    output_file = json_file.parent / (json_file.stem.replace('.json', '') + '.parquet')

    if force:
        return False, output_file

    if output_file.exists() and output_file.stat().st_size > 100:
        return True, output_file
    return False, output_file

def process_json_files(conn: duckdb.DuckDBPyConnection, json_files: list, dataset_name: str, dbname: str, force: bool = False) -> list:
    """Process all JSON files, converting to parquet where needed."""
    parsed_files = []

    for i, json_file in enumerate(sorted(json_files), 1):
        print(f"[IMPORT] Processing {i}/{len(json_files)}: {json_file.name}")

        # Check if we should skip conversion
        should_skip, output_file = should_skip_conversion(json_file, force)

        if should_skip:
            print(f"[IMPORT]   ✓ Parquet already exists, skipping ({output_file.stat().st_size} bytes)")
            parsed_files.append(output_file.name)
            continue

        try:
            # Choose converter based on dataset and database
            if dataset_name == 's2orc_v2':
                convert_s2orc_v2(conn, json_file, output_file)
                print(f"[IMPORT] Using s2orc_v2 converter (structured annotations)")
            elif dbname == 'openalex':
                convert_openalex(conn, json_file, output_file)
                print(f"[IMPORT] Using OpenAlex converter (abstract_inverted_index as VARCHAR)")
            else:
                convert_semantic_scholar(conn, json_file, output_file)
                print(f"[IMPORT] Using Semantic Scholar converter")
                
            
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

    return parsed_files

def create_manifest_and_finish(dataset_name: str, dataset_output_dir: Path, json_files: list, parsed_files: list) -> Path:
    """Create manifest file and finish up the parsing process."""
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
        help="Database name (openalex, s2, etc.)"
    )
    parser.add_argument(
        "dataset_name",
        help="Dataset name (works, papers, authors, s2orc_v2, etc.)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reparse all files, even if parquet already exists"
    )
    
    args = parser.parse_args()
    
    try:
        if args.force:
            print("🔄 Force mode enabled - will reparse all files")

        parse_json_to_parquet(args.db_name, args.dataset_name, args.force)
        
        print(f"\n🎉 SUCCESS!")
        print(f"\n📋 Next steps:")
        print(f"   1. Run 'make validate' to check data quality")
        print(f"   2. Run 'make export' to load into DuckLake")
        
    except Exception as e:
        print(f"❌ Parse failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()