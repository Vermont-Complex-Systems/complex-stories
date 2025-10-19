from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import os
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import io
import time
from label_studio_sdk import LabelStudio
import logging

from dotenv import load_dotenv
from ..core.database import get_db_session
from ..models.annotation_datasets import AcademicResearchGroups, AcademicResearchGroupCreate

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("export_snapshots")

load_dotenv()  # take environment variables

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL")
LABEL_STUDIO_API_KEY = os.getenv("LABEL_STUDIO_API_KEY")
FACULTY_PROJECT_ID = os.getenv("FACULTY_PROJECT_ID")
DEPARTMENT_PROJECT_ID = os.getenv("DEPARTMENT_PROJECT_ID")

# Base directory for datasets
DATA_DIR = Path(__file__).parent.parent.parent / "data"

def get_available_datasets() -> List[Dict[str, Any]]:
    """Get list of available datasets with metadata."""
    datasets = []

    # Dynamic datasets from Label Studio
    if LABEL_STUDIO_URL and LABEL_STUDIO_API_KEY and FACULTY_PROJECT_ID:
        datasets.append({
            "name": "academic-research-groups",
            "description": "Faculty research groups data from Label Studio annotations",
            "format": "Dynamic (JSON/Parquet)",
            "source": "Label Studio",
            "keywords": ["research", "groups", "faculty", "annotations"],
            "endpoints": {
                "json": "/datasets/academic-research-groups",
                "parquet": "/datasets/academic-research-groups?format=parquet"
            }
        })

    # Static datasets (if any exist)
    if (DATA_DIR / "academic-department.parquet").exists():
        datasets.append({
            "name": "academic-department",
            "filename": "academic-department.parquet",
            "description": "Mapping of academic departments to their colleges and other metadata",
            "format": "Parquet",
            "source": "Static file",
            "keywords": ["colleges", "scisci"],
            "endpoints": {
                "json": "/datasets/academic-department",
                "file": "/datasets/data/academic-department.parquet"
            }
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

def export_snapshot(project_id: int, export_type: str = "CSV") -> bytes:
    """Download Label Studio export in memory."""
    ls = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_KEY)
    export_job = ls.projects.exports.create(id=project_id, title="API Export")

    export_id = export_job.id
    logger.info(f"Created export: {export_id}")

    # Poll until finished
    start = time.time()
    timeout = 300
    while True:
        job = ls.projects.exports.get(id=project_id, export_pk=export_id)
        if job.status in ("completed", "failed"):
            break
        if time.time() - start > timeout:
            raise HTTPException(status_code=504, detail="Export timed out")
        time.sleep(1)

    if job.status == "failed":
        raise HTTPException(status_code=500, detail="Label Studio export failed")

    # Download as bytes
    return b"".join(
        ls.projects.exports.download(
            id=project_id,
            export_pk=export_id,
            export_type=export_type,
            request_options={"chunk_size": 1024},
        )
    )

@router.get("/academic-department")
async def get_academic_department(inst_ipeds_id: int = 231174, year: int = 2023, format: str = "json"):
    """Get department data from Label Studio - return JSON or download parquet."""
    # Export data as CSV first
    raw_bytes = export_snapshot(DEPARTMENT_PROJECT_ID, export_type="CSV")
    raw_csv = raw_bytes.decode("utf-8")

    # Convert CSV to DataFrame
    df = pd.read_csv(io.StringIO(raw_csv))

    # Wrangle 
    df.drop(['annotation_id', 'annotator', 'created_at', 'updated_at', 'lead_time', 'id'], axis=1, inplace=True)
    df.fillna("", inplace=True)
    
    # Apply IPEDS filter if specified
    if inst_ipeds_id and "inst_ipeds_id" in df.columns:
        df = df[df['inst_ipeds_id'] == inst_ipeds_id]

    if year and "year" in df.columns:
        df = df[df['year'] == year]

    if format.lower() == "parquet":
        # Convert to parquet and return as download
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False, engine="pyarrow")
        buffer.seek(0)
        parquet_bytes = buffer.read()

        return StreamingResponse(
            io.BytesIO(parquet_bytes),
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment; filename=academic-department.parquet"}
        )
    else:
        # Return JSON data (default)
        rows = df.to_dict('records')

        return rows

@router.post("/academic-research-groups")
async def create_academic_research_group(
    group: AcademicResearchGroupCreate,
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

    if format.lower() == "parquet":
        # Convert to DataFrame for parquet export
        data = []
        for annotation in annotations:
            data.append({
                'id': annotation.id,
                'payroll_name': annotation.payroll_name,
                'payroll_year': annotation.payroll_year,
                'position': annotation.position,
                'oa_display_name': annotation.oa_display_name,
                'is_prof': annotation.is_prof,
                'perceived_as_male': annotation.perceived_as_male,
                'host_dept': annotation.host_dept,
                'has_research_group': annotation.has_research_group,
                'group_size': annotation.group_size,
                'oa_uid': annotation.oa_uid,
                'group_url': annotation.group_url,
                'first_pub_year': annotation.first_pub_year,
                'inst_ipeds_id': annotation.inst_ipeds_id,
                'notes': annotation.notes,
                'college': annotation.college
            })

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
        # Return JSON data (default)
        return annotations

@router.post("/academic-research-groups/bulk")
async def bulk_create_academic_research_groups(
    groups: List[AcademicResearchGroupCreate],
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

    return db_groups

@router.post("/academic-research-groups/import")
async def import_research_groups_data(
    records: List[Dict[str, Any]],
    clear_existing: bool = True,
    db: AsyncSession = Depends(get_db_session)
):
    """Import academic research groups data from request payload."""
    try:
        if clear_existing:
            # Clear existing data
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

        return {
            "message": "Data imported successfully",
            "imported_count": imported_count,
            "records_received": len(records)
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

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

@router.put("/academic-research-groups/{record_id}")
async def update_academic_research_group_by_id(
    record_id: int,
    group_update: Dict[str, Any],
    db: AsyncSession = Depends(get_db_session)
):
    """Update an academic research group entry by database ID."""

    query = select(AcademicResearchGroups).where(AcademicResearchGroups.id == record_id)
    result = await db.execute(query)
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    update_data = {k: v for k, v in group_update.items() if v is not None}
    for field, value in update_data.items():
        setattr(group, field, value)

    await db.commit()
    await db.refresh(group)
    return group

@router.delete("/academic-research-groups/{record_id}")
async def delete_academic_research_group(
    record_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete an academic research group entry by database ID."""

    query = select(AcademicResearchGroups).where(AcademicResearchGroups.id == record_id)
    result = await db.execute(query)
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    await db.delete(group)
    await db.commit()
    return {"message": "Faculty member entry deleted successfully"}
