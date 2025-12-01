"""
Datalakes API endpoints for querying registered ducklakes/datalakes.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from ..core.database import get_db_session
from ..core.duckdb_client import get_duckdb_client
from ..models.datalakes import Datalake, EntityMapping
from ..routers.auth import get_admin_user
from ..models.auth import User

router = APIRouter()
admin_router = APIRouter()


class DatalakeCreate(BaseModel):
    dataset_id: str
    data_location: str
    data_format: str = "ducklake"
    description: Optional[str] = None
    tables_metadata: Optional[Dict] = None


class EntityMappingCreate(BaseModel):
    dataset_id: str
    local_id: str
    entity_id: str
    entity_name: str
    entity_ids: List[str]


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
    """Register a new datalake."""

    # Check if dataset_id already exists
    existing = await db.execute(
        select(Datalake).where(Datalake.dataset_id == datalake.dataset_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Datalake with dataset_id '{datalake.dataset_id}' already exists"
        )

    # Create new datalake entry
    db_datalake = Datalake(**datalake.model_dump())
    db.add(db_datalake)
    await db.commit()
    await db.refresh(db_datalake)

    return {
        "message": f"Datalake '{datalake.dataset_id}' registered successfully",
        "datalake": {
            "dataset_id": db_datalake.dataset_id,
            "data_location": db_datalake.data_location,
            "data_format": db_datalake.data_format,
            "description": db_datalake.description
        }
    }


@router.get("/{dataset_id}")
async def get_datalake_info(
    dataset_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get information and available endpoints for a specific datalake."""

    # Look up datalake in registry
    query = select(Datalake).where(Datalake.dataset_id == dataset_id)
    result = await db.execute(query)
    datalake = result.scalar_one_or_none()

    if not datalake:
        raise HTTPException(
            status_code=404,
            detail=f"Datalake '{dataset_id}' not found"
        )

    # Get adapter table content for entity mappings using stored metadata
    adapter_mappings = []
    if datalake.tables_metadata and "adapter" in datalake.tables_metadata:
        try:
            duckdb_client = get_duckdb_client()
            conn = duckdb_client.connect()

            adapter_metadata = datalake.tables_metadata["adapter"]
            adapter_file_path = f"{datalake.data_location}/main/{adapter_metadata['path']}{adapter_metadata['file_path']}"

            adapter_result = conn.execute(f"SELECT * FROM read_parquet('{adapter_file_path}')").fetchall()

            for row in adapter_result:
                adapter_mappings.append({
                    "local_id": row[0],
                    "entity_id": row[1],
                    "entity_name": row[2],
                    "entity_ids": row[3]
                })
        except Exception as e:
            # If adapter table doesn't exist, that's okay
            pass
        finally:
            try:
                duckdb_client.close()
            except:
                pass

    return {
        "dataset_id": datalake.dataset_id,
        "data_location": datalake.data_location,
        "data_format": datalake.data_format,
        "description": datalake.description,
        "created_at": datalake.created_at,
        "updated_at": datalake.updated_at,
        "entity_mappings": adapter_mappings
    }


@router.get("/babynames/top-ngrams")
async def get_babynames_top_ngrams(
    dates: List[str] = Query(default=["1991,1993"]),  # ["1950,1952"] or ["1950,1952", "1991,1993"]
    locations: List[str] = Query(default=["wikidata:Q30"]),  # ["wikidata:Q30"] or ["wikidata:Q30", "wikidata:Q16"]
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

    # Parse dates parameter
    date_ranges = []
    for date_range_str in dates:
        years = [int(y) for y in date_range_str.split(',')]
        if len(years) == 1:
            years.append(years[0])  # Single year becomes range [year, year]
        date_ranges.append(years)

    # Parse locations parameter
    location_list = locations

    # Validation: if multiple date ranges, must have single location
    if len(date_ranges) > 1 and len(location_list) > 1:
        raise HTTPException(
            status_code=400,
            detail="Cannot specify multiple date ranges AND multiple locations. Choose one for comparison."
        )

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

        # Use stored metadata to get exact file paths for current versions
        babynames_metadata = datalake.tables_metadata.get("babynames", {})
        adapter_metadata = datalake.tables_metadata.get("adapter", {})

        babynames_path = f"{datalake.data_location}/main/{babynames_metadata['path']}{babynames_metadata['file_path']}"
        adapter_path = f"{datalake.data_location}/main/{adapter_metadata['path']}{adapter_metadata['file_path']}"

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
                    FROM read_parquet('{babynames_path}') b
                    LEFT JOIN read_parquet('{adapter_path}') a ON b.countries = a.local_id
                    WHERE b.year BETWEEN {date_range[0]} AND {date_range[1]}
                      AND a.entity_id = '{location}'
                """

                if sex:
                    sql_query += f" AND b.sex = '{sex}'"

                sql_query += f" GROUP BY b.types ORDER BY counts DESC LIMIT {limit}"

                cursor = conn.execute(sql_query)
                query_results = cursor.fetchall()

                # Structure results for comparison or simple format
                if key == "data":
                    # Simple single query - return flat array for backwards compatibility
                    return [{"types": row[0], "counts": row[1]} for row in query_results]
                else:
                    # Comparative query - return array directly under the key
                    results[key] = [{"types": row[0], "counts": row[1]} for row in query_results]

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")
    finally:
        try:
            duckdb_client.close()
        except:
            pass