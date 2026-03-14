"""
Partition continuity tests for parquet_hive datasets.

For every dataset that:
  - has data_format = "parquet_hive"
  - has an endpoint_schema with type = "types-counts" and a time_dimension

...we verify that every partition expected between avail_min and avail_max
actually exists on disk, per granularity and entity recorded in
partitioning.available.

Run:
    cd backend && uv run pytest tests/test_registry_continuity.py -v
"""

import os
import duckdb
import pytest
from urllib.parse import quote
from sqlalchemy import create_engine, text

from app.core.parquet_utils import compute_partition_starts

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://jstonge1@localhost/complex_stories"
)
SYNC_URL = DATABASE_URL.replace("+asyncpg", "+psycopg")

_GRANULARITY_TO_TIME_COL = {"daily": "date", "weekly": "week", "monthly": "month"}


def _collect_test_cases():
    """
    Query the registry and return one pytest.param per
    (domain, dataset_id, granularity, local_id) combination that has
    a types-counts endpoint schema with a time_dimension.
    """
    try:
        engine = create_engine(SYNC_URL)
        with engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT domain, dataset_id, data_location,
                       partitioning, endpoint_schemas
                FROM datasets
                WHERE data_format = 'parquet_hive'
                  AND endpoint_schemas IS NOT NULL
            """)).fetchall()
    except Exception as e:
        pytest.skip(f"Cannot connect to registry DB: {e}", allow_module_level=True)
        return []

    cases = []
    for domain, dataset_id, data_location, partitioning, endpoint_schemas in rows:
        schemas = endpoint_schemas or []
        has_types_counts = any(
            s.get("type") == "types-counts" and s.get("time_dimension")
            for s in schemas
        )
        if not has_types_counts:
            continue

        for granularity, gran_data in (partitioning or {}).items():
            time_column = _GRANULARITY_TO_TIME_COL.get(granularity)
            if not time_column:
                continue

            for local_id, bounds in gran_data.get("available", {}).items():
                avail_min = bounds.get("min")
                avail_max = bounds.get("max")
                if not avail_min or not avail_max:
                    continue

                cases.append(pytest.param(
                    data_location, granularity, time_column,
                    local_id, avail_min, avail_max,
                    id=f"{domain}/{dataset_id}/{granularity}/{local_id}",
                ))

    return cases


@pytest.mark.parametrize(
    "data_location,granularity,time_column,local_id,avail_min,avail_max",
    _collect_test_cases(),
)
def test_partition_continuity(
    data_location, granularity, time_column, local_id, avail_min, avail_max
):
    """All expected partitions between avail_min and avail_max must exist on disk."""
    encoded = quote(local_id, safe="")
    glob_path = (
        f"{data_location}/{granularity}/country={encoded}"
        f"/{time_column}=*/data_0.parquet"
    )

    conn = duckdb.connect()
    existing = {
        row[0].split(f"{time_column}=")[1].split("/")[0]
        for row in conn.execute("SELECT * FROM glob(?)", [glob_path]).fetchall()
    }

    expected = compute_partition_starts(avail_min, avail_max, granularity)
    missing = [p for p in expected if p not in existing]

    assert not missing, (
        f"Missing {len(missing)}/{len(expected)} {granularity} partitions "
        f"for '{local_id}' between {avail_min} and {avail_max}.\n"
        f"Missing: {missing[:10]}{'...' if len(missing) > 10 else ''}\n"
        f"Hint: re-run the ingestion pipeline or update partitioning.available "
        f"in the registry to reflect actual data bounds."
    )
