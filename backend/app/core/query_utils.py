"""Shared DuckDB query utilities for registry-driven types-counts datasets.

Used by any router that loads data from a registered dataset with
endpoint_schema.type == 'types-counts'.  Currently consumed by:
  - routers/storywrangler.py  (allotax2)
  - routers/wikimedia.py      (top-ngrams3)

Three time cases handled by load_system:
  1. No time axis   (parquet, no time_dimension)         — compare entities directly
  2. Time column    (parquet/ducklake, time_dimension)   — WHERE year BETWEEN ...
  3. Hive-partitioned time (parquet_hive, granularities) — path-level entity+time
"""

from typing import List, Optional
from urllib.parse import quote

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.registry import EntityMapping


async def resolve_entity(
    db: AsyncSession, domain: str, dataset: str, entity_id: str
) -> EntityMapping:
    """Resolve a global entity_id → EntityMapping row.

    Raises 400 if the entity is not found in the mapping table for this dataset.
    """
    result = await db.execute(
        select(EntityMapping).where(
            EntityMapping.domain == domain,
            EntityMapping.dataset_id == dataset,
            EntityMapping.entity_id == entity_id,
        )
    )
    em = result.scalar_one_or_none()
    if not em:
        raise HTTPException(
            status_code=400,
            detail=f"Entity '{entity_id}' not found in entity mappings for {domain}/{dataset}",
        )
    return em


def resolve_flat_path(dataset_obj) -> str:
    """Return a DuckDB read_parquet() expression for non-hive datasets.

    - parquet:          reads data_location directly (single flat file)
    - ducklake/duckdb:  reads the parquet files listed in the first non-adapter
                        entry of format_config.tables_metadata

    Raises 400 for parquet_hive — those use path-based loading in load_system.
    """
    fmt = dataset_obj.data_format
    if fmt == "parquet":
        return f"'{dataset_obj.data_location}'"
    if fmt in ("ducklake", "duckdb"):
        tm = (dataset_obj.format_config or {}).get("tables_metadata", {})
        for key, files in tm.items():
            if key != "adapter" and files:
                if len(files) == 1:
                    return f"'{files[0]}'"
                files_expr = ", ".join(f"'{f}'" for f in files)
                return f"[{files_expr}]"
    raise HTTPException(
        status_code=400,
        detail=(
            f"Cannot resolve path for data_format '{fmt}'. "
            "Ensure format_config.tables_metadata has a non-adapter key with file paths."
        ),
    )


def load_system(
    conn,
    dataset_obj,
    local_id: Optional[str],
    dates: Optional[List[str]],
    filter_vals: dict,
    granularity: Optional[str],
    limit: int,
) -> dict:
    """Load types-counts for one system, handling all three time cases.

    Branches on data_format:
    - parquet_hive: path-based — entity and time are hive partition keys.
                    Reads only the relevant partition directories.
    - parquet / ducklake / duckdb: WHERE-based — entity and time are column values.

    Column names come from endpoint_schema (type_column / count_column),
    defaulting to 'types' / 'counts' for datasets that follow the convention.

    Returns {"types": [...], "counts": [...]} ready for allotax or direct serialization.
    """
    ep = dataset_obj.endpoint_schema or {}
    entity_col = (dataset_obj.entity_mapping or {}).get("local_id_column")
    type_col  = ep.get("type_column",  "types")
    count_col = ep.get("count_column", "counts")

    if dataset_obj.data_format == "parquet_hive":
        # Entity and time filtering happen at the path level
        time_col = ep["granularities"][granularity]  # already validated by caller
        encoded = quote(local_id, safe="") if local_id else "*"
        glob_path = (
            f"{dataset_obj.data_location}/{granularity}"
            f"/{entity_col}={encoded}/{time_col}=*/data_0.parquet"
        )

        conditions, params = [], []
        if dates:
            conditions.append(f"{time_col} BETWEEN ? AND ?")
            params.extend(dates)
        for col, val in filter_vals.items():
            conditions.append(f"{col} = ?")
            params.append(val)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        rows = conn.execute(
            f"""
            SELECT {type_col}, SUM({count_col}) AS counts
            FROM read_parquet('{glob_path}')
            {where}
            GROUP BY {type_col}
            ORDER BY counts DESC
            LIMIT ?
            """,
            [*params, limit],
        ).fetchall()

    else:
        # Entity and time filtering happen via WHERE clauses
        time_col = ep.get("time_dimension")
        path_expr = resolve_flat_path(dataset_obj)

        conditions, params = [], []
        if entity_col and local_id is not None:
            conditions.append(f"{entity_col} = ?")
            params.append(local_id)
        if time_col and dates:
            conditions.append(f"{time_col} BETWEEN ? AND ?")
            params.extend(dates)
        for col, val in filter_vals.items():
            conditions.append(f"{col} = ?")
            params.append(val)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        rows = conn.execute(
            f"""
            SELECT {type_col}, SUM({count_col}) AS counts
            FROM read_parquet({path_expr})
            {where}
            GROUP BY {type_col}
            ORDER BY counts DESC
            LIMIT ?
            """,
            [*params, limit],
        ).fetchall()

    return {"types": [r[0] for r in rows], "counts": [float(r[1]) for r in rows]}
