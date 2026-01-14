"""
Datalakes API endpoints for querying registered ducklakes/datalakes.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
import httpx
from ..core.database import get_db_session
from ..core.duckdb_client import get_duckdb_client
from ..models.datalakes import Datalake, EntityMapping
from ..routers.auth import get_admin_user
from ..models.auth import User

router = APIRouter()
admin_router = APIRouter()


class EntityMappingConfig(BaseModel):
    """Configuration for entity mapping table"""
    table: str = Field(..., description="Name of the adapter table containing entity mappings")
    local_id_column: str = Field(..., description="Column name for local identifiers")
    entity_id_column: str = Field(..., description="Column name for standardized entity identifiers")


class DatalakeCreate(BaseModel):
    dataset_id: str
    data_location: str
    data_format: str = "ducklake"
    description: Optional[str] = None
    tables_metadata: Optional[Dict] = None
    ducklake_data_path: Optional[str] = None
    schema: Optional[Dict[str, str]] = None  # Column name -> type mapping
    entity_mapping: Optional[EntityMappingConfig] = None
    sources: Optional[Dict[str, Dict[str, Union[str, List[str]]]]] = None


@router.get("/")
async def list_datalakes(db: AsyncSession = Depends(get_db_session)):
    """List all registered datalakes."""
    query = select(Datalake).order_by(Datalake.dataset_id)
    result = await db.execute(query)
    datalakes = result.scalars().all()

    return {
        "datalakes": [
            {
                "dataset_id": dl.dataset_id,
                "data_location": dl.data_location,
                "data_format": dl.data_format,
                "description": dl.description,
                "created_at": dl.created_at,
                "updated_at": dl.updated_at
            }
            for dl in datalakes
        ],
        "total": len(datalakes)
    }


@admin_router.post("/")
async def register_datalake(
    datalake: DatalakeCreate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Register a new datalake or update existing one."""
    # Check if dataset_id already exists
    existing_result = await db.execute(
        select(Datalake).where(Datalake.dataset_id == datalake.dataset_id)
    )
    existing_datalake = existing_result.scalar_one_or_none()

    if existing_datalake:
        # Update existing datalake
        existing_datalake.data_location = datalake.data_location
        existing_datalake.data_format = datalake.data_format
        existing_datalake.description = datalake.description
        existing_datalake.tables_metadata = datalake.tables_metadata
        existing_datalake.ducklake_data_path = datalake.ducklake_data_path
        existing_datalake.schema = datalake.schema
        existing_datalake.entity_mapping = datalake.entity_mapping.model_dump() if datalake.entity_mapping else None
        existing_datalake.sources = datalake.sources

        await db.commit()
        await db.refresh(existing_datalake)

        return {
            "message": f"Datalake '{datalake.dataset_id}' updated successfully"
        }
    else:
        # Create new datalake entry
        datalake_data = datalake.model_dump()

        # Convert Pydantic models to dicts for JSON storage
        if datalake_data.get('entity_mapping'):
            datalake_data['entity_mapping'] = datalake_data['entity_mapping']
        if datalake_data.get('dimensions'):
            datalake_data['dimensions'] = datalake_data['dimensions']

        db_datalake = Datalake(**datalake_data)
        db.add(db_datalake)
        await db.commit()
        await db.refresh(db_datalake)

        return {
            "message": f"Datalake '{datalake.dataset_id}' registered successfully",
            "datalake": {
                "dataset_id": db_datalake.dataset_id,
                "data_location": db_datalake.data_location,
                "data_format": db_datalake.data_format,
                "description": db_datalake.description,
                "schema": db_datalake.schema,
                "ducklake_data_path": db_datalake.ducklake_data_path
            }
        }


