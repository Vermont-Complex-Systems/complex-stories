from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
import io
import time
from label_studio_sdk import LabelStudio
import logging
from pydantic import BaseModel

from dotenv import load_dotenv
from ..core.database import get_db_session
from ..models.annotation_datasets import AcademicResearchGroups

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

# Pydantic schemas for academic research groups
class AcademicResearchGroupCreate(BaseModel):
    payroll_name: str
    payroll_year: int
    position: Optional[str] = None
    oa_display_name: Optional[str] = None
    is_prof: Optional[bool] = None
    perceived_as_male: Optional[bool] = None
    host_dept: Optional[str] = None
    has_research_group: Optional[bool] = None
    group_size: Optional[int] = None
    oa_uid: Optional[str] = None
    group_url: Optional[str] = None
    first_pub_year: Optional[int] = None
    inst_ipeds_id: Optional[str] = None
    notes: Optional[str] = None
    college: Optional[str] = None

class AcademicResearchGroupUpdate(BaseModel):
    payroll_name: Optional[str] = None
    payroll_year: Optional[int] = None
    position: Optional[str] = None
    oa_display_name: Optional[str] = None
    is_prof: Optional[bool] = None
    perceived_as_male: Optional[bool] = None
    host_dept: Optional[str] = None
    has_research_group: Optional[bool] = None
    group_size: Optional[int] = None
    oa_uid: Optional[str] = None
    group_url: Optional[str] = None
    first_pub_year: Optional[int] = None
    inst_ipeds_id: Optional[str] = None
    notes: Optional[str] = None
    college: Optional[str] = None

class AcademicResearchGroupResponse(BaseModel):
    id: int
    payroll_name: str
    payroll_year: int
    position: Optional[str] = None
    oa_display_name: Optional[str] = None
    is_prof: Optional[bool] = None
    perceived_as_male: Optional[bool] = None
    host_dept: Optional[str] = None
    has_research_group: Optional[bool] = None
    group_size: Optional[int] = None
    oa_uid: Optional[str] = None
    group_url: Optional[str] = None
    first_pub_year: Optional[int] = None
    inst_ipeds_id: Optional[str] = None
    notes: Optional[str] = None
    college: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/academic-research-groups", response_model=List[AcademicResearchGroupResponse])
async def get_academic_research_groups_list(
    skip: int = 0,
    payroll_year: Optional[int] = None,
    format: str = "json",
    db: AsyncSession = Depends(get_db_session)
):
    """Get academic research groups data from database - return JSON or download parquet."""
    from sqlalchemy import select

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

@router.get("/academic-department")
async def get_academic_department(inst_ipeds_id: int = 231174, year: int = 2023, format: str = "json"):
    """Get department data from Label Studio - return JSON or download parquet."""
    # Export data as CSV first
    raw_bytes = export_snapshot(DEPARTMENT_PROJECT_ID, export_type="CSV")
    raw_csv = raw_bytes.decode("utf-8")

    # Convert CSV to DataFrame
    import io as io_module
    df = pd.read_csv(io_module.StringIO(raw_csv))

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



# CRUD endpoints for academic research groups
@router.get("/academic-research-groups/{oa_uid}", response_model=AcademicResearchGroupResponse)
async def get_academic_research_group_by_uid(
    oa_uid: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific faculty member by OpenAlex UID."""
    from sqlalchemy import select

    query = select(AcademicResearchGroups).where(AcademicResearchGroups.oa_uid == oa_uid)
    result = await db.execute(query)
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(status_code=404, detail="Faculty member not found")
    return group


@router.post("/academic-research-groups", response_model=AcademicResearchGroupResponse)
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


@router.put("/academic-research-groups/{oa_uid}", response_model=AcademicResearchGroupResponse)
async def update_academic_research_group(
    oa_uid: str,
    group_update: AcademicResearchGroupUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Update an academic research group entry by OpenAlex UID."""
    from sqlalchemy import select

    query = select(AcademicResearchGroups).where(AcademicResearchGroups.oa_uid == oa_uid)
    result = await db.execute(query)
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    update_data = group_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)

    await db.commit()
    await db.refresh(group)
    return group


@router.put("/academic-research-groups/by-id/{record_id}", response_model=AcademicResearchGroupResponse)
async def update_academic_research_group_by_id(
    record_id: int,
    group_update: AcademicResearchGroupUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Update an academic research group entry by database ID."""
    from sqlalchemy import select

    query = select(AcademicResearchGroups).where(AcademicResearchGroups.id == record_id)
    result = await db.execute(query)
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    update_data = group_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)

    await db.commit()
    await db.refresh(group)
    return group


@router.delete("/academic-research-groups/{oa_uid}")
async def delete_academic_research_group(
    oa_uid: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete an academic research group entry by OpenAlex UID."""
    from sqlalchemy import select

    query = select(AcademicResearchGroups).where(AcademicResearchGroups.oa_uid == oa_uid)
    result = await db.execute(query)
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    await db.delete(group)
    await db.commit()
    return {"message": "Faculty member entry deleted successfully"}


@router.post("/academic-research-groups/bulk", response_model=List[AcademicResearchGroupResponse])
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


# Import endpoint for loading CSV data
@router.post("/academic-research-groups/import-csv")
async def import_csv_data(
    db: AsyncSession = Depends(get_db_session)
):
    """Import UVM salaries CSV data into database."""
    import csv
    from pathlib import Path

    # Path to the CSV file - use annotated version
    csv_path = Path(__file__).parent.parent.parent / "scripts/label-studio/academic-research-groups/import/academic-research-groups2.csv"

    if not csv_path.exists():
        raise HTTPException(status_code=404, detail=f"CSV file not found: {csv_path}")

    try:
        # Clear existing data (optional)
        from sqlalchemy import delete
        await db.execute(delete(AcademicResearchGroups))

        imported_count = 0

        # Read and import CSV
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            batch = []
            batch_size = 100

            for row in reader:
                # Helper function to parse boolean values
                def parse_bool(value):
                    if not value or value == '':
                        return None
                    if value == '1.0' or value == '1':
                        return True
                    if value == '0.0' or value == '0':
                        return False
                    return None

                # Helper function to parse integers
                def parse_int(value):
                    if not value or value == '':
                        return None
                    try:
                        return int(float(value))  # Handle values like "231174.0"
                    except (ValueError, TypeError):
                        return None

                # Convert CSV row to database record
                record = AcademicResearchGroups(
                    payroll_name=row['payroll_name'] if row['payroll_name'] else None,
                    payroll_year=parse_int(row['payroll_year']),
                    position=row['position'] if row['position'] else None,
                    oa_display_name=row['oa_display_name'] if row['oa_display_name'] else None,
                    is_prof=parse_bool(row['is_prof']),
                    perceived_as_male=parse_bool(row['perceived_as_male']),
                    host_dept=row['host_dept'] if row['host_dept'] else None,
                    has_research_group=parse_bool(row['has_research_group']),
                    group_size=parse_int(row['group_size']),
                    oa_uid=row['oa_uid'] if row['oa_uid'] else None,
                    group_url=row['group_url'] if row['group_url'] else None,
                    first_pub_year=parse_int(row['first_pub_year']),
                    inst_ipeds_id=row['inst_ipeds_id'].replace('.0', '') if row['inst_ipeds_id'] else None,  # Keep as string, remove .0
                    notes=row['notes'] if row['notes'] else None,
                    college=row['college'] if row['college'] else None,
                )

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
            "message": "CSV data imported successfully",
            "imported_count": imported_count,
            "csv_path": str(csv_path)
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
