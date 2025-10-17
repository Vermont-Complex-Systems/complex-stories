from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
import io
import time
from label_studio_sdk import LabelStudio
import logging

from dotenv import load_dotenv

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("export_snapshots")

load_dotenv()  # take environment variables

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL")
LABEL_STUDIO_API_KEY = os.getenv("LABEL_STUDIO_API_KEY")
FACULTY_PROJECT_ID = os.getenv("FACULTY_PROJECT_ID")


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

@router.get("/academic-research-groups")
def get_academic_research_groups(inst_ipeds_id: int = None, year: int = None, format: str = "json"):
    """Get academic research groups data from Label Studio - return JSON or download parquet."""
    # Export data as CSV first
    raw_bytes = export_snapshot(FACULTY_PROJECT_ID, export_type="CSV")
    raw_csv = raw_bytes.decode("utf-8")

    # Convert CSV to DataFrame
    import io as io_module
    df = pd.read_csv(io_module.StringIO(raw_csv))

    # Wrangle 
    df.drop(['annotation_id', 'annotator', 'created_at', 'updated_at', 'notes', 'lead_time', 'id'], axis=1, inplace=True)
    df.fillna("", inplace=True)
    df['is_prof'] = np.where(df.position.str.contains("Professor"), 1, 0)

    # Apply IPEDS filter if specified
    if inst_ipeds_id and "inst_ipeds_id" in df.columns:
        df = df[df['inst_ipeds_id'] == inst_ipeds_id]

    if year and "payroll_year" in df.columns:
        df = df[df['payroll_year'] == year]

    if format.lower() == "parquet":
        # Making sure fields are appropriate for pyarrow
        df['first_pub_year'] = pd.to_numeric(df['first_pub_year'], errors='coerce')
        df['group_size'] = pd.to_numeric(df['group_size'], errors='coerce')
        df['has_research_group'] = pd.to_numeric(df['has_research_group'], errors='coerce')
        df['perceived_as_male'] = pd.to_numeric(df['perceived_as_male'], errors='coerce')
        
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
        rows = df.to_dict('records')

        return rows

@router.get("/academic-department")
async def get_academic_department(college: str = None):
    """Get academic department data with optional filtering.

    Note: This endpoint still uses a static parquet file.
    TODO: Consider migrating to Label Studio or database source.
    """
    file_path = DATA_DIR / "academic-department.parquet"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Academic department dataset not found")

    try:
        # Read parquet file with pandas
        df = pd.read_parquet(file_path)

        # Apply college filter if specified
        if college:
            df = df[df['college'].str.contains(college, case=False, na=False)]

        # Convert to records and clean NaN values
        rows = df.fillna("").to_dict('records')

        return {
            "dataset": "academic-department",
            "source": "static_file",
            "total_rows": len(rows),
            "filters_applied": {
                "college": college
            },
            "data": rows
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading dataset: {str(e)}")
