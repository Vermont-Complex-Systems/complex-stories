from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse
import os
import csv
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
import io
from pydantic import BaseModel
import time
from label_studio_sdk import LabelStudio
import io
from label_studio_sdk.client import LabelStudio
from label_studio_sdk.core.api_error import ApiError
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

    if (DATA_DIR / "academic-research-groups.parquet").exists():
        datasets.append({
            "name": "academic-research-groups",
            "filename": "academic-research-groups.parquet",
            "description": "Professors label with research groups and publications",
            "format": "Parquet",
            "keywords": ["research", "groups"],
            "url": "/datasets/data/academic-research-groups.parquet"
        })

    if (DATA_DIR / "academic-department.parquet").exists():
        datasets.append({
            "name": "academic-department",
            "filename": "academic-department.parquet",
            "description": "Mapping of academic departments to their colleges and other metadata",
            "format": "Parquet",
            "keywords": ["colleges", "scisci"],
            "url": "/datasets/data/academic-department.parquet"
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


@router.get("/data/{filename}")
async def get_dataset_file(filename: str):
    """Serve raw dataset files."""
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset file '{filename}' not found")

    # Ensure it's a supported file type for security
    if not (filename.endswith('.csv') or filename.endswith('.parquet')):
        raise HTTPException(status_code=400, detail="Only CSV and Parquet files are supported")

    # Set appropriate media type
    media_type = "application/octet-stream" if filename.endswith('.parquet') else "text/csv"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "public, max-age=3600"  # Cache for 1 hour
        }
    )


@router.get("/data/{filename}/preview")
async def preview_dataset(filename: str, limit: int = 10):
    """Preview first N rows of a dataset."""
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset file '{filename}' not found")

    if not (filename.endswith('.csv') or filename.endswith('.parquet')):
        raise HTTPException(status_code=400, detail="Only CSV and Parquet files are supported")

    try:
        if filename.endswith('.parquet'):
            # Read parquet file with pandas
            df = pd.read_parquet(file_path)
            # Get first N rows
            preview_df = df.head(limit)
            rows = preview_df.fillna("").to_dict('records')
            columns = list(df.columns)
        else:
            # Read CSV file
            rows = []
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for i, row in enumerate(csv_reader):
                    if i >= limit:
                        break
                    rows.append(row)
            columns = list(rows[0].keys()) if rows else []

        return {
            "filename": filename,
            "preview_rows": limit,
            "total_rows_shown": len(rows),
            "columns": columns,
            "data": rows
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


# @router.get("/academic-research-groups")
# async def get_academic_research_groups(
#     limit: int = None,
#     department: str = None,
#     year: int = None,
#     inst_ipeds_id: int = None,
#     college: str = None
# ):
#     """Get academic research groups data with optional filtering."""
#     file_path = DATA_DIR / "academic-research-groups.parquet"

#     if not file_path.exists():
#         raise HTTPException(status_code=404, detail="Academic research groups dataset not found")

#     try:
#         # Read parquet file with pandas
#         df = pd.read_parquet(file_path)

#         # Apply filters
#         if department:
#             df = df[df['host_dept'].str.contains(department, case=False, na=False)]

#         if year:
#             df = df[df['payroll_year'] == year]

#         if inst_ipeds_id:
#             df = df[df['inst_ipeds_id'] == inst_ipeds_id]

#         if college:
#             df = df[df['college'].str.contains(college, case=False, na=False)]

#         # Apply limit
#         if limit:
#             df = df.head(limit)

#         # Convert to records and clean NaN values
#         rows = df.fillna("").to_dict('records')

#         return {
#             "dataset": "academic-research-groups",
#             "total_rows": len(rows),
#             "filters_applied": {
#                 "department": department,
#                 "year": year,
#                 "inst_ipeds_id": inst_ipeds_id,
#                 "college": college,
#                 "limit": limit
#             },
#             "data": rows
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error reading dataset: {str(e)}")


@router.get("/academic-department")
async def get_academic_department(college: str = None):
    """Get academic department data with optional filtering."""
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
            "total_rows": len(rows),
            "filters_applied": {
                "college": college
            },
            "data": rows
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading dataset: {str(e)}")


@router.get("/stats")
async def get_datasets_stats():
    """Get statistics about all datasets."""
    stats = {}

    for dataset in get_available_datasets():
        filename = dataset["filename"]
        file_path = DATA_DIR / filename

        if file_path.exists():
            try:
                if filename.endswith('.parquet'):
                    # Read parquet file with pandas
                    df = pd.read_parquet(file_path)
                    row_count = len(df)
                    columns = list(df.columns)
                else:
                    # Read CSV file
                    with open(file_path, 'r', encoding='utf-8') as file:
                        csv_reader = csv.DictReader(file)
                        row_count = sum(1 for _ in csv_reader)

                        # Get column names
                        file.seek(0)
                        csv_reader = csv.DictReader(file)
                        columns = csv_reader.fieldnames or []

                stats[dataset["name"]] = {
                    "filename": filename,
                    "row_count": row_count,
                    "column_count": len(columns),
                    "columns": columns,
                    "file_size_bytes": file_path.stat().st_size
                }
            except Exception as e:
                stats[dataset["name"]] = {"error": str(e)}

    return {"stats": stats}

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