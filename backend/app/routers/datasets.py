from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse
import os
import csv
from pathlib import Path
from typing import List, Dict, Any
import io

router = APIRouter()

# Base directory for datasets
DATA_DIR = Path(__file__).parent.parent.parent / "data"


def get_available_datasets() -> List[Dict[str, Any]]:
    """Get list of available datasets with metadata."""
    datasets = []

    if (DATA_DIR / "academic-research-groups.csv").exists():
        datasets.append({
            "name": "academic-research-groups",
            "filename": "academic-research-groups.csv",
            "description": "Professors label with research groups and publications",
            "format": "CSV",
            "keywords": ["research", "groups"],
            "url": "/datasets/data/academic-research-groups.csv"
        })

    if (DATA_DIR / "academic-department.csv").exists():
        datasets.append({
            "name": "academic-department",
            "filename": "academic-department.csv",
            "description": "Mapping of academic departments to their colleges and other metadata",
            "format": "CSV",
            "keywords": ["colleges", "scisci"],
            "url": "/datasets/data/academic-department.csv"
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

    # Ensure it's a CSV file for security
    if not filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    return FileResponse(
        path=file_path,
        media_type="text/csv",
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

    if not filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        rows = []
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for i, row in enumerate(csv_reader):
                if i >= limit:
                    break
                rows.append(row)

        return {
            "filename": filename,
            "preview_rows": limit,
            "total_rows_shown": len(rows),
            "columns": list(rows[0].keys()) if rows else [],
            "data": rows
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@router.get("/academic-research-groups")
async def get_academic_research_groups(
    limit: int = None,
    department: str = None,
    year: int = None,
    inst_ipeds_id: int = None,
    college: str = None
):
    """Get academic research groups data with optional filtering."""
    file_path = DATA_DIR / "academic-research-groups.csv"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Academic research groups dataset not found")

    try:
        rows = []
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Apply department filter if specified
                if department and department.lower() not in row.get('host_dept', '').lower():
                    continue

                # Apply year filter if specified
                if year and row.get('payroll_year') and int(row.get('payroll_year', 0)) != year:
                    continue

                # Apply institution filter if specified
                if inst_ipeds_id and row.get('inst_ipeds_id') and int(row.get('inst_ipeds_id', 0)) != inst_ipeds_id:
                    continue

                # Apply college filter if specified
                if college and college.lower() not in row.get('college', '').lower():
                    continue

                rows.append(row)

                # Apply limit if specified
                if limit and len(rows) >= limit:
                    break

        return {
            "dataset": "academic-research-groups",
            "total_rows": len(rows),
            "filters_applied": {
                "department": department,
                "year": year,
                "inst_ipeds_id": inst_ipeds_id,
                "college": college,
                "limit": limit
            },
            "data": rows
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading dataset: {str(e)}")


@router.get("/academic-department")
async def get_academic_department(college: str = None):
    """Get academic department data with optional filtering."""
    file_path = DATA_DIR / "academic-department.csv"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Academic department dataset not found")

    try:
        rows = []
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Apply college filter if specified
                if college and college.lower() not in row.get('college', '').lower():
                    continue

                rows.append(row)

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