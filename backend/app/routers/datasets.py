from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pandas as pd
from typing import List, Dict, Any, Optional
import io
import json
from ..core.database import get_db_session
from ..core.duckdb_client import get_duckdb_client
from ..models.annotation_datasets import AcademicResearchGroups, AcademicResearchGroupCreate, GoogleScholarVenues
from ..routers.auth import get_admin_user, get_current_active_user
from ..models.auth import User

router = APIRouter()
admin_router = APIRouter()

def get_available_datasets() -> List[Dict[str, Any]]:
    """Get list of available datasets with metadata."""
    datasets = []

    # Academic research groups dataset (from database)
    datasets.append({
        "name": "academic-research-groups",
        "description": "Faculty research groups data from database",
        "format": "Dynamic (JSON/Parquet)",
        "source": "Database",
        "keywords": ["research", "groups", "faculty", "annotations"],
        "endpoints": {
            "json": "/datasets/academic-research-groups",
            "parquet": "/datasets/academic-research-groups?format=parquet"
        },
        "streamable": False
    })

    # Google Scholar venues dataset (overthinking-fos)
    datasets.append({
        "name": "google-scholar-venues",
        "description": "Google Scholar top venues by field with h5-index metrics",
        "format": "Dynamic (JSON/Parquet)",
        "source": "Database",
        "keywords": ["overthinking-fos", "venues", "google-scholar", "h5-index", "fields-of-study"],
        "endpoints": {
            "json": "/datasets/google-scholar-venues",
            "parquet": "/datasets/google-scholar-venues?format=parquet"
        }
    })

    # S2ORC arXiv full text dataset
    datasets.append({
        "name": "s2orc-arxiv",
        "description": "S2ORC full text and annotations for arXiv papers (~2.78M documents)",
        "format": "Streaming (NDJSON/CSV)",
        "source": "DuckLake (scisciDB)",
        "keywords": ["s2orc", "arxiv", "fulltext", "annotations", "bibliography"],
        "endpoints": {
            "stream": "/datasets/s2orc/arxiv/stream",
            "stream_by_year": "/datasets/s2orc/arxiv/stream?year=2023"
        },
        "auth_required": True,
        "note": "Requires JWT token in header: 'Authorization: Bearer <token>'"
    })

    return datasets

@router.get("/")
async def list_datasets():
    """List all available datasets with metadata."""
    datasets = get_available_datasets()
    return {
        "datasets": datasets,
        "total": len(datasets)
    }

# Label Studio functions removed - no longer needed

