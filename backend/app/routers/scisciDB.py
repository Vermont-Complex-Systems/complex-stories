from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy import text
from typing import List, Optional
from ..core.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any

router = APIRouter()

# New field metrics endpoints
@router.post("/field-metrics/bulk")
async def upload_field_metrics(
    data: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db_session)
):
    """Bulk upload precomputed field metrics from export script."""
    try:
        # Simple approach: delete all existing data and insert new
        await db.execute(text("DELETE FROM field_metrics"))

        # Bulk insert new data
        await db.execute(
            text("INSERT INTO field_metrics (field, year, metric_type, count) VALUES (:field, :year, :metric_type, :count)"),
            data
        )

        await db.commit()

        return {"message": f"Uploaded {len(data)} field-metric records"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/field-metrics")
async def get_precomputed_field_metrics(
    start_year: int = Query(default=2000, ge=1900, le=2030),
    end_year: int = Query(default=2024, ge=1900, le=2030),
    fields: Optional[List[str]] = Query(default=None),
    metric_types: Optional[List[str]] = Query(default=None, description="Metric types: total, has_abstract, has_full_text"),
    db: AsyncSession = Depends(get_db_session)
) -> List[Dict[str, Any]]:
    """Get field metrics from precomputed table."""

    # Build dynamic query based on filters
    where_conditions = ["year >= :start_year", "year <= :end_year"]
    params = {"start_year": start_year, "end_year": end_year}

    if fields:
        where_conditions.append("field = ANY(:fields)")
        params["fields"] = fields

    if metric_types:
        where_conditions.append("metric_type = ANY(:metric_types)")
        params["metric_types"] = metric_types

    query = text(f"""
        SELECT field, year, metric_type, count
        FROM field_metrics
        WHERE {' AND '.join(where_conditions)}
        ORDER BY field, year DESC, metric_type
    """)

    result = await db.execute(query, params)
    rows = result.fetchall()

    return [{"field": r[0], "year": r[1], "metric_type": r[2], "count": r[3]} for r in rows]