@router.get("/{dataset_id}")
async def get_datalake_info(
    dataset_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get metadata for a specific datalake."""

    # Look up datalake in registry
    query = select(Datalake).where(Datalake.dataset_id == dataset_id)
    result = await db.execute(query)
    datalake = result.scalar_one_or_none()

    if not datalake:
        raise HTTPException(
            status_code=404,
            detail=f"Datalake '{dataset_id}' not found"
        )

    # Return all stored metadata
    return {
        "dataset_id": datalake.dataset_id,
        "data_location": datalake.data_location,
        "data_format": datalake.data_format,
        "description": datalake.description,
        "tables_metadata": datalake.tables_metadata,
        "ducklake_data_path": datalake.ducklake_data_path,
        "schema": datalake.schema,
        "entity_mapping": datalake.entity_mapping,
        "sources": datalake.sources,
        "created_at": datalake.created_at,
        "updated_at": datalake.updated_at
    }

@router.get("/{dataset_id}/adapter")
async def get_adapter_info(
    dataset_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get metadata for a specific datalake."""

    # Look up datalake in registry
    query = select(Datalake).where(Datalake.dataset_id == dataset_id)
    result = await db.execute(query)
    datalake = result.scalar_one_or_none()

    if not datalake:
        raise HTTPException(
            status_code=404,
            detail=f"Datalake '{dataset_id}' not found"
        )

    try:
        # Get DuckDB connection
        duckdb_client = get_duckdb_client()
        conn = duckdb_client.connect()

        print(datalake)
        # Use stored metadata to get exact file paths for current versions
        if not datalake.tables_metadata:
            raise HTTPException(
                status_code=500,
                detail="Datalake metadata is missing. Please re-register the datalake with proper tables_metadata."
            )
        
        adapter_fnames = datalake.tables_metadata.get("adapter")

        if not adapter_fnames:
            raise HTTPException(
                status_code=500,
                detail="Missing babynames or adapter file paths. Required: tables_metadata.babynames and tables_metadata.adapter"
            )

        adapter_path = [
            f"{datalake.data_location}/{datalake.ducklake_data_path}/main/adapter/{fname}" for fname in adapter_fnames
            ]

        # Execute comparative queries
        results = {}

        # Query for each combination of date ranges and locations
        
        sql_query = f"""
            SELECT
                *
            FROM read_parquet(?)
        """

        cursor = conn.execute(sql_query, [adapter_path])
        query_results = cursor.fetchall()

        print(f"🔍 Final results object: {query_results}")
        return query_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")
    finally:
        try:
            duckdb_client.close()
        except:
            pass

@router.get("/babynames/top-ngrams")
async def get_babynames_top_ngrams(
    dates: str = Query(default="1991,1993"),  # First date range
    dates2: Optional[str] = Query(default=None),  # Optional second date range
    locations: str = Query(default="wikidata:Q30"),  # Single location
    sex: Optional[str] = 'M',
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """Get top baby names with flexible comparative analysis.

    Supports:
    - Single date range: dates=["1950,1952"]
    - Dual date ranges: dates=["1950,1952", "1991,1993"] (requires single location)
    - Single location: locations=["wikidata:Q30"]
    - Multiple locations: locations=["wikidata:Q30", "wikidata:Q16"] (requires single date range)

    Examples:
    - Temporal comparison: dates=["1950,1952", "1991,1993"]&locations=["wikidata:Q30"]
    - Geographic comparison: dates=["1950,1952"]&locations=["wikidata:Q30", "wikidata:Q16"]
    - Simple query: dates=["1950,1952"]&locations=["wikidata:Q30"]

    Returns structured data for comparison visualization.
    """

    # Parse dates parameters
    # dates="1991,1993"
    date_ranges = []

    # Parse first date range
    years1 = [int(y) for y in dates.split(',')]
    if len(years1) == 1:
        years1.append(years1[0])  # Single year becomes range [year, year]
    date_ranges.append(years1)

    # Parse optional second date range
    if dates2:
        years2 = [int(y) for y in dates2.split(',')]
        if len(years2) == 1:
            years2.append(years2[0])  # Single year becomes range [year, year]
        date_ranges.append(years2)

    # Single location (no longer a list)
    # locations="wikidata:Q176"
    location_list = [locations]

    # Look up babynames datalake
    query = select(Datalake).where(Datalake.dataset_id == "babynames")
    result = await db.execute(query)
    datalake = result.scalar_one_or_none()

    if not datalake:
        raise HTTPException(status_code=404, detail="Babynames datalake not found")

    try:
        # Get DuckDB connection
        duckdb_client = get_duckdb_client()
        conn = duckdb_client.connect()

        print(datalake)
        # Use stored metadata to get exact file paths for current versions
        if not datalake.tables_metadata:
            raise HTTPException(
                status_code=500,
                detail="Datalake metadata is missing. Please re-register the datalake with proper tables_metadata."
            )
        
        # babynames_fnames=["ducklake-019af69d-b42c-7877-9073-3f440e2ee162.parquet", "ducklake-019af69d-d7d5-7c8d-b38e-6ef9eca5d606.parquet"]
        babynames_fnames = datalake.tables_metadata.get("babynames")

        adapter_fnames = datalake.tables_metadata.get("adapter")

        if not babynames_fnames or not adapter_fnames:
            raise HTTPException(
                status_code=500,
                detail="Missing babynames or adapter file paths. Required: tables_metadata.babynames and tables_metadata.adapter"
            )

        # Construct full paths by combining data_location with the filenames
        # For ducklake format, files are stored in metadata.ducklake.files/main/ subdirectories
        # babynames_path="/users/j/s/jstonge1/babynames/metadata.ducklake.files/main/babynames/*parquet"
        babynames_path = [
            f"{datalake.data_location}/{datalake.ducklake_data_path}/main/babynames/{fname}" for fname in babynames_fnames
            ]
        # adapter_path= "/users/j/s/jstonge1/babynames/metadata.ducklake.files/main/adapter/*parquet"
        adapter_path = [
            f"{datalake.data_location}/{datalake.ducklake_data_path}/main/adapter/{fname}" for fname in adapter_fnames
            ]

        # Execute comparative queries
        results = {}

        # Query for each combination of date ranges and locations
        for i, date_range in enumerate(date_ranges):
            for j, location in enumerate(location_list):
                # Create key for result structure
                if len(date_ranges) > 1:
                    # Temporal comparison: use readable date format
                    if date_range[0] == date_range[1]:
                        key = str(date_range[0])  # Single year: "1990"
                    else:
                        key = f"{date_range[0]}-{date_range[1]}"  # Range: "2010-2015"
                elif len(location_list) > 1:
                    # Geographic comparison: use location ID
                    key = location.replace(":", "_").replace("-", "_")
                else:
                    key = "data"  # Single query, return simple format
                
                sql_query = f"""
                    SELECT
                        b.types,
                        SUM(b.counts) as counts
                    FROM read_parquet(?) b
                    LEFT JOIN read_parquet(?) a ON b.geo = a.local_id
                    WHERE b.year BETWEEN ? AND ?
                      AND a.entity_id = ?
                """

                if sex:
                    sql_query += " AND b.sex = ?"

                sql_query += f"""
                    GROUP BY b.types
                    ORDER BY counts DESC
                    LIMIT ?
                """

                print(babynames_path)
                cursor = conn.execute(sql_query, [babynames_path, adapter_path, date_range[0], date_range[1], location, sex, limit])
                query_results = cursor.fetchall()

    
                # Structure results for comparison or simple format
                try:
                    if key == "data":
                        # Simple single query - return flat array for backwards compatibility
                        formatted_results = []
                        for i, row in enumerate(query_results):
                            formatted_results.append({"types": row[0], "counts": row[1]})
                        return formatted_results
                    else:
                        # Comparative query - return array directly under the key
                        formatted_results = []
                        for i, row in enumerate(query_results):
                            formatted_results.append({"types": row[0], "counts": row[1]})
                        results[key] = formatted_results
                except Exception as format_error:
                    print(f"❌ Error formatting results: {format_error}")
                    print(f"❌ Raw query_results: {query_results}")
                    raise

        print(f"🔍 Final results object: {results}")
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")
    finally:
        try:
            duckdb_client.close()
        except:
            pass


@router.get("/{dataset_id}/validate-sources")
async def validate_datalake_sources(
    dataset_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Validate that all source URLs for a datalake are still accessible.

    Returns status for each source URL in the datalake's sources metadata.
    """
    # Look up datalake
    query = select(Datalake).where(Datalake.dataset_id == dataset_id)
    result = await db.execute(query)
    datalake = result.scalar_one_or_none()

    if not datalake:
        raise HTTPException(
            status_code=404,
            detail=f"Datalake '{dataset_id}' not found"
        )

    if not datalake.sources:
        return {
            "dataset_id": dataset_id,
            "message": "No sources configured for validation",
            "sources": {}
        }

    validation_results = {}

    # Iterate through dimensions and their sources
    for dimension, locations in datalake.sources.items():
        validation_results[dimension] = {}

        for location, urls in locations.items():
            # Handle both single URL (string) and multiple URLs (list)
            url_list = [urls] if isinstance(urls, str) else urls
            location_results = []

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
                for url in url_list:
                    method_used = "HEAD"
                    try:
                        # Try HEAD first (faster)
                        response = await client.head(url)

                        # If HEAD fails with 403/405, try GET with Range (some servers block HEAD for downloads)
                        if response.status_code in [403, 405]:
                            method_used = "GET"
                            response = await client.get(url, headers={"Range": "bytes=0-0"})

                        location_results.append({
                            "url": url,
                            "status": "accessible" if response.status_code < 400 else "error",
                            "status_code": response.status_code,
                            "method": method_used
                        })
                    except httpx.TimeoutException:
                        location_results.append({
                            "url": url,
                            "status": "timeout",
                            "error": "Request timed out after 10 seconds"
                        })
                    except httpx.RequestError as e:
                        location_results.append({
                            "url": url,
                            "status": "error",
                            "error": str(e)
                        })

            validation_results[dimension][location] = location_results

    # Calculate summary
    total_urls = sum(
        len(locations)
        for dimension_results in validation_results.values()
        for locations in dimension_results.values()
    )
    accessible_urls = sum(
        1
        for dimension_results in validation_results.values()
        for locations in dimension_results.values()
        for result in locations
        if result.get("status") == "accessible"
    )

    return {
        "dataset_id": dataset_id,
        "summary": {
            "total_urls": total_urls,
            "accessible": accessible_urls,
            "inaccessible": total_urls - accessible_urls,
            "all_accessible": accessible_urls == total_urls
        },
        "sources": validation_results
    }