@admin_router.post("/academic-research-groups")
async def create_academic_research_group(
    group: AcademicResearchGroupCreate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new academic research group entry."""
    db_group = AcademicResearchGroups(**group.model_dump())
    db.add(db_group)
    await db.commit()
    await db.refresh(db_group)
    return db_group

@router.get("/academic-research-groups")
async def get_academic_research_groups_list(
    skip: int = 0,
    payroll_year: Optional[int] = None,
    format: str = "json",
    db: AsyncSession = Depends(get_db_session)
):
    """Get academic research groups data from database - return JSON or download parquet."""

    # Build query
    query = select(AcademicResearchGroups)

    if payroll_year:
        query = query.where(AcademicResearchGroups.payroll_year == payroll_year)

    query = query.offset(skip)

    # Execute query
    result = await db.execute(query)
    annotations = result.scalars().all()

    data = []
    for annotation in annotations:
        data.append({
            'id': annotation.id,
            'payroll_name': annotation.payroll_name,
            'payroll_year': annotation.payroll_year,
            'position': annotation.position,
            # 'oa_display_name': annotation.oa_display_name,
            # 'is_prof': annotation.is_prof,
            'perceived_as_male': annotation.perceived_as_male,
            'has_research_group': annotation.has_research_group,
            'group_size': annotation.group_size,
            'oa_uid': annotation.oa_uid,
            'first_pub_year': annotation.first_pub_year,
            'host_dept': annotation.host_dept,
            'group_url': annotation.group_url,
            'inst_ipeds_id': annotation.inst_ipeds_id,
            'college': annotation.college,
            'notes': annotation.notes,
            'last_updated': annotation.last_updated
        })
    
    if format.lower() == "parquet":
        # Convert to DataFrame for parquet export

        df = pd.DataFrame(data)

        # Convert to parquet and return as download
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False, engine="pyarrow")
        buffer.seek(0)
        parquet_bytes = buffer.read()

        return StreamingResponse(
            io.BytesIO(parquet_bytes),
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment; filename=academic-research-groups.parquet"}
        )
    else:
        return data

@router.get("/academic-research-groups/{record_id}")
async def get_academic_research_group_by_id(
    record_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific faculty member by database ID."""

    query = select(AcademicResearchGroups).where(AcademicResearchGroups.id == record_id)
    result = await db.execute(query)
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(status_code=404, detail="Faculty member not found")
    return group


@admin_router.put("/academic-research-groups/{record_id}")
async def update_academic_research_group_by_id(
    record_id: int,
    group_update: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update an academic research group entry by database ID."""

    query = select(AcademicResearchGroups).where(AcademicResearchGroups.id == record_id)
    result = await db.execute(query)
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    # Role-based access control
    if current_user.role == 'admin' or current_user.role == 'annotator':
        # Admins and annotators can edit any record
        pass
    elif current_user.role == 'faculty':
        # Faculty can only edit their own records
        if group.payroll_name != current_user.payroll_name:
            raise HTTPException(status_code=403, detail="You can only edit your own record")
    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    update_data = {k: v for k, v in group_update.items() if v is not None}
    for field, value in update_data.items():
        setattr(group, field, value)

    await db.commit()
    await db.refresh(group)
    return group

@admin_router.delete("/academic-research-groups/{record_id}")
async def delete_academic_research_group(
    record_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete an academic research group entry by database ID."""

    query = select(AcademicResearchGroups).where(AcademicResearchGroups.id == record_id)
    result = await db.execute(query)
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    # Role-based access control
    if current_user.role == 'admin' or current_user.role == 'annotator':
        # Admins and annotators can delete any record
        pass
    elif current_user.role == 'faculty':
        # Faculty can only delete their own records
        if group.payroll_name != current_user.payroll_name:
            raise HTTPException(status_code=403, detail="You can only delete your own record")
    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    await db.delete(group)
    await db.commit()
    return {"message": "Faculty member entry deleted successfully"}

@admin_router.post("/academic-research-groups/import")
async def import_research_groups_data(
    records: List[Dict[str, Any]],
    clear_existing: bool = True,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Import academic research groups data from request payload."""
    try:
        if clear_existing:
            # Clear existing data
            from sqlalchemy import delete
            await db.execute(delete(AcademicResearchGroups))

        imported_count = 0
        batch = []
        batch_size = 100

        for row in records:
            # Helper function to parse boolean values
            def parse_bool(value):
                if value is None or value == '':
                    return None
                if value in ('1.0', '1', 1, True, 'true', 'True'):
                    return True
                if value in ('0.0', '0', 0, False, 'false', 'False'):
                    return False
                return None

            # Helper function to parse integers
            def parse_int(value):
                if value is None or value == '':
                    return None
                try:
                    return int(float(value))  # Handle values like "231174.0"
                except (ValueError, TypeError):
                    return None

            # Helper function to clean strings
            def clean_string(value):
                if value is None or value == '':
                    return None
                return str(value).strip()

            # Convert row to database record with validation
            record = AcademicResearchGroups(
                payroll_name=clean_string(row.get('payroll_name')),
                payroll_year=parse_int(row.get('payroll_year')),
                position=clean_string(row.get('position')),
                oa_display_name=clean_string(row.get('oa_display_name')),
                is_prof=parse_bool(row.get('is_prof')),
                perceived_as_male=parse_bool(row.get('perceived_as_male')),
                host_dept=clean_string(row.get('host_dept')),
                has_research_group=parse_bool(row.get('has_research_group')),
                group_size=parse_int(row.get('group_size')),
                oa_uid=clean_string(row.get('oa_uid')),
                group_url=clean_string(row.get('group_url')),
                first_pub_year=parse_int(row.get('first_pub_year')),
                inst_ipeds_id=clean_string(row.get('inst_ipeds_id', '')).replace('.0', '') if row.get('inst_ipeds_id') else None,
                notes=clean_string(row.get('notes')),
                college=clean_string(row.get('college')),
            )

            # Validate required fields
            if not record.payroll_name:
                continue  # Skip records without required payroll_name

            batch.append(record)

            # Process batch
            if len(batch) >= batch_size:
                db.add_all(batch)
                await db.commit()
                imported_count += len(batch)
                batch = []

        # Process remaining records
        if batch:
            db.add_all(batch)
            await db.commit()
            imported_count += len(batch)

        # Automatically sync users from payroll data after successful import
        from ..routers.auth import sync_users_from_payroll
        user_sync_result = await sync_users_from_payroll(db)
        await db.commit()

        return {
            "message": "Data imported successfully",
            "imported_count": imported_count,
            "records_received": len(records),
            "user_sync": user_sync_result
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@admin_router.post("/academic-research-groups/bulk")
async def bulk_create_academic_research_groups(
    groups: List[AcademicResearchGroupCreate],
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Bulk create academic research group entries."""
    db_groups = []
    for group in groups:
        db_group = AcademicResearchGroups(**group.model_dump())
        db.add(db_group)
        db_groups.append(db_group)

    await db.commit()
    for db_group in db_groups:
        await db.refresh(db_group)

    # Automatically sync users from payroll data after successful bulk create
    from ..routers.auth import sync_users_from_payroll
    user_sync_result = await sync_users_from_payroll(db)
    await db.commit()

    return {
        "groups": db_groups,
        "user_sync": user_sync_result
    }

@router.get("/google-scholar-venues")
async def get_google_scholar_venues(
    format: str = "json",
    db: AsyncSession = Depends(get_db_session)
):
    """Get Google Scholar venues data - return JSON or download parquet."""

    query = select(GoogleScholarVenues).order_by(GoogleScholarVenues.h5_index.desc())
    result = await db.execute(query)
    venues = result.scalars().all()

    data = []
    for venue in venues:
        data.append({
            'source': venue.source,
            'venue': venue.venue,
            'field': venue.field,
            'h5_index': venue.h5_index,
            'h5_median': venue.h5_median
        })

    if format.lower() == "parquet":
        # Convert to DataFrame for parquet export
        df = pd.DataFrame(data)

        # Convert to parquet and return as download
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False, engine="pyarrow")
        buffer.seek(0)
        parquet_bytes = buffer.read()

        return StreamingResponse(
            io.BytesIO(parquet_bytes),
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment; filename=google-scholar-venues.parquet"}
        )
    else:
        return data

@admin_router.post("/google-scholar-venues/import")
async def import_google_scholar_data(
    records: List[Dict[str, Any]],
    clear_existing: bool = True,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Import Google Scholar venue data from request payload."""
    try:
        if clear_existing:
            # Clear existing data
            from sqlalchemy import delete
            await db.execute(delete(GoogleScholarVenues))

        imported_count = 0
        batch = []
        batch_size = 100

        for row in records:
            # Helper function to clean strings
            def clean_string(value):
                if value is None or value == '':
                    return None
                return str(value).strip()

            # Helper function to parse integers
            def parse_int(value):
                if value is None or value == '':
                    return None
                try:
                    return int(float(value))
                except (ValueError, TypeError):
                    return None

            # Convert row to database record with validation
            record = GoogleScholarVenues(
                source=clean_string(row.get('source')),
                venue=clean_string(row.get('venue')),
                field=clean_string(row.get('field')),
                h5_index=parse_int(row.get('h5_index')),
                h5_median=parse_int(row.get('h5_median'))
            )

            # Validate required fields
            if not all([record.source, record.venue, record.field,
                       record.h5_index is not None, record.h5_median is not None]):
                continue  # Skip records with missing required fields

            batch.append(record)

            # Process batch
            if len(batch) >= batch_size:
                db.add_all(batch)
                await db.commit()
                imported_count += len(batch)
                batch = []

        # Process remaining records
        if batch:
            db.add_all(batch)
            await db.commit()
            imported_count += len(batch)

        return {
            "message": "Google Scholar venue data imported successfully",
            "imported_count": imported_count,
            "records_received": len(records)
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
    
#!TODO: fix once we have storage
# @router.get("/s2orc/arxiv/stream")
# async def stream_arxiv_texts(
#     year: Optional[int] = None,
#     format: str = "ndjson",  # ndjson or csv
#     user: User = Depends(get_current_active_user)
# ):
#     """
#     Stream S2ORC arXiv papers with full text and annotations.

#     Requires JWT token in header: `Authorization: Bearer <token>`

#     Parameters:
#     - year: Optional filter by publication year
#     - format: Output format - 'ndjson' (default) or 'csv'

#     Returns streaming download of papers with:
#     - corpusid: S2 corpus ID
#     - year: Publication year
#     - text: Full paper text
#     - annotations: Bibliography references and other annotations
#     """
#     def generate_data():
#         try:
#             # Get DuckDB connection with scisciDB attached
#             duckdb_client = get_duckdb_client()
#             conn = duckdb_client.connect()

#             # Use materialized view for fast queries
#             query = """
#                 SELECT
#                     corpusid,
#                     year,
#                     text,
#                     annotations
#                 FROM arxiv_fulltext
#                 WHERE 1=1
#             """

#             if year:
#                 query += f" AND year = {year}"

#             # Execute query and stream results in batches
#             cursor = conn.execute(query)
#             batch_size = 1000

#             if format == "csv":
#                 # CSV header
#                 yield "corpusid,year,text,annotations\n"

#             while True:
#                 batch = cursor.fetchmany(batch_size)
#                 if not batch:
#                     break

#                 for row in batch:
#                     corpusid, year_val, text, annotations = row

#                     if format == "ndjson":
#                         # NDJSON format - one JSON object per line
#                         data = {
#                             "corpusid": corpusid,
#                             "year": year_val,
#                             "text": text,
#                             "annotations": annotations
#                         }
#                         yield json.dumps(data, ensure_ascii=False) + "\n"

#                     elif format == "csv":
#                         # CSV format - escape quotes and newlines
#                         text_escaped = text.replace('"', '""').replace('\n', '\\n') if text else ""
#                         annotations_str = json.dumps(annotations) if annotations else ""
#                         annotations_escaped = annotations_str.replace('"', '""')

#                         yield f'"{corpusid}","{year_val}","{text_escaped}","{annotations_escaped}"\n'

#         except Exception as e:
#             # Stream error back to client
#             error_msg = {"error": f"Query failed: {str(e)}"}
#             yield json.dumps(error_msg) + "\n"
#         finally:
#             # Clean up connection
#             try:
#                 duckdb_client.close()
#             except:
#                 pass

#     # Set up streaming response
#     filename = f"arxiv_s2orc_{year or 'all'}.{format}"
#     media_type = "application/x-ndjson" if format == "ndjson" else "text/csv"

#     return StreamingResponse(
#         generate_data(),
#         media_type=media_type,
#         headers={
#             "Content-Disposition": f"attachment; filename={filename}",
#             "X-Content-Type-Options": "nosniff"
#         }
#     )

#!TODO: fix once we have storage
# @router.get("/s2orc/arxiv/stats")
# async def get_arxiv_stats(
#     user: User = Depends(get_current_active_user)
# ):
#     """
#     Get S2ORC arXiv dataset statistics including yearly breakdown.

#     Requires JWT token in header: `Authorization: Bearer <token>`

#     Returns:
#     - total_papers: Total number of papers
#     - yearly_stats: Papers count by year
#     - size_estimates: Estimated dataset sizes
#     """
#     try:
#         # Get DuckDB connection with scisciDB attached
#         duckdb_client = get_duckdb_client()
#         conn = duckdb_client.connect()

#         # Get total count
#         total_query = "SELECT COUNT(*) FROM arxiv_fulltext"
#         total_result = conn.execute(total_query).fetchone()
#         total_papers = total_result[0] if total_result else 0

#         # Get yearly breakdown
#         yearly_query = """
#             SELECT
#                 year,
#                 COUNT(*) as paper_count,
#                 AVG(LENGTH(text)) as avg_text_length
#             FROM arxiv_fulltext
#             WHERE year IS NOT NULL
#             GROUP BY year
#             ORDER BY year DESC
#         """
#         yearly_result = conn.execute(yearly_query).fetchall()

#         yearly_stats = {}
#         for row in yearly_result:
#             year, count, avg_length = row
#             yearly_stats[str(year)] = {
#                 "papers": count,
#                 "avg_text_length": int(avg_length) if avg_length else 0
#             }

#         # Calculate size estimates (rough approximation)
#         total_avg_length = conn.execute("SELECT AVG(LENGTH(text)) FROM arxiv_fulltext").fetchone()[0]
#         estimated_size_bytes = total_papers * (total_avg_length or 0) * 1.2  # Add overhead factor
#         estimated_size_gb = estimated_size_bytes / (1024**3)

#         return {
#             "total_papers": total_papers,
#             "yearly_stats": yearly_stats,
#             "estimated_size": {
#                 "bytes": int(estimated_size_bytes),
#                 "gb": round(estimated_size_gb, 2)
#             },
#             "avg_text_length": int(total_avg_length) if total_avg_length else 0
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
#     finally:
#         try:
#             duckdb_client.close()
#         except:
#             pass
