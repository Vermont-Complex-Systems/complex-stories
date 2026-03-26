"""
One-time migration: read adapter parquet files for babynames and wikimedia/ngrams
and load their rows into the entity_mappings PostgreSQL table via the registry API.

Usage:
    # Dry run (default) — shows what would be inserted, touches nothing
    uv run python scripts/migrate_adapter_to_entity_mappings.py

    # Execute — calls the API and writes to the DB
    uv run python scripts/migrate_adapter_to_entity_mappings.py --execute

    # Custom API base and credentials
    uv run python scripts/migrate_adapter_to_entity_mappings.py --execute \\
        --api-base http://localhost:3001 \\
        --username admin --password admin123

Datasets migrated:
    - babynames/babynames (ducklake, 2 unique rows)
    - wikimedia/ngrams    (parquet_hive, 11 rows)

Datasets skipped:
    - wikimedia/revisions — adapter.parquet contains article metadata (identifier,
      name, revision_count, ...), not canonical entity mappings. Needs a separate
      design for "dimension catalogs". See data-governance.md TODO.
"""

import argparse
import glob
import sys
import os
import duckdb
import httpx


# ---------------------------------------------------------------------------
# Adapter sources — update paths here if data moves.
# ---------------------------------------------------------------------------

ADAPTERS = [
    {
        "domain": "babynames",
        "dataset_id": "babynames",
        "format": "ducklake",
        # Glob pattern — ducklake splits across multiple parquet files
        "path_glob": "/users/j/s/jstonge1/babynames/metadata.ducklake.files/main/adapter/*.parquet",
    },
    {
        "domain": "wikimedia",
        "dataset_id": "ngrams",
        "format": "parquet_hive",
        "path_glob": "/netfiles/compethicslab/wikimedia/1grams/adapter.parquet",
    },
]


def read_adapter(path_glob: str) -> list[dict]:
    """Read adapter parquet file(s) and return deduplicated rows as dicts."""
    files = glob.glob(path_glob)
    if not files:
        raise FileNotFoundError(f"No parquet files matched: {path_glob}")

    conn = duckdb.connect()
    rows = conn.execute(
        f"SELECT DISTINCT local_id, entity_id, entity_name, entity_ids "
        f"FROM read_parquet({files!r}) "
        f"ORDER BY local_id"
    ).fetchall()

    return [
        {
            "local_id": r[0],
            "entity_id": r[1],
            "entity_name": r[2],
            "entity_ids": list(r[3]) if r[3] is not None else None,
        }
        for r in rows
    ]


def get_auth_token(api_base: str, username: str, password: str) -> str:
    """Obtain a JWT access token from the API."""
    resp = httpx.post(
        f"{api_base}/auth/login",
        json={"username": username, "password": password},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def push_entities(
    api_base: str,
    token: str,
    domain: str,
    dataset_id: str,
    entities: list[dict],
) -> dict:
    """POST entity rows to the batch upsert endpoint."""
    resp = httpx.post(
        f"{api_base}/admin/registry/{domain}/{dataset_id}/entities",
        json=entities,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--execute", action="store_true", help="Actually write to the DB (default: dry run)")
    parser.add_argument("--api-base", default="http://localhost:3001", help="API base URL")
    parser.add_argument("--username", default=os.getenv("ADMIN_USERNAME", "admin"))
    parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD", ""))
    parser.add_argument("--token", default=os.getenv("FASTAPI_ADMIN_TOKEN", ""), help="Pre-generated JWT (skips login)")
    args = parser.parse_args()

    mode = "EXECUTE" if args.execute else "DRY RUN"
    print(f"=== Adapter → entity_mappings migration [{mode}] ===\n")

    token = None
    if args.execute:
        if args.token:
            token = args.token
            print("Using pre-generated token from FASTAPI_ADMIN_TOKEN.\n")
        else:
            print(f"Authenticating at {args.api_base} as '{args.username}'...")
            try:
                token = get_auth_token(args.api_base, args.username, args.password)
                print("Auth OK.\n")
            except Exception as e:
                print(f"Auth failed: {e}", file=sys.stderr)
                sys.exit(1)

    total_inserted = 0

    for adapter in ADAPTERS:
        domain = adapter["domain"]
        dataset_id = adapter["dataset_id"]
        label = f"{domain}/{dataset_id}"
        print(f"--- {label} ({adapter['format']}) ---")

        try:
            rows = read_adapter(adapter["path_glob"])
        except FileNotFoundError as e:
            print(f"  SKIP: {e}\n")
            continue

        print(f"  {len(rows)} unique rows found:")
        for r in rows:
            print(f"    local_id={r['local_id']!r:30s} entity_id={r['entity_id']!r:25s} name={r['entity_name']!r}")

        if args.execute:
            try:
                result = push_entities(args.api_base, token, domain, dataset_id, rows)
                n = result.get("entities_upserted", "?")
                print(f"  → Inserted {n} rows into entity_mappings.")
                total_inserted += len(rows)
            except httpx.HTTPStatusError as e:
                print(f"  ERROR: {e.response.status_code} {e.response.text}", file=sys.stderr)
        else:
            print(f"  [dry run] would insert {len(rows)} rows")

        print()

    if args.execute:
        print(f"Done. Total rows inserted: {total_inserted}")
    else:
        print("Dry run complete. Re-run with --execute to write to the DB.")


if __name__ == "__main__":
    main()
