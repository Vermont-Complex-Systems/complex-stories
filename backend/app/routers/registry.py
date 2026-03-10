"""
Dataset registry endpoints — discover and inspect registered file-based datasets.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
import httpx

from ..core.database import get_db_session
from ..core.duckdb_client import get_duckdb_client
from ..models.registry import Dataset
from ..routers.auth import get_admin_user
from ..models.auth import User

router = APIRouter()
admin_router = APIRouter()

# Domains that have actual registered routers. Update when adding a new router to main.py.
VALID_DOMAINS = {
    "wikimedia",
    "storywrangler",
    "babynames",
    "datalakes",
    "open-academic-analytics",
    "scisciDB",
    "annotations",
}


class EntityMappingConfig(BaseModel):
    table: Optional[str] = Field(None, description="DuckLake table name (ducklake format only)")
    path: Optional[str] = Field(None, description="Absolute path to adapter parquet file (parquet_hive format only)")
    local_id_column: str = Field(..., description="Column name in the adapter that holds the dataset-local identifier")
    entity_id_column: str = Field(..., description="Column name in the adapter that holds the canonical entity ID (e.g. 'wikidata:Q30')")


class DatasetCreate(BaseModel):
    """Register a dataset backend so API endpoints can discover and query it.

    The platform supports three data formats:
    - parquet_hive: Hive-partitioned parquet tree on disk (most common for large tabular data)
    - duckdb: Plain DuckDB database file
    - ducklake: DuckLake catalog (versioned, schema-aware DuckDB extension)

    The (domain, dataset_id) pair must be unique. Use domain to group datasets by the
    router/service that owns them (e.g. 'wikimedia', 'storywrangler').
    """
    dataset_id: str = Field(..., description="Short identifier, unique within domain. e.g. 'ngrams', 'revisions', 'babynames'")
    domain: str = Field(..., description="Owning service or router. Groups related datasets. e.g. 'wikimedia', 'storywrangler', 'babynames'")
    data_location: str = Field(..., description="Absolute path to the root of the dataset on disk (parquet_hive/duckdb) or connection string (ducklake)")
    data_format: str = Field("parquet_hive", description="Storage format. One of: parquet_hive | duckdb | ducklake")
    description: Optional[str] = Field(None, description="Human-readable description of the dataset")
    tables_metadata: Optional[Dict] = Field(
        None,
        description=(
            "parquet_hive only. Maps logical table names to lists of representative file paths. "
            "Keys must match physical Hive partition directory names under data_location. "
            "Example: {\"events\": [\"date=2024-01-01/geo=Q30/part.parquet\"], \"adapter\": [\"adapter.parquet\"]}"
        )
    )
    ducklake_data_path: Optional[str] = Field(None, description="ducklake only. Path to the DuckLake catalog .duckdb file")
    data_schema: Optional[Dict[str, str]] = Field(None, description="ducklake only. Column name → DuckDB type, for query reference. e.g. {\"title\": \"VARCHAR\", \"views\": \"BIGINT\"}")
    partitioning: Optional[Dict] = Field(None, description="Partitioning scheme description. e.g. {\"keys\": [\"date\", \"geo\"], \"granularity\": \"daily\"}")
    entity_mapping: Optional[EntityMappingConfig] = Field(None, description="How to map canonical entity IDs (e.g. Wikidata QIDs) to dataset-local identifiers. Required for geo/entity filtering endpoints.")
    sources: Optional[Dict[str, Dict[str, Union[str, List[str]]]]] = Field(None, description="Source URLs for provenance/validation. e.g. {\"main\": {\"url\": \"https://...\"}}")
    endpoint_schemas: Optional[List[Dict]] = Field(None, description="Endpoint types this dataset supports. Each entry: {type, time_dimension?, entity_dimensions?, filter_dimensions?}. e.g. [{\"type\": \"types-counts\", \"time_dimension\": \"date\", \"entity_dimensions\": [\"country\"]}]")


@admin_router.post("/register")
async def register_dataset(
    dataset: DatasetCreate,
    _current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Register a new dataset or update an existing one."""
    if dataset.domain not in VALID_DOMAINS:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown domain '{dataset.domain}'. Valid domains: {sorted(VALID_DOMAINS)}"
        )

    existing_result = await db.execute(
        select(Dataset).where(Dataset.domain == dataset.domain, Dataset.dataset_id == dataset.dataset_id)
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        existing.domain = dataset.domain
        existing.data_location = dataset.data_location
        existing.data_format = dataset.data_format
        existing.description = dataset.description
        existing.tables_metadata = dataset.tables_metadata
        existing.ducklake_data_path = dataset.ducklake_data_path
        existing.data_schema = dataset.data_schema
        existing.partitioning = dataset.partitioning
        existing.entity_mapping = dataset.entity_mapping.model_dump() if dataset.entity_mapping else None
        existing.sources = dataset.sources
        existing.endpoint_schemas = dataset.endpoint_schemas

        await db.commit()
        await db.refresh(existing)
        return {"message": f"Dataset '{dataset.dataset_id}' updated successfully"}
    else:
        db_dataset = Dataset(**dataset.model_dump())
        db.add(db_dataset)
        await db.commit()
        await db.refresh(db_dataset)
        return {
            "message": f"Dataset '{dataset.dataset_id}' registered successfully",
            "dataset": {
                "dataset_id": db_dataset.dataset_id,
                "data_location": db_dataset.data_location,
                "data_format": db_dataset.data_format,
                "description": db_dataset.description,
                "data_schema": db_dataset.data_schema,
                "ducklake_data_path": db_dataset.ducklake_data_path
            }
        }


@router.get("/")
async def list_registered_datasets(db: AsyncSession = Depends(get_db_session)):
    """List all registered datasets."""
    query = select(Dataset).order_by(Dataset.domain, Dataset.dataset_id)
    result = await db.execute(query)
    datasets = result.scalars().all()
    return {
        "datasets": [
            {
                "domain": ds.domain,
                "dataset_id": ds.dataset_id,
                "data_location": ds.data_location,
                "data_format": ds.data_format,
                "description": ds.description,
                "created_at": ds.created_at,
                "updated_at": ds.updated_at,
            }
            for ds in datasets
        ],
        "total": len(datasets),
    }


@router.get("/{domain}/{dataset_id}")
async def get_dataset_info(
    domain: str,
    dataset_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get metadata for a specific registered dataset."""
    result = await db.execute(
        select(Dataset).where(Dataset.domain == domain, Dataset.dataset_id == dataset_id)
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail=f"Dataset '{domain}/{dataset_id}' not found")
    return {
        "domain": ds.domain,
        "dataset_id": ds.dataset_id,
        "data_location": ds.data_location,
        "data_format": ds.data_format,
        "description": ds.description,
        "ducklake_data_path": ds.ducklake_data_path,
        "data_schema": ds.data_schema,
        "partitioning": ds.partitioning,
        "entity_mapping": ds.entity_mapping,
        "sources": ds.sources,
        "endpoint_schemas": ds.endpoint_schemas,
        "created_at": ds.created_at,
        "updated_at": ds.updated_at,
    }


@router.get("/{domain}/{dataset_id}/adapter")
async def get_adapter_info(
    domain: str,
    dataset_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Read the adapter table for a dataset (entity_id ↔ local_id mapping)."""
    result = await db.execute(
        select(Dataset).where(Dataset.domain == domain, Dataset.dataset_id == dataset_id)
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail=f"Dataset '{domain}/{dataset_id}' not found")

    if not ds.tables_metadata:
        raise HTTPException(status_code=500, detail="Dataset metadata is missing.")

    if ds.data_format == "parquet_hive":
        if not ds.entity_mapping or not ds.entity_mapping.get("path"):
            raise HTTPException(status_code=500, detail="Missing entity_mapping.path for parquet_hive format.")
        adapter_path = [ds.entity_mapping["path"]]
    else:
        adapter_fnames = ds.tables_metadata.get("adapter")
        if not adapter_fnames:
            raise HTTPException(status_code=500, detail="Missing adapter file paths. Required: tables_metadata.adapter")
        base = f"{ds.data_location}/{ds.ducklake_data_path}" if ds.ducklake_data_path else ds.data_location
        adapter_path = [
            f"{base}/main/adapter/{fname}" for fname in adapter_fnames
        ]

    try:
        conn = get_duckdb_client().connect()
        rows = conn.execute("SELECT * FROM read_parquet(?)", [adapter_path]).fetchall()
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/{domain}/{dataset_id}/validate-sources")
async def validate_dataset_sources(
    domain: str,
    dataset_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Validate that all source URLs for a dataset are still accessible."""
    result = await db.execute(
        select(Dataset).where(Dataset.domain == domain, Dataset.dataset_id == dataset_id)
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail=f"Dataset '{domain}/{dataset_id}' not found")

    if not ds.sources:
        return {"domain": domain, "dataset_id": dataset_id, "message": "No sources configured", "sources": {}}

    validation_results: Dict[str, Any] = {}
    headers = {"User-Agent": "Mozilla/5.0"}

    for dimension, locations in ds.sources.items():
        validation_results[dimension] = {}
        for location, urls in locations.items():
            url_list = [urls] if isinstance(urls, str) else urls
            location_results = []
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
                for url in url_list:
                    method_used = "HEAD"
                    try:
                        response = await client.head(url)
                        if response.status_code in [403, 405]:
                            method_used = "GET"
                            response = await client.get(url, headers={"Range": "bytes=0-0"})
                        location_results.append({
                            "url": url,
                            "status": "accessible" if response.status_code < 400 else "error",
                            "status_code": response.status_code,
                            "method": method_used,
                        })
                    except httpx.TimeoutException:
                        location_results.append({"url": url, "status": "timeout", "error": "Request timed out after 10 seconds"})
                    except httpx.RequestError as e:
                        location_results.append({"url": url, "status": "error", "error": str(e)})
            validation_results[dimension][location] = location_results

    total_urls = sum(len(locs) for dim in validation_results.values() for locs in dim.values())
    accessible = sum(1 for dim in validation_results.values() for locs in dim.values() for r in locs if r.get("status") == "accessible")
    return {
        "domain": domain,
        "dataset_id": dataset_id,
        "summary": {"total_urls": total_urls, "accessible": accessible, "inaccessible": total_urls - accessible, "all_accessible": accessible == total_urls},
        "sources": validation_results,
    }
