"""
Storywrangler API — instruments from the Vermont Complex Systems Institute.

Currently includes:
  - Allotaxonometer: rank-turbulence divergence between two ngram distributions.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from urllib.parse import quote

from ..core.database import get_db_session
from ..core.duckdb_client import get_duckdb_client
from ..core.query_utils import load_system, resolve_entity

from ..models.registry import Dataset, EntityMapping

router = APIRouter()


def _load_ngrams(conn, dataset_obj, granularity: str, time_column: str,
                 date_range: List[str], encoded_country: str, limit: int) -> dict:
    """Load top ngrams for one (date_range, location) system from a dataset.

    encoded_country is the URL-encoded local_id resolved from entity_id before calling.
    Returns a dict with "types" and "counts" lists ready for allotax input.
    """

    glob_path = f"{dataset_obj.data_location}/{granularity}/country={encoded_country}/{time_column}=*/data_0.parquet"

    sql = f"""
        SELECT ngram, SUM(pv_count) AS counts
        FROM read_parquet('{glob_path}')
        WHERE {time_column} BETWEEN ? AND ?
        GROUP BY ngram
        ORDER BY counts DESC
        LIMIT ?
    """
    rows = conn.execute(sql, [date_range[0], date_range[1], limit]).fetchall()

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

    Loads raw ngrams server-side from the specified dataset, runs the full allotax
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

    time_column = {"daily": "date", "weekly": "week", "monthly": "month"}[granularity]

    def parse_range(s: str) -> List[str]:
        parts = s.split(",")
        return [parts[0], parts[0]] if len(parts) == 1 else [parts[0], parts[1]]

    dr1 = parse_range(dates)
    dr2 = parse_range(dates2)

    # Look up dataset
    result = await db.execute(
        select(Dataset).where(Dataset.domain == domain, Dataset.dataset_id == dataset)
    )
    dataset_obj = result.scalar_one_or_none()
    if not dataset_obj:
        raise HTTPException(status_code=404, detail=f"Dataset '{domain}/{dataset}' not found")

    try:
        import allotax
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="allotax module not available. Install via: cd allotaxonometer-core/crates/allotax-py && maturin develop --release"
        )

    # Resolve entity_ids → encoded local_ids via DB before entering sync DuckDB code
    async def resolve_location(loc: str) -> str:
        em_result = await db.execute(
            select(EntityMapping).where(
                EntityMapping.domain == domain,
                EntityMapping.dataset_id == dataset,
                EntityMapping.entity_id == loc,
            )
        )
        em = em_result.scalar_one_or_none()
        if not em:
            raise HTTPException(status_code=400, detail=f"Location '{loc}' not found in entity mappings")
        return quote(em.local_id, safe='')

    encoded1 = await resolve_location(location)
    encoded2 = await resolve_location(location2)

    try:
        duckdb_client = get_duckdb_client()
        conn = duckdb_client.connect()

        sys1 = _load_ngrams(conn, dataset_obj, granularity, time_column, dr1, encoded1, ngram_limit)
        sys2 = _load_ngrams(conn, dataset_obj, granularity, time_column, dr2, encoded2, ngram_limit)

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


# ── allotax2 — generic, registry-driven ──────────────────────────────────────


@router.get("/allotax2")
async def allotax2_endpoint(
    request: Request,
    domain: str = Query(..., description="Domain owning the dataset, e.g. 'wikimedia'"),
    dataset: str = Query(..., description="Dataset ID within the domain, e.g. 'ngrams'"),
    entity: Optional[str] = Query(None, description="Global entity ID for system 1, e.g. 'wikidata:Q30'"),
    entity2: Optional[str] = Query(None, description="Global entity ID for system 2, e.g. 'wikidata:Q16'"),
    dates: Optional[str] = Query(None, description="Date/year range for system 1. Single value '2020' or range '2020,2023'"),
    dates2: Optional[str] = Query(None, description="Date/year range for system 2"),
    granularity: Optional[str] = Query(None, description="Hive granularity (parquet_hive only): daily | weekly | monthly"),
    alpha: float = Query(1.0, description="RTD alpha parameter"),
    alphas: Optional[str] = Query(None, description="Comma-separated alphas for multi-alpha mode, e.g. '0.5,1.0,2.0'"),
    ngram_limit: int = Query(10000, description="Max types to load per system before computing"),
    wordshift_limit: int = Query(200, description="Truncate wordshift output to top N entries"),
    db: AsyncSession = Depends(get_db_session),
):
    """Generic allotaxonometer endpoint — works for any registered types-counts dataset.

    Driven entirely by the dataset's registered endpoint_schema and entity_mapping.
    Intended to replace /allotax (wikimedia-specific) and /allotax/compare (WIP).

    Comparison axes — any two systems differing on at least one dimension:
      entity vs entity     ?entity=wikidata:Q30&entity2=wikidata:Q16
      time vs time         ?entity=wikidata:Q30&dates=2020&dates2=2010
      filter vs filter     ?entity=wikidata:Q30&sex=M&sex2=F   (babynames)
      entity x time        ?entity=wikidata:Q30&dates=2024-01&entity2=wikidata:Q16&dates2=2023-01

    For parquet_hive datasets (e.g. ngrams), granularity is required:
      &granularity=daily

    Filter dimensions (e.g. sex) are declared in endpoint_schema.filter_dimensions
    and passed as extra query params: ?sex=M&sex2=F
    """
    # ── Load and validate dataset ──────────────────────────────
    result = await db.execute(
        select(Dataset).where(Dataset.domain == domain, Dataset.dataset_id == dataset)
    )
    dataset_obj = result.scalar_one_or_none()
    if not dataset_obj:
        raise HTTPException(status_code=404, detail=f"Dataset '{domain}/{dataset}' not found")

    ep = dataset_obj.endpoint_schema
    if not ep or ep.get("type") != "types-counts":
        raise HTTPException(
            status_code=400,
            detail="Dataset does not support the types-counts endpoint. Register with endpoint_schema.type='types-counts'.",
        )

    # Validate granularity for hive-partitioned datasets
    if dataset_obj.data_format == "parquet_hive":
        granularities = ep.get("granularities", {})
        if not granularity:
            raise HTTPException(
                status_code=400,
                detail=f"granularity is required for parquet_hive datasets. Options: {sorted(granularities)}",
            )
        if granularity not in granularities:
            raise HTTPException(
                status_code=400,
                detail=f"granularity must be one of {sorted(granularities)}",
            )

    # ── Extract filter dimensions from request params ──────────
    filter_dims = ep.get("filter_dimensions") or []
    qp = request.query_params
    filter_vals1 = {dim: qp[dim]       for dim in filter_dims if dim in qp}
    filter_vals2 = {dim: qp[f"{dim}2"] for dim in filter_dims if f"{dim}2" in qp}

    def parse_dates(s: str) -> List[str]:
        parts = s.split(",")
        return [parts[0], parts[0]] if len(parts) == 1 else [parts[0], parts[1]]

    dr1 = parse_dates(dates)  if dates  else None
    dr2 = parse_dates(dates2) if dates2 else None

    # ── Resolve global entity IDs → local IDs (async, before DuckDB) ──
    local_id1 = (await resolve_entity(db, domain, dataset, entity)).local_id  if entity  else None
    local_id2 = (await resolve_entity(db, domain, dataset, entity2)).local_id if entity2 else None

    # ── Allotax ────────────────────────────────────────────────
    try:
        import allotax
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="allotax module not available. Install via: cd allotaxonometer-core/crates/allotax-py && maturin develop --release",
        )

    try:
        conn = get_duckdb_client().connect()
        sys1 = load_system(conn, dataset_obj, local_id1, dr1, filter_vals1, granularity, ngram_limit)
        sys2 = load_system(conn, dataset_obj, local_id2, dr2, filter_vals2, granularity, ngram_limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data loading failed: {str(e)}")

    try:
        if alphas:
            alpha_list = [float(a) for a in alphas.split(",")]
            result_data = allotax.compute_allotax_multi_alpha(sys1, sys2, alpha_list, wordshift_limit)
        else:
            result_data = allotax.compute_allotax(sys1, sys2, alpha, wordshift_limit)

        return {
            **result_data,
            "meta": {
                "system1": {"entity": entity, "dates": dates, "filters": filter_vals1, "types": len(sys1["types"])},
                "system2": {"entity": entity2, "dates": dates2, "filters": filter_vals2, "types": len(sys2["types"])},
                "domain": domain,
                "dataset": dataset,
                "granularity": granularity,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Allotax computation failed: {str(e)}")
