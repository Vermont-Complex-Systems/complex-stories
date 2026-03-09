"""
Storywrangler API — instruments from the Vermont Complex Systems Institute.

Currently includes:
  - Allotaxonometer: rank-turbulence divergence between two ngram distributions.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from urllib.parse import quote

from ..core.database import get_db_session
from ..core.duckdb_client import get_duckdb_client
from ..core.parquet_utils import get_parquet_paths, compute_partition_starts
from ..models.datasets import Dataset

router = APIRouter()


def _load_ngrams(conn, datalake, table_name: str, time_column: str,
                 date_range: List[str], location: str, limit: int) -> dict:
    """Load top ngrams for one (date_range, location) system from a datalake.

    Returns a dict with "types" and "counts" lists ready for allotax input.
    """
    ngrams_path, adapter_path = get_parquet_paths(datalake, table_name)

    # Resolve entity_id → local_id via adapter
    adapter_row = conn.execute(
        "SELECT local_id FROM read_parquet(?) WHERE entity_id = ? LIMIT 1",
        [adapter_path, location]
    ).fetchone()
    if not adapter_row:
        raise HTTPException(status_code=400, detail=f"Location '{location}' not found in adapter")
    local_geo = quote(adapter_row[0], safe='')

    # Filter to relevant partition directories
    granularity = {v[1]: k for k, v in {
        "daily": ("wikigrams", "date"),
        "weekly": ("wikigrams_weekly", "week"),
        "monthly": ("wikigrams_monthly", "month"),
    }.items()}.get(time_column, "daily")
    partition_starts = compute_partition_starts(date_range[0], date_range[1], granularity)

    filtered_path = [
        p for p in ngrams_path
        if any(f"{time_column}={ps}" in p for ps in partition_starts)
        and f"geo={local_geo}" in p
    ]

    if not filtered_path:
        raise HTTPException(
            status_code=400,
            detail=f"No data found for {date_range[0]} to {date_range[1]} / location {location}"
        )

    # Use snapped partition boundaries in SQL — raw input dates won't match stored
    # week/month column values (e.g. input "2024-11-07" vs stored "2024-11-04").
    sql = f"""
        SELECT w.types, SUM(w.counts) AS counts
        FROM read_parquet(?) w
        LEFT JOIN read_parquet(?) a ON w.geo = a.local_id
        WHERE w.{time_column} BETWEEN ? AND ?
          AND a.entity_id = ?
        GROUP BY w.types
        ORDER BY counts DESC
        LIMIT ?
    """
    rows = conn.execute(sql, [filtered_path, adapter_path,
                               partition_starts[0], partition_starts[-1], location, limit]).fetchall()

    types = [r[0] for r in rows]
    counts = [float(r[1]) for r in rows]
    return {"types": types, "counts": counts}


@router.get("/allotax")
async def allotax_endpoint(
    # System 1
    dates: str = Query(..., description="Date range for system 1, e.g. '2024-01-01,2024-01-31'"),
    location: str = Query(..., description="Location entity ID for system 1, e.g. 'wikidata:Q30'"),
    # System 2
    dates2: str = Query(..., description="Date range for system 2, e.g. '2024-02-01,2024-02-28'"),
    location2: str = Query(..., description="Location entity ID for system 2, e.g. 'wikidata:Q16'"),
    # Dataset
    domain: str = Query("wikimedia", description="Domain owning the dataset, e.g. 'wikimedia'"),
    dataset: str = Query("ngrams", description="Dataset ID within the domain, e.g. 'ngrams'"),
    granularity: str = Query("daily", description="Partition granularity: daily, weekly, monthly"),
    # Allotax params
    alpha: float = Query(1.0, description="RTD alpha parameter"),
    alphas: Optional[str] = Query(None, description="Comma-separated alphas for multi-alpha mode, e.g. '0.5,1.0,2.0,3.0'"),
    # Response shaping
    ngram_limit: int = Query(10000, description="Max ngrams to load per system before computing"),
    wordshift_limit: int = Query(200, description="Truncate wordshift output to top N entries"),
    db: AsyncSession = Depends(get_db_session),
):
    """Compute allotaxonometer (rank-turbulence divergence) between two ngram distributions.

    Loads raw ngrams server-side from the specified datalake, runs the full allotax
    pipeline in Rust via PyO3, and returns lean visualization data (~30-50KB).

    Response shape (single alpha):
      normalization, diamond_counts, max_delta_loss, wordshift, balance, alpha, meta

    Response shape (multi-alpha via `alphas`):
      balance, alpha_results[{alpha, normalization, diamond_counts, max_delta_loss, wordshift}], meta

    Alpha slider pattern — precompute a discrete set of alphas in one call:
      /allotax?alphas=0.33,0.5,1.0,2.0,3.0&...
      Then use adaptMultiAlphaResult() from allotaxonometer-ui to drive the slider client-side.
    """
    if granularity not in ("daily", "weekly", "monthly"):
        raise HTTPException(status_code=400, detail="granularity must be daily, weekly, or monthly")

    granularity_map = {
        "daily": ("wikigrams", "date"),
        "weekly": ("wikigrams_weekly", "week"),
        "monthly": ("wikigrams_monthly", "month"),
    }
    table_name, time_column = granularity_map[granularity]

    def parse_range(s: str) -> List[str]:
        parts = s.split(",")
        return [parts[0], parts[0]] if len(parts) == 1 else [parts[0], parts[1]]

    dr1 = parse_range(dates)
    dr2 = parse_range(dates2)

    # Look up dataset
    result = await db.execute(
        select(Dataset).where(Dataset.domain == domain, Dataset.dataset_id == dataset)
    )
    datalake = result.scalar_one_or_none()
    if not datalake:
        raise HTTPException(status_code=404, detail=f"Dataset '{domain}/{dataset}' not found")

    if not datalake.tables_metadata or table_name not in datalake.tables_metadata:
        available = list(datalake.tables_metadata.keys()) if datalake.tables_metadata else []
        raise HTTPException(
            status_code=400,
            detail=f"Table '{table_name}' not available. Found: {available}"
        )

    try:
        import allotax
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="allotax module not available. Install via: cd allotaxonometer-core/crates/allotax-py && maturin develop --release"
        )

    try:
        duckdb_client = get_duckdb_client()
        conn = duckdb_client.connect()

        sys1 = _load_ngrams(conn, datalake, table_name, time_column, dr1, location, ngram_limit)
        sys2 = _load_ngrams(conn, datalake, table_name, time_column, dr2, location2, ngram_limit)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data loading failed: {str(e)}")

    # Compute allotax — package returns lean display data natively
    try:
        if alphas:
            alpha_list = [float(a) for a in alphas.split(",")]
            result_data = allotax.compute_allotax_multi_alpha(sys1, sys2, alpha_list, wordshift_limit)
        else:
            result_data = allotax.compute_allotax(sys1, sys2, alpha, wordshift_limit)


        return {
            **result_data,
            "meta": {
                "system1": {"dates": dates, "location": location, "ngrams": len(sys1["types"])},
                "system2": {"dates": dates2, "location": location2, "ngrams": len(sys2["types"])},
                "domain": domain,
                "dataset": dataset,
                "granularity": granularity,
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Allotax computation failed: {str(e)}")
