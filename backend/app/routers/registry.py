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
from ..models.registry import Dataset, EntityMapping
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
    """Schema declaration for entity ID resolution. Stored in datasets.entity_mapping.

    Describes how a dataset-local column maps to canonical entity IDs (e.g. Wikidata QIDs).
    The actual mapping rows live in the entity_mappings table, submitted inline or via the
    batch upsert endpoint.
    """
    entity_type: str = Field(..., description="Entity identifier system (e.g. 'wikidata', 'orcid', 'ror')")
    local_id_column: str = Field(..., description="Column in the dataset holding the dataset-local identifier")


class EntityRow(BaseModel):
    local_id: str = Field(..., description="Dataset-local identifier (e.g. country code, author ID)")
    entity_id: str = Field(..., description="Canonical entity ID conforming to the entity_type format (e.g. 'wikidata:Q30')")
    entity_name: str = Field(..., description="Human-readable name for the entity")
    entity_ids: Optional[List[str]] = Field(None, description="Alternate identifiers (e.g. ['iso:US', 'local:babynames:united_states'])")


class FormatConfig(BaseModel):
    # parquet_hive + ducklake: adapter parquet path(s) live here, not in entity_mapping
    tables_metadata: Optional[Dict] = Field(None, description="Maps logical table names to lists of representative file paths. e.g. {\"events\": [\"date=2024-01-01/part.parquet\"]}")
    # ducklake
    ducklake_data_path: Optional[str] = Field(None, description="ducklake only. Path to the DuckLake catalog .duckdb file.")
    data_schema: Optional[Dict[str, str]] = Field(None, description="Column name → DuckDB type. e.g. {\"title\": \"VARCHAR\", \"views\": \"BIGINT\"}")
    # parquet_hive with physical partitioning (e.g. revisions partitioned by identifier)
    partitioning: Optional[Dict] = Field(None, description="Physical partition scheme. e.g. {\"partition_by\": \"identifier\"}. Use for datasets physically Hive-partitioned on disk.")
    # shared: what data exists per dimension (dates per country, years per geo, etc.)
    availability: Optional[Dict] = Field(None, description="Data availability/coverage metadata. e.g. ngrams: {\"daily\": {\"available\": {\"US\": {\"min\": ..., \"max\": ...}}}}, babynames: {\"yearly\": {\"available\": {...}}}")


class OwnershipConfig(BaseModel):
    owner_group: Optional[str] = Field(None, description="Lab or research group (e.g. 'compethicslab', 'vcsi').")
    contact: Optional[str] = Field(None, description="Email or GitHub handle of the current maintainer.")
    status: Optional[str] = Field("active", description="Lifecycle state: active | needs_successor | archived.")
    storage_risk: Optional[str] = Field(None, description="Durability signal: managed | institutional | cloud | personal.")


class LineageConfig(BaseModel):
    derived_from: Optional[List[str]] = Field(None, description="Upstream datasets as 'domain/dataset_id' references (e.g. ['wikimedia/ngrams']).")
    produced_by: Optional[str] = Field(None, description="Pipeline or script that generated this dataset (git SHA, script path, or Dagster asset key).")
    consumers: Optional[List[str]] = Field(None, description="Opt-in list of downstream users — stories, tools, or scripts that depend on this dataset.")


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
    format_config: Optional[FormatConfig] = Field(None, description="Storage-format-specific metadata. parquet_hive: tables_metadata + partitioning (physical) + availability (coverage). ducklake: ducklake_data_path + data_schema + availability.")
    entity_mapping: Optional[EntityMappingConfig] = Field(None, description="Schema declaration for entity ID resolution. Describes entity_type and local_id_column. Actual mapping rows submitted via 'entities'.")
    entities: Optional[List[EntityRow]] = Field(None, description="Entity mapping rows to upsert into the entity_mappings table. Each row maps a dataset-local ID to a canonical entity ID.")
    sources: Optional[Dict[str, Dict[str, Union[str, List[str]]]]] = Field(None, description="Source URLs for provenance/validation. e.g. {\"main\": {\"url\": \"https://...\"}}")
    endpoint_schema: Optional[Dict] = Field(None, description="Query contract for this dataset. Keys: type (required), time_dimension (non-hive), granularities (hive-partitioned), filter_dimensions, type_column (default 'types'), count_column (default 'counts'). e.g. {\"type\": \"types-counts\", \"type_column\": \"ngram\", \"count_column\": \"pv_count\", \"granularities\": {\"daily\": \"date\"}}")
    catalog: Optional[str] = Field("vcsi", description="Producing organisation or group. Defaults to 'vcsi'. Enables future 3-level namespace catalog.domain.dataset_id.")
    ownership: Optional[OwnershipConfig] = Field(None, description="Ownership and succession metadata.")
    lineage: Optional[LineageConfig] = Field(None, description="Lineage metadata: upstream datasets, producing pipeline, downstream consumers.")


