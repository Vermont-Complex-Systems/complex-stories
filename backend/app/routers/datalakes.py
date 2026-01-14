"""
Datalakes API endpoints for querying registered ducklakes/datalakes.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
import httpx
import re
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

def parse_partition_values(file_paths: List[str], partition_key: str) -> List[str]:
    """Extract unique partition values from Hive-style file paths.

    Args:
        file_paths: List of Hive-partitioned paths like ["geo=US/week=2025-03-03/data.parquet"]
        partition_key: Partition key to extract (e.g., "week", "month", "date")

    Returns:
        Sorted list of unique partition values

    Example:
        >>> parse_partition_values(["geo=US/week=2025-03-03/data.parquet"], "week")
        ["2025-03-03"]
    """
    pattern = re.compile(f"{partition_key}=([^/]+)")
    values = set()
    for path in file_paths:
        match = pattern.search(path)
        if match:
            values.add(match.group(1))
    return sorted(values)

def filter_paths_by_partitions(
    file_paths: List[str],
    partition_values: List[str],
    partition_key: str
) -> List[str]:
    """Filter file paths to only include those matching the given partition values.

    Args:
        file_paths: List of Hive-partitioned file paths
        partition_values: List of partition values to keep (e.g., ["2024-11-01", "2024-11-02"])
        partition_key: Partition key to match (e.g., "date", "week", "month")

    Returns:
        Filtered list of file paths

    Example:
        >>> filter_paths_by_partitions(
        ...     ["geo=US/date=2024-11-01/data.parquet", "geo=US/date=2024-10-01/data.parquet"],
        ...     ["2024-11-01"],
        ...     "date"
        ... )
        ["geo=US/date=2024-11-01/data.parquet"]
    """
    filtered = []
    pattern = re.compile(f"{partition_key}=([^/]+)")

    for path in file_paths:
        match = pattern.search(path)
        if match and match.group(1) in partition_values:
            filtered.append(path)

    return filtered


def find_overlapping_partitions(
    user_start_date: str,
    user_end_date: str,
    partition_values: List[str],
    granularity: str
) -> List[str]:
    """Find partition values that overlap with user's date range.

    Args:
        user_start_date: Start date in ISO format (YYYY-MM-DD)
        user_end_date: End date in ISO format (YYYY-MM-DD)
        partition_values: Available partition values from parse_partition_values()
        granularity: One of "daily", "weekly", "monthly"

    Returns:
        List of partition values that overlap with the date range

    Example:
        >>> find_overlapping_partitions("2025-03-05", "2025-03-12",
        ...                            ["2025-03-03", "2025-03-10"], "weekly")
        ["2025-03-03", "2025-03-10"]
    """
    overlapping = []

    for partition_value in partition_values:
        if granularity == "daily":
            # Partition value is a date like "2025-03-05"
            if user_start_date <= partition_value <= user_end_date:
                overlapping.append(partition_value)

        elif granularity == "weekly":
            # Partition value is week start (Monday) like "2025-03-03"
            week_start = partition_value
            week_end = (datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
            # Include week if it overlaps: week_start <= user_end AND week_end >= user_start
            if week_start <= user_end_date and week_end >= user_start_date:
                overlapping.append(partition_value)

        elif granularity == "monthly":
            # Partition value is month start like "2025-03-01"
            month_start = partition_value
            # Calculate last day of month
            month_dt = datetime.strptime(month_start, "%Y-%m-%d")
            if month_dt.month == 12:
                next_month = month_dt.replace(year=month_dt.year + 1, month=1, day=1)
            else:
                next_month = month_dt.replace(month=month_dt.month + 1, day=1)
            month_end = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")
            # Include month if it overlaps
            if month_start <= user_end_date and month_end >= user_start_date:
                overlapping.append(partition_value)

    return overlapping


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
        # "tables_metadata": datalake.tables_metadata,
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

        # Parse available partition values from file paths
        available_partitions = parse_partition_values(
            datalake.tables_metadata[table_name],
            time_column
        )

        print(f"🔍 DEBUG: Available partitions ({len(available_partitions)} total): {available_partitions[:10] if len(available_partitions) > 10 else available_partitions}...")

        # Execute comparative queries
        results = {}
        queried_partitions_metadata = []

        # Query for each combination of date ranges and locations
        for i, date_range in enumerate(date_ranges):
            for j, location in enumerate(location_list):
                print(f"🔍 DEBUG: User requested date range: {date_range[0]} to {date_range[1]}")

                # Find partitions that overlap with this date range
                overlapping_partitions = find_overlapping_partitions(
                    date_range[0],
                    date_range[1],
                    available_partitions,
                    granularity
                )

                print(f"🔍 DEBUG: Overlapping partitions found: {overlapping_partitions}")

                if not overlapping_partitions:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No {granularity} data available for date range {date_range[0]} to {date_range[1]}"
                    )

                # Filter file paths to only include the overlapping partitions
                filtered_wikigrams_path = filter_paths_by_partitions(
                    wikigrams_path,
                    overlapping_partitions,
                    time_column
                )

                # Map entity_id to local geo name for file path filtering
                # This is a hardcoded mapping - ideally we'd query the adapter table
                entity_to_geo = {
                    "wikidata:Q30": "United%20States",
                    "wikidata:Q145": "United%20Kingdom",
                    "wikidata:Q16": "Canada",
                    "wikidata:Q408": "Australia"
                }

                local_geo = entity_to_geo.get(location)
                if local_geo:
                    # Further filter by geo partition
                    filtered_wikigrams_path = [
                        path for path in filtered_wikigrams_path
                        if f"geo={local_geo}" in path
                    ]
                    print(f"🔍 DEBUG: Filtered to {len(filtered_wikigrams_path)} files for geo={local_geo}")

                queried_partitions_metadata.append({
                    "date_range": date_range,
                    "partitions": overlapping_partitions
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

                # Build IN clause for partition filtering
                partition_placeholders = ",".join(["?" for _ in overlapping_partitions])

                sql_query = f"""
                    SELECT
                        w.types,
                        SUM(w.counts) as counts
                    FROM read_parquet(?) w
                    LEFT JOIN read_parquet(?) a ON w.geo = a.local_id
                    WHERE w.{time_column} IN ({partition_placeholders})
                      AND a.entity_id = ?
                    GROUP BY w.types
                    ORDER BY counts DESC
                    LIMIT ?
                """

                # Build parameter list: [filtered_wikigrams_path, adapter_path, ...partition_values, location, limit]
                params = [filtered_wikigrams_path, adapter_path] + overlapping_partitions + [location, limit]

                cursor = conn.execute(sql_query, params)
                query_results = cursor.fetchall()


                # Structure results for comparison or simple format
                try:
                    if key == "data":
                        # Simple single query - return with metadata
                        formatted_results = []
                        for i, row in enumerate(query_results):
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
                        for i, row in enumerate(query_results):
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