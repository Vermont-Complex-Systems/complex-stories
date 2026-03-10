"""
Babynames API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from ..core.database import get_db_session
from ..core.duckdb_client import get_duckdb_client
from ..models.registry import Dataset

router = APIRouter()

BabynamesDataset = select(Dataset).where(Dataset.domain == "babynames")

@router.get("/top-ngrams")
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

    # Look up babynames dataset
    query = BabynamesDataset.where(Dataset.dataset_id == "babynames")
    result = await db.execute(query)
    dataset_obj = result.scalar_one_or_none()

    if not dataset_obj:
        raise HTTPException(status_code=404, detail="Babynames dataset not found")

    try:
        # Get DuckDB connection
        duckdb_client = get_duckdb_client()
        conn = duckdb_client.connect()

        # Use stored metadata to get exact file paths for current versions
        if not dataset_obj.tables_metadata:
            raise HTTPException(
                status_code=500,
                detail="Dataset metadata is missing. Please re-register the dataset with proper tables_metadata."
            )

        # babynames_fnames=["ducklake-019af69d-b42c-7877-9073-3f440e2ee162.parquet", ...]
        babynames_fnames = dataset_obj.tables_metadata.get("babynames")
        adapter_fnames = dataset_obj.tables_metadata.get("adapter")

        if not babynames_fnames or not adapter_fnames:
            raise HTTPException(
                status_code=500,
                detail="Missing babynames or adapter file paths. Required: tables_metadata.babynames and tables_metadata.adapter"
            )

        # Construct full paths by combining data_location with the filenames
        # For ducklake format, files are stored in metadata.ducklake.files/main/ subdirectories
        babynames_path = [
            f"{dataset_obj.data_location}/{dataset_obj.ducklake_data_path}/main/babynames/{fname}" for fname in babynames_fnames
        ]
        adapter_path = [
            f"{dataset_obj.data_location}/{dataset_obj.ducklake_data_path}/main/adapter/{fname}" for fname in adapter_fnames
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

                cursor = conn.execute(sql_query, [babynames_path, adapter_path, date_range[0], date_range[1], location, sex, limit])
                query_results = cursor.fetchall()

                # Structure results for comparison or simple format
                try:
                    if key == "data":
                        # Simple single query - return flat array for backwards compatibility
                        return [{"types": row[0], "counts": row[1]} for row in query_results]
                    else:
                        # Comparative query - return array directly under the key
                        results[key] = [{"types": row[0], "counts": row[1]} for row in query_results]
                except Exception as format_error:
                    print(f"❌ Error formatting results: {format_error}")
                    raise

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")