async def _upsert_entities(
    db: AsyncSession,
    domain: str,
    dataset_id: str,
    entities: List[EntityRow],
) -> int:
    """Upsert entity mapping rows into entity_mappings table. Returns count upserted."""
    for entity in entities:
        row_id = f"{domain}:{dataset_id}:{entity.local_id}"
        existing_em = await db.get(EntityMapping, row_id)
        if existing_em:
            existing_em.entity_id = entity.entity_id
            existing_em.entity_name = entity.entity_name
            existing_em.entity_ids = entity.entity_ids
        else:
            db.add(EntityMapping(
                id=row_id,
                domain=domain,
                dataset_id=dataset_id,
                local_id=entity.local_id,
                entity_id=entity.entity_id,
                entity_name=entity.entity_name,
                entity_ids=entity.entity_ids,
            ))
    return len(entities)


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

    entities_count = 0
    if dataset.entities:
        entities_count = await _upsert_entities(db, dataset.domain, dataset.dataset_id, dataset.entities)

    if existing:
        existing.domain = dataset.domain
        existing.data_location = dataset.data_location
        existing.data_format = dataset.data_format
        existing.description = dataset.description
        existing.format_config = dataset.format_config.model_dump() if dataset.format_config else None
        existing.entity_mapping = dataset.entity_mapping.model_dump() if dataset.entity_mapping else None
        existing.sources = dataset.sources
        existing.endpoint_schema = dataset.endpoint_schema
        existing.catalog = dataset.catalog
        existing.ownership = dataset.ownership.model_dump() if dataset.ownership else None
        existing.lineage = dataset.lineage.model_dump() if dataset.lineage else None

        await db.commit()
        await db.refresh(existing)
        msg = {"message": f"Dataset '{dataset.dataset_id}' updated successfully"}
        if entities_count:
            msg["entities_upserted"] = entities_count
        return msg
    else:
        dataset_data = dataset.model_dump(exclude={"entities"})
        # Serialize nested Pydantic sub-models to dicts for JSON columns
        if dataset.format_config:
            dataset_data["format_config"] = dataset.format_config.model_dump()
        if dataset.entity_mapping:
            dataset_data["entity_mapping"] = dataset.entity_mapping.model_dump()
        if dataset.ownership:
            dataset_data["ownership"] = dataset.ownership.model_dump()
        if dataset.lineage:
            dataset_data["lineage"] = dataset.lineage.model_dump()

        db_dataset = Dataset(**dataset_data)
        db.add(db_dataset)
        await db.commit()
        await db.refresh(db_dataset)
        msg = {
            "message": f"Dataset '{dataset.dataset_id}' registered successfully",
            "dataset": {
                "dataset_id": db_dataset.dataset_id,
                "data_location": db_dataset.data_location,
                "data_format": db_dataset.data_format,
                "description": db_dataset.description,
                "format_config": db_dataset.format_config,
            }
        }
        if entities_count:
            msg["entities_upserted"] = entities_count
        return msg


@admin_router.post("/{domain}/{dataset_id}/entities")
async def upsert_dataset_entities(
    domain: str,
    dataset_id: str,
    entities: List[EntityRow],
    _current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Batch upsert entity mapping rows for a registered dataset.

    Accepts a list of {local_id, entity_id, entity_name, entity_ids?} objects.
    Idempotent — safe to re-run after data changes.
    """
    existing_result = await db.execute(
        select(Dataset).where(Dataset.domain == domain, Dataset.dataset_id == dataset_id)
    )
    if not existing_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Dataset '{domain}/{dataset_id}' not found")

    count = await _upsert_entities(db, domain, dataset_id, entities)
    await db.commit()
    return {"domain": domain, "dataset_id": dataset_id, "entities_upserted": count}


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
    full: bool = False,
    db: AsyncSession = Depends(get_db_session),
):
    """Get metadata for a specific registered dataset.

    Use ?full=true to include tables_metadata (file path lists) in format_config.
    """
    result = await db.execute(
        select(Dataset).where(Dataset.domain == domain, Dataset.dataset_id == dataset_id)
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail=f"Dataset '{domain}/{dataset_id}' not found")
    fc = ds.format_config or {}
    return {
        "domain": ds.domain,
        "dataset_id": ds.dataset_id,
        "data_location": ds.data_location,
        "data_format": ds.data_format,
        "description": ds.description,
        "format_config": fc if full else {k: v for k, v in fc.items() if k != "tables_metadata"},
        "entity_mapping": ds.entity_mapping,
        "sources": ds.sources,
        "endpoint_schema": ds.endpoint_schema,
        "created_at": ds.created_at,
        "updated_at": ds.updated_at,
    }


@router.get("/{domain}/{dataset_id}/adapter")
async def get_adapter_info(
    domain: str,
    dataset_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """List entity mapping rows for a dataset (entity_id ↔ local_id).

    Reads from the entity_mappings table. Populate via the batch entities endpoint
    or by including 'entities' in the registration payload.
    """
    existing_result = await db.execute(
        select(Dataset).where(Dataset.domain == domain, Dataset.dataset_id == dataset_id)
    )
    if not existing_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Dataset '{domain}/{dataset_id}' not found")

    result = await db.execute(
        select(EntityMapping).where(
            EntityMapping.domain == domain,
            EntityMapping.dataset_id == dataset_id,
        )
    )
    rows = result.scalars().all()
    return [
        {
            "local_id": r.local_id,
            "entity_id": r.entity_id,
            "entity_name": r.entity_name,
            "entity_ids": r.entity_ids,
        }
        for r in rows
    ]


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
