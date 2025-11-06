#!/usr/bin/env python3
"""
ENRICH step: Add derived fields and computed columns
Replaces MongoDB aggregation pipelines with DuckDB transformations
"""
import argparse
from pathlib import Path
import duckdb
import json

# updating s2orc

# ALTER TABLE papers ADD COLUMN has_abstract BOOLEAN;
# UPDATE papers AS p
# SET has_abstract = EXISTS (
#     SELECT 1 FROM abstracts AS o
#     WHERE o.corpusid = p.corpusid
# );

# ALTER TABLE papers ADD COLUMN has_fulltext BOOLEAN;
# UPDATE papers AS p
# SET has_fulltext = EXISTS (
#     SELECT 1 FROM s2orc_v2 AS o
#     WHERE o.corpusid = p.corpusid
# );

def add_primary_field(import_dir: Path, output_dir: Path, dataset_name: str):
    """
    Add primary_s2field - similar to your MongoDB add_primary_s2field()
    But done in DuckDB on Parquet files
    """
    print(f"[ENRICH] Adding primary_s2field to {dataset_name}")

    input_path = import_dir / dataset_name
    output_path = output_dir / dataset_name
    output_path.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect()

    # Add primary field using DuckDB
    conn.execute(f"""
        COPY (
            SELECT
                *,
                -- Extract primary field from s2fieldsofstudy array
                list_filter(
                    s2fieldsofstudy,
                    x -> x.source = 's2-fos-model'
                )[1].category as primary_s2field
            FROM read_parquet('{input_path}/*.parquet')
            WHERE s2fieldsofstudy IS NOT NULL
        )
        TO '{output_path}/'
        (FORMAT PARQUET, PARTITION_BY (corpusid % 100), COMPRESSION 'zstd')
    """)

    # Verify
    count = conn.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{output_path}/**/*.parquet')
        WHERE primary_s2field IS NOT NULL
    """).fetchone()[0]

    print(f"[ENRICH] ✓ Added primary_s2field to {count:,} papers")

    return output_path


def compute_citation_metrics(import_dir: Path, output_dir: Path):
    """
    Compute derived metrics - replaces MongoDB aggregations
    """
    print(f"[ENRICH] Computing citation metrics")

    conn = duckdb.connect()

    # Example: Add citation percentile, h-index, etc.
    conn.execute(f"""
        COPY (
            SELECT
                *,
                PERCENT_RANK() OVER (
                    PARTITION BY year
                    ORDER BY citationcount
                ) as citation_percentile,
                -- Add more derived metrics
            FROM read_parquet('{import_dir}/papers/*.parquet')
        )
        TO '{output_dir}/papers_enriched/'
        (FORMAT PARQUET, PARTITION_BY year, COMPRESSION 'zstd')
    """)

    print(f"[ENRICH] ✓ Citation metrics computed")


def main():
    parser = argparse.ArgumentParser(
        description="ENRICH step: Add derived fields"
    )
    parser.add_argument("dataset_name")
    parser.add_argument("--input", type=Path, default=Path("import"))
    parser.add_argument("--output", type=Path, default=Path("enrich"))
    parser.add_argument("--operation",
                       choices=["add_primary_field", "citation_metrics", "all"],
                       default="all")

    args = parser.parse_args()

    try:
        if args.operation in ["add_primary_field", "all"]:
            add_primary_field(args.input, args.output, args.dataset_name)

        if args.operation in ["citation_metrics", "all"]:
            compute_citation_metrics(args.input, args.output)

        print(f"\n[ENRICH] ✓ Enrichment complete!")

    except Exception as e:
        print(f"❌ Enrichment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()