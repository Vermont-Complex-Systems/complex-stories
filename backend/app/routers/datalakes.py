"""
Datalakes API endpoints for querying registered ducklakes/datalakes.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
import httpx
import time
from datetime import datetime, timedelta
from urllib.parse import unquote
from ..core.database import get_db_session
from ..core.duckdb_client import get_duckdb_client
from ..models.datalakes import Datalake, EntityMapping
from ..routers.auth import get_admin_user
from ..models.auth import User

router = APIRouter()
admin_router = APIRouter()


# Helper functions for top-ngrams endpoints
def get_parquet_paths(datalake, data_table_name: str):
    """Construct parquet file paths for data table and adapter table.

    The paths stored in tables_metadata are relative paths from the ducklake data directory.
    We prepend data_location to make them absolute.
    """
    if not datalake.tables_metadata:
        raise HTTPException(
            status_code=500,
            detail="Datalake metadata is missing. Please re-register the datalake with proper tables_metadata."
        )

    data_fnames = datalake.tables_metadata.get(data_table_name)
    adapter_fnames = datalake.tables_metadata.get("adapter")

    if not data_fnames or not adapter_fnames:
        raise HTTPException(
            status_code=500,
            detail=f"Missing {data_table_name} or adapter file paths. Required: tables_metadata.{data_table_name} and tables_metadata.adapter"
        )

    # Paths in tables_metadata are relative paths like "geo=US/date=2024-11-01/file.parquet"
    # We need to construct: {data_location}/main/{table_name}/{relative_path}
    # NOTE: Don't URL-decode - the filesystem actually has %20 in directory names
    data_path = [
        f"{datalake.data_location}/main/{data_table_name}/{fname}"
        for fname in data_fnames
    ]
    adapter_path = [
        f"{datalake.data_location}/main/adapter/{fname}"
        for fname in adapter_fnames
    ]

    return data_path, adapter_path

def format_results(query_results, key: str):
    """Format query results into structured response."""
    formatted_results = []
    for row in query_results:
        formatted_results.append({"types": row[0], "counts": row[1]})

    if key == "data":
        # Simple single query - return flat array
        return formatted_results, True  # True = early return
    else:
        # Comparative query - return under key
        return {key: formatted_results}, False  # False = continue aggregating

def compute_partition_starts(start_date: str, end_date: str, granularity: str) -> List[str]:
    """Compute partition start dates covering [start_date, end_date] using date arithmetic.

    Assumes no gaps in the data. For weekly/monthly granularities, snaps start_date
    back to the nearest partition boundary so that partial periods at the edges are included.

    Args:
        start_date: Start of the date range (YYYY-MM-DD). Should be a partition boundary
                    for top-ngrams queries; will be snapped for server-computed windows.
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
        # Snap back to the Monday of the week containing start_date
        current = start - timedelta(days=start.weekday())
    elif granularity == "monthly":
        # Snap back to the first of the month containing start_date
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
    data_schema: Optional[Dict[str, str]] = None  # Column name -> type mapping
    partitioning: Optional[Dict] = None  # Partitioning metadata
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
        existing_datalake.data_schema = datalake.data_schema
        existing_datalake.partitioning = datalake.partitioning
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
                "data_schema": db_datalake.data_schema,
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
        # "tables_metadata": datalake.tables_metadata,
        "ducklake_data_path": datalake.ducklake_data_path,
        "data_schema": datalake.data_schema,
        "partitioning": datalake.partitioning,
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
        for date_range in date_ranges:
            for location in location_list:
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
                        for row in query_results:
                            formatted_results.append({"types": row[0], "counts": row[1]})
                        return formatted_results
                    else:
                        # Comparative query - return array directly under the key
                        formatted_results = []
                        for row in query_results:
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

@router.get("/wikigrams/top-ngrams")
async def get_wikigrams_top_ngrams(
    dates: str = Query(default="2024-11-01,2024-11-07"),  # First date range
    dates2: Optional[str] = Query(default=None),  # Optional second date range
    locations: str = Query(default="wikidata:Q30"),  # Single location
    granularity: str = Query(default="daily"),  # Partition granularity: daily, weekly, monthly
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """Get top Wikipedia n-grams with flexible comparative analysis.

    Supports:
    - Single date range: dates="2024-01-01,2024-01-31"
    - Dual date ranges: dates="2024-01-01,2024-01-31"&dates2="2024-02-01,2024-02-28" (requires single location)
    - Single location: locations="wikidata:Q30"
    - Granularity selection: granularity="daily|weekly|monthly" (default: daily)

    Examples:
    - Temporal comparison: dates="2024-01-01,2024-01-31"&dates2="2024-02-01,2024-02-28"&locations="wikidata:Q30"
    - Simple query: dates="2024-01-01,2024-01-31"&locations="wikidata:Q30"
    - Weekly aggregation: dates="2024-01-01,2024-01-31"&granularity=weekly

    Returns structured data for comparison visualization with metadata about queried partitions.
    """

    # Validate granularity parameter
    if granularity not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="granularity must be one of: daily, weekly, monthly")

    # Parse dates parameters
    date_ranges = []

    # Parse first date range
    dates_str1 = dates.split(',')
    if len(dates_str1) == 1:
        dates_str1.append(dates_str1[0])  # Single date becomes range [date, date]
    date_ranges.append(dates_str1)

    # Parse optional second date range
    if dates2:
        dates_str2 = dates2.split(',')
        if len(dates_str2) == 1:
            dates_str2.append(dates_str2[0])  # Single date becomes range [date, date]
        date_ranges.append(dates_str2)

    # Single location (no longer a list)
    location_list = [locations]

    # Look up wikigrams datalake
    query = select(Datalake).where(Datalake.dataset_id == "wikigrams")
    result = await db.execute(query)
    datalake = result.scalar_one_or_none()

    if not datalake:
        raise HTTPException(status_code=404, detail="Wikigrams datalake not found")

    # Map granularity to table name and time column
    granularity_mapping = {
        "daily": ("wikigrams", "date"),
        "weekly": ("wikigrams_weekly", "week"),
        "monthly": ("wikigrams_monthly", "month")
    }
    table_name, time_column = granularity_mapping[granularity]

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

        # Check if requested granularity table exists
        if table_name not in datalake.tables_metadata:
            available = [k for k in datalake.tables_metadata.keys() if k.startswith("wikigrams")]
            raise HTTPException(
                status_code=400,
                detail=f"Table '{table_name}' not found. Available: {available}. Please re-register or use a different granularity."
            )

        # Get file paths using helper function
        wikigrams_path, adapter_path = get_parquet_paths(datalake, table_name)

        entity_to_geo = {
            "wikidata:Q30": "United%20States",
            "wikidata:Q145": "United%20Kingdom",
            "wikidata:Q16": "Canada",
            "wikidata:Q408": "Australia"
        }

        # Execute comparative queries
        results = {}
        queried_partitions_metadata = []

        # Query for each combination of date ranges and locations
        for date_range in date_ranges:
            for location in location_list:
                # Compute partition directories by stepping through the date range
                partition_starts = compute_partition_starts(date_range[0], date_range[1], granularity)

                # Filter paths to partition directories and geo
                local_geo = entity_to_geo.get(location)
                filtered_wikigrams_path = [
                    p for p in wikigrams_path
                    if any(f"{time_column}={ps}" in p for ps in partition_starts)
                    and (not local_geo or f"geo={local_geo}" in p)
                ]

                if not filtered_wikigrams_path:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No {granularity} data found for {date_range[0]} to {date_range[1]}"
                    )

                queried_partitions_metadata.append({
                    "date_range": date_range,
                    "partitions": partition_starts
                })

                # Create key for result structure
                if len(date_ranges) > 1:
                    # Temporal comparison: use readable date format
                    if date_range[0] == date_range[1]:
                        key = date_range[0]  # Single date: "2024-01-15"
                    else:
                        key = f"{date_range[0]}_{date_range[1]}"  # Range: "2024-01-01_2024-01-31"
                elif len(location_list) > 1:
                    # Geographic comparison: use location ID
                    key = location.replace(":", "_").replace("-", "_")
                else:
                    key = "data"  # Single query, return simple format

                sql_query = f"""
                    SELECT
                        w.types,
                        SUM(w.counts) as counts
                    FROM read_parquet(?) w
                    LEFT JOIN read_parquet(?) a ON w.geo = a.local_id
                    WHERE w.{time_column} BETWEEN ? AND ?
                      AND a.entity_id = ?
                    GROUP BY w.types
                    ORDER BY counts DESC
                    LIMIT ?
                """

                params = [filtered_wikigrams_path, adapter_path, date_range[0], date_range[1], location, limit]

                cursor = conn.execute(sql_query, params)
                query_results = cursor.fetchall()


                # Structure results for comparison or simple format
                try:
                    if key == "data":
                        # Simple single query - return with metadata
                        formatted_results = []
                        for row in query_results:
                            formatted_results.append({"types": row[0], "counts": row[1]})
                        return {
                            "data": formatted_results,
                            "metadata": {
                                "granularity": granularity,
                                "table_used": table_name,
                                "time_column": time_column,
                                "queried_partitions": overlapping_partitions
                            }
                        }
                    else:
                        # Comparative query - return array directly under the key
                        formatted_results = []
                        for row in query_results:
                            formatted_results.append({"types": row[0], "counts": row[1]})
                        results[key] = formatted_results
                except Exception as format_error:
                    print(f"❌ Error formatting results: {format_error}")
                    print(f"❌ Raw query_results: {query_results}")
                    raise

        # Add metadata for comparative queries
        return {
            **results,
            "metadata": {
                "granularity": granularity,
                "table_used": table_name,
                "time_column": time_column,
                "queries": queried_partitions_metadata
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")
    finally:
        try:
            duckdb_client.close()
        except:
            pass

@router.get("/search-term/{term}")
async def search_term(
    term: str,
    location: str = Query("wikidata:Q30", description="Location entity ID (e.g., wikidata:Q30 for United States)"),
    date: Optional[str] = Query(None, description="Optional date filter (YYYY-MM-DD)"),
    granularity: str = Query("daily", description="Granularity: daily, weekly, monthly"),
    window_days: int = Query(7, description="Days before/after the chosen date to include in spark plot data"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Search for a specific ngram term in the wikigrams datalake.

    Args:
        term: The ngram term to search for
        location: Location entity ID (default: wikidata:Q30 for United States)
        date: Optional date filter in YYYY-MM-DD format. If omitted, returns all dates.
        granularity: Partition granularity - daily, weekly, or monthly (default: daily)
        window_days: Days before/after the chosen date for spark plot rank data (default: 7)

    Returns:
        Dictionary containing termData, sparkData (rank over window), and query duration
    """
    if granularity not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="granularity must be one of: daily, weekly, monthly")

    if date:
        try:
            datetime.fromisoformat(date)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD: {e}")

    # Look up wikigrams datalake
    query = select(Datalake).where(Datalake.dataset_id == "wikigrams")
    result = await db.execute(query)
    datalake = result.scalar_one_or_none()

    if not datalake:
        raise HTTPException(status_code=404, detail="Wikigrams datalake not found")

    granularity_mapping = {
        "daily": ("wikigrams", "date"),
        "weekly": ("wikigrams_weekly", "week"),
        "monthly": ("wikigrams_monthly", "month")
    }
    table_name, time_column = granularity_mapping[granularity]

    try:
        duckdb_client = get_duckdb_client()
        conn = duckdb_client.connect()

        if not datalake.tables_metadata:
            raise HTTPException(status_code=500, detail="Datalake metadata is missing.")

        if table_name not in datalake.tables_metadata:
            available = [k for k in datalake.tables_metadata.keys() if k.startswith("wikigrams")]
            raise HTTPException(
                status_code=400,
                detail=f"Table '{table_name}' not found. Available: {available}."
            )

        wikigrams_path, adapter_path = get_parquet_paths(datalake, table_name)

        entity_to_geo = {
            "wikidata:Q30": "United%20States",
            "wikidata:Q145": "United%20Kingdom",
            "wikidata:Q16": "Canada",
            "wikidata:Q408": "Australia"
        }
        local_geo = entity_to_geo.get(location)
        if local_geo:
            wikigrams_path = [p for p in wikigrams_path if f"geo={local_geo}" in p]

        # When a date is given, compute the window partition directories arithmetically.
        # Use the wider window paths for both queries so we only open parquet files once.
        window_start = window_end = None
        if date:
            focus_date = datetime.fromisoformat(date)
            window_start = (focus_date - timedelta(days=window_days)).strftime("%Y-%m-%d")
            window_end = (focus_date + timedelta(days=window_days)).strftime("%Y-%m-%d")
            window_partitions = compute_partition_starts(window_start, window_end, granularity)
            query_paths = [
                p for p in wikigrams_path
                if any(f"{time_column}={ps}" in p for ps in window_partitions)
            ]
        else:
            query_paths = wikigrams_path

        if not query_paths:
            raise HTTPException(status_code=404, detail="No data files found for the given filters")

        start_time = time.time()

        # --- Main query: counts for the specific date (or all dates) ---
        sql_query = f"""
            SELECT
                w.types,
                w.{time_column},
                w.geo,
                SUM(w.counts) as counts
            FROM read_parquet(?) w
            LEFT JOIN read_parquet(?) a ON w.geo = a.local_id
            WHERE w.types = ?
              AND a.entity_id = ?
        """
        params = [query_paths, adapter_path, term, location]

        if date:
            sql_query += f" AND w.{time_column} = ?"
            params.append(date)

        sql_query += f" GROUP BY w.types, w.{time_column}, w.geo ORDER BY w.{time_column}"

        cursor = conn.execute(sql_query, params)
        query_results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        if not query_results:
            raise HTTPException(status_code=404, detail="Search term not found")

        term_data = [dict(zip(columns, row)) for row in query_results]

        # --- Spark query: rank of this term for each date in the window ---
        spark_data = []
        if date and window_start and window_end:
            spark_sql = f"""
                WITH daily_totals AS (
                    SELECT
                        w.types,
                        w.{time_column},
                        SUM(w.counts) AS counts
                    FROM read_parquet(?) w
                    LEFT JOIN read_parquet(?) a ON w.geo = a.local_id
                    WHERE a.entity_id = ?
                      AND w.{time_column} BETWEEN ? AND ?
                    GROUP BY w.types, w.{time_column}
                ),
                ranked AS (
                    SELECT
                        types,
                        {time_column},
                        counts,
                        RANK() OVER (PARTITION BY {time_column} ORDER BY counts DESC) AS rank
                    FROM daily_totals
                )
                SELECT {time_column}, rank, counts
                FROM ranked
                WHERE types = ?
                ORDER BY {time_column}
            """
            spark_params = [query_paths, adapter_path, location, window_start, window_end, term]
            spark_cursor = conn.execute(spark_sql, spark_params)
            spark_results = spark_cursor.fetchall()
            spark_cols = [desc[0] for desc in spark_cursor.description]
            spark_data = [dict(zip(spark_cols, row)) for row in spark_results]

        duration = (time.time() - start_time) * 1000
        print(f"searchTerm query took {duration:.2f}ms")

        return {
            "termData": term_data,
            "sparkData": spark_data,
            "duration": duration
        }

    except HTTPException:
        raise
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