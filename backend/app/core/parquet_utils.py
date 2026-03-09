"""
General-purpose DuckDB / Hive-parquet utilities shared across routers.

These helpers are dataset-agnostic — they work with any parquet_hive or
ducklake-format datalake registered in the system.
"""

from datetime import datetime, timedelta
from typing import List, Tuple
from fastapi import HTTPException


def get_parquet_paths(datalake, data_table_name: str) -> Tuple[List[str], List[str]]:
    """Construct parquet file paths for data table and adapter table.

    For parquet_hive format: paths in tables_metadata are absolute; adapter comes from entity_mapping.path.
    For ducklake format: paths are relative filenames; prepend data_location + /main/ + table_name/.
    """
    if not datalake.tables_metadata:
        raise HTTPException(
            status_code=500,
            detail="Datalake metadata is missing. Please re-register the datalake with proper tables_metadata."
        )

    data_fnames = datalake.tables_metadata.get(data_table_name)

    if not data_fnames:
        raise HTTPException(
            status_code=500,
            detail=f"Missing {data_table_name} file paths. Required: tables_metadata.{data_table_name}"
        )

    if datalake.data_format == "parquet_hive":
        data_path = data_fnames
        if not datalake.entity_mapping or not datalake.entity_mapping.get("path"):
            raise HTTPException(
                status_code=500,
                detail="Missing entity_mapping.path for parquet_hive format. Please re-register with entity_mapping."
            )
        adapter_path = [datalake.entity_mapping["path"]]
    else:
        # ducklake format: relative filenames, prepend data_location
        # NOTE: Don't URL-decode - the filesystem actually has %20 in directory names
        adapter_fnames = datalake.tables_metadata.get("adapter")
        if not adapter_fnames:
            raise HTTPException(
                status_code=500,
                detail="Missing adapter file paths. Required: tables_metadata.adapter"
            )
        data_path = [
            f"{datalake.data_location}/main/{data_table_name}/{fname}"
            for fname in data_fnames
        ]
        adapter_path = [
            f"{datalake.data_location}/main/adapter/{fname}"
            for fname in adapter_fnames
        ]

    return data_path, adapter_path


def compute_partition_starts(start_date: str, end_date: str, granularity: str) -> List[str]:
    """Compute partition start dates covering [start_date, end_date] using date arithmetic.

    Assumes no gaps in the data. For weekly/monthly granularities, snaps start_date
    back to the nearest partition boundary so that partial periods at the edges are included.

    Args:
        start_date: Start of the date range (YYYY-MM-DD).
        end_date: End of the date range (YYYY-MM-DD)
        granularity: One of "daily", "weekly", "monthly"

    Returns:
        Sorted list of partition start dates

    Example:
        >>> compute_partition_starts("2024-10-07", "2024-10-27", "weekly")
        ["2024-10-07", "2024-10-14", "2024-10-21"]
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    if granularity == "daily":
        current = start
    elif granularity == "weekly":
        current = start - timedelta(days=start.weekday())
    elif granularity == "monthly":
        current = start.replace(day=1)
    else:
        raise ValueError(f"Unknown granularity: {granularity}")

    partitions = []
    while current <= end:
        partitions.append(current.strftime("%Y-%m-%d"))
        if granularity == "daily":
            current += timedelta(days=1)
        elif granularity == "weekly":
            current += timedelta(weeks=1)
        elif granularity == "monthly":
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1, day=1)
            else:
                current = current.replace(month=current.month + 1, day=1)

    return partitions
