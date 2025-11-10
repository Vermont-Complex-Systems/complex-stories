from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy import text
from typing import List, Optional
from ..core.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any

router = APIRouter()

# Unified metrics endpoints
@router.post("/metrics/bulk")
async def upload_metrics(
    data: List[Dict[str, Any]],
    group_by: str = Query(description="Group by: field or venue"),
    db: AsyncSession = Depends(get_db_session)
):
    """Bulk upload precomputed metrics from export script."""
    if group_by not in ["field", "venue"]:
        raise HTTPException(status_code=400, detail="group_by must be either 'field' or 'venue'")

    try:
        if group_by == "field":
            # Clear and insert field metrics
            await db.execute(text("DELETE FROM field_metrics"))
            await db.execute(
                text("INSERT INTO field_metrics (field, year, metric_type, count) VALUES (:field, :year, :metric_type, :count)"),
                data
            )
        elif group_by == "venue":
            # Clear and insert venue metrics
            await db.execute(text("DELETE FROM venue_metrics"))
            await db.execute(
                text("INSERT INTO venue_metrics (venue, year, metric_type, count) VALUES (:venue, :year, :metric_type, :count)"),
                data
            )

        await db.commit()

        return {"message": f"Uploaded {len(data)} {group_by}-metric records"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/metrics")
async def get_precomputed_metrics(
    start_year: int = Query(default=2000, ge=1900, le=2030),
    end_year: int = Query(default=2024, ge=1900, le=2030),
    fields: Optional[List[str]] = Query(default=None),
    venues: Optional[List[str]] = Query(default=None),
    metric_types: Optional[List[str]] = Query(default=None, description="Metric types: total, has_abstract, has_fulltext"),
    group_by: str = Query(default="field", description="Group by: field or venue"),
    db: AsyncSession = Depends(get_db_session)
) -> List[Dict[str, Any]]:
    """Get metrics from precomputed tables. Supports both field and venue groupings."""

    if group_by not in ["field", "venue"]:
        raise HTTPException(status_code=400, detail="group_by must be either 'field' or 'venue'")

    # Build dynamic query based on grouping
    where_conditions = ["year >= :start_year", "year <= :end_year"]
    params = {"start_year": start_year, "end_year": end_year}

    if group_by == "field":
        if fields:
            where_conditions.append("field = ANY(:fields)")
            params["fields"] = fields

        where_clause = ' AND '.join(where_conditions)
        if metric_types:
            where_clause += " AND metric_type = ANY(:metric_types)"
            params["metric_types"] = metric_types

        query = text(f"""
            SELECT field, year, metric_type, count
            FROM field_metrics
            WHERE {where_clause}
            ORDER BY field, year DESC, metric_type
        """)

        result = await db.execute(query, params)
        rows = result.fetchall()

        return [{"field": r[0], "year": r[1], "metric_type": r[2], "count": r[3]} for r in rows]

    elif group_by == "venue":
        if venues:
            where_conditions.append("venue = ANY(:venues)")
            params["venues"] = venues

        where_clause = ' AND '.join(where_conditions)
        if metric_types:
            where_clause += " AND metric_type = ANY(:metric_types)"
            params["metric_types"] = metric_types

        query = text(f"""
            SELECT venue, year, metric_type, count
            FROM venue_metrics
            WHERE {where_clause}
            ORDER BY venue, year DESC, metric_type
        """)

        result = await db.execute(query, params)
        rows = result.fetchall()

        return [{"venue": r[0], "year": r[1], "metric_type": r[2], "count": r[3]} for r in rows]
