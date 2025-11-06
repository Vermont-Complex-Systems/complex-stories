from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import pandas as pd
import numpy as np
import io
import os
import time
import logging
from label_studio_sdk import LabelStudio
from dotenv import load_dotenv
from ..routers.auth import get_admin_user
from ..models.auth import User

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter()
admin_router = APIRouter()

# Label Studio configuration
LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL")
LABEL_STUDIO_API_KEY = os.getenv("LABEL_STUDIO_API_KEY")
FACULTY_PROJECT_ID = os.getenv("FACULTY_PROJECT_ID")
DEPARTMENT_PROJECT_ID = os.getenv("DEPARTMENT_PROJECT_ID")

# Cache for export data
_export_cache = {}
CACHE_TTL = 3600  # 1 hour cache

def export_snapshot(project_id: int, export_type: str = "CSV", force_refresh: bool = False, timeout: int = 300) -> bytes:
    """
    Download Label Studio export in memory with optional caching.

    Args:
        project_id: Label Studio project ID
        export_type: Export format (CSV, JSON, etc.)
        force_refresh: Force fresh export (ignore cache)
        timeout: Maximum time to wait for export completion (seconds)

    Returns:
        Export data as bytes

    Raises:
        HTTPException: For various error conditions
    """
    if not LABEL_STUDIO_URL or not LABEL_STUDIO_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Label Studio credentials not configured"
        )

    # Check cache first (unless force_refresh is True)
    cache_key = f"{project_id}_{export_type}"
    current_time = time.time()

    if not force_refresh and cache_key in _export_cache:
        cached_data, timestamp = _export_cache[cache_key]
        if current_time - timestamp < CACHE_TTL:
            logger.info(f"Using cached export for project {project_id}")
            return cached_data

    # Create fresh export with retry logic
    logger.info(f"Creating fresh export for project {project_id} (force_refresh={force_refresh})")

    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Disable SSL verification for local development
            import httpx
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            ls = LabelStudio(
                base_url=LABEL_STUDIO_URL,
                api_key=LABEL_STUDIO_API_KEY,
                httpx_client=httpx.Client(verify=False)
            )

            # Create export job
            export_job = ls.projects.exports.create(
                id=project_id,
                title=f"API Export {int(current_time)}"
            )

            export_id = export_job.id
            logger.info(f"Created export job {export_id} for project {project_id}")

            # Poll until finished with exponential backoff
            start_time = time.time()
            poll_interval = 1  # Start with 1 second
            max_poll_interval = 10  # Cap at 10 seconds

            while True:
                try:
                    job = ls.projects.exports.get(id=project_id, export_pk=export_id)

                    if job.status == "completed":
                        logger.info(f"Export {export_id} completed successfully")
                        break
                    elif job.status == "failed":
                        error_msg = f"Export {export_id} failed"
                        logger.error(error_msg)
                        raise HTTPException(status_code=500, detail=error_msg)
                    elif job.status in ("created", "queued", "in_progress"):
                        # Still processing
                        elapsed = time.time() - start_time
                        if elapsed > timeout:
                            raise HTTPException(
                                status_code=504,
                                detail=f"Export timed out after {timeout} seconds"
                            )

                        logger.debug(f"Export {export_id} status: {job.status}, elapsed: {elapsed:.1f}s")
                        time.sleep(poll_interval)

                        # Exponential backoff
                        poll_interval = min(poll_interval * 1.5, max_poll_interval)
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Unknown export status: {job.status}"
                        )

                except Exception as e:
                    if "timeout" in str(e).lower():
                        raise  # Re-raise timeout errors
                    logger.warning(f"Polling error for export {export_id}: {e}")
                    time.sleep(2)  # Wait before retry

            # Download as bytes with error handling
            try:
                export_data = b"".join(
                    ls.projects.exports.download(
                        id=project_id,
                        export_pk=export_id,
                        export_type=export_type,
                        request_options={"chunk_size": 1024},
                    )
                )

                if not export_data:
                    raise HTTPException(
                        status_code=500,
                        detail="Export download returned empty data"
                    )

                # Cache the result
                _export_cache[cache_key] = (export_data, current_time)
                logger.info(f"Successfully cached export for project {project_id} ({len(export_data)} bytes)")

                return export_data

            except Exception as e:
                logger.error(f"Download failed for export {export_id}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to download export: {str(e)}"
                )

        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                logger.error(f"Export failed after {max_retries} retries: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Export failed after {max_retries} retries: {str(e)}"
                )

            logger.warning(f"Export attempt {retry_count} failed, retrying: {e}")
            time.sleep(2 ** retry_count)  # Exponential backoff between retries

def get_user_info(user_id: int) -> Dict[str, Any]:
    """
    Get user information from Label Studio API.

    Args:
        user_id: The user ID to look up

    Returns:
        Dictionary with user information (email, username, etc.)
    """
    try:
        # Disable SSL verification for local development
        import httpx
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        ls = LabelStudio(
            base_url=LABEL_STUDIO_URL,
            api_key=LABEL_STUDIO_API_KEY,
            httpx_client=httpx.Client(verify=False)
        )

        # Use the SDK to get user info
        user_data = ls.users.get(id=user_id)

        return {
            'id': user_data.id,
            'email': user_data.email,
            'username': user_data.username,
            'first_name': user_data.first_name,
            'last_name': user_data.last_name
        }

    except Exception as e:
        logger.error(f"Error fetching user info for {user_id}: {str(e)}")
        return {'id': user_id, 'email': f'user_{user_id}', 'username': f'user_{user_id}'}

def enrich_annotator_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich the dataframe with user information (email, username) for annotators.

    Args:
        df: DataFrame with annotator IDs

    Returns:
        DataFrame with added user information columns
    """
    if 'annotator' not in df.columns:
        return df

    # Get unique annotator IDs
    unique_annotators = df['annotator'].dropna().unique()

    # Create mapping of annotator ID to user info
    user_mapping = {}
    for annotator_id in unique_annotators:
        try:
            annotator_int = int(annotator_id)
            user_info = get_user_info(annotator_int)
            user_mapping[annotator_id] = user_info
        except (ValueError, TypeError):
            # Handle non-integer annotator IDs
            user_mapping[annotator_id] = {
                'id': annotator_id,
                'email': str(annotator_id),
                'username': str(annotator_id)
            }

    # Add user info columns to dataframe
    df = df.copy()
    df['annotator_email'] = df['annotator'].map(lambda x: user_mapping.get(x, {}).get('email', str(x)))
    df['annotator_username'] = df['annotator'].map(lambda x: user_mapping.get(x, {}).get('username', str(x)))

    logger.info(f"Enriched annotator data for {len(unique_annotators)} unique annotators")

    return df

def compute_inter_annotator_agreement(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute inter-annotator agreement metrics for Label Studio annotations.

    Args:
        df: DataFrame with Label Studio export data

    Returns:
        Dictionary with agreement metrics
    """
    if df.empty:
        return {"error": "No data provided"}

    # Extract task ID and annotator information
    if 'id' not in df.columns or 'annotator' not in df.columns:
        return {"error": "Required columns 'id' and 'annotator' not found"}

    # Group by id (task) to find tasks with multiple annotators
    task_counts = df.groupby('id')['annotator'].count()
    multi_annotated_tasks = task_counts[task_counts > 1].index.tolist()

    if not multi_annotated_tasks:
        return {
            "error": "No tasks with multiple annotators found",
            "total_tasks": len(task_counts),
            "multi_annotated_tasks": 0
        }

    # Filter to multi-annotated tasks
    multi_df = df[df['id'].isin(multi_annotated_tasks)]

    # Get annotation columns (exclude metadata columns)

    # Focus on the sentiment column for agreement calculation
    annotation_cols = ['sentiment'] if 'sentiment' in multi_df.columns else [col for col in multi_df.columns if col not in ['id', 'annotator', 'annotation_id']]

    agreements = {}

    for col in annotation_cols:
        if col not in multi_df.columns:
            continue

        # Calculate agreement for this annotation field
        task_agreements = []

        for task_id in multi_annotated_tasks:
            task_annotations = multi_df[multi_df['id'] == task_id][col].dropna()

            if len(task_annotations) < 2:
                continue

            # For categorical data, calculate percentage agreement
            if task_annotations.dtype == 'object' or pd.api.types.is_categorical_dtype(task_annotations):
                # Simple percentage agreement
                unique_values = task_annotations.unique()
                if len(unique_values) == 1:
                    task_agreements.append(1.0)  # Perfect agreement
                else:
                    # Calculate pairwise agreement
                    total_pairs = 0
                    agreeing_pairs = 0
                    for i, val1 in enumerate(task_annotations):
                        for j, val2 in enumerate(task_annotations):
                            if i < j:
                                total_pairs += 1
                                if val1 == val2:
                                    agreeing_pairs += 1

                    if total_pairs > 0:
                        task_agreements.append(agreeing_pairs / total_pairs)

            # For numeric data, calculate correlation or threshold-based agreement
            elif pd.api.types.is_numeric_dtype(task_annotations):
                # Calculate coefficient of variation (lower is better agreement)
                if task_annotations.std() == 0:
                    task_agreements.append(1.0)  # Perfect agreement
                else:
                    cv = task_annotations.std() / abs(task_annotations.mean()) if task_annotations.mean() != 0 else float('inf')
                    # Convert CV to agreement score (1 means perfect, 0 means high disagreement)
                    agreement_score = 1 / (1 + cv) if cv != float('inf') else 0
                    task_agreements.append(agreement_score)

        if task_agreements:
            agreements[col] = {
                "mean_agreement": np.mean(task_agreements),
                "std_agreement": np.std(task_agreements),
                "min_agreement": np.min(task_agreements),
                "max_agreement": np.max(task_agreements),
                "num_tasks": len(task_agreements)
            }

    # Calculate overall statistics
    # Use annotator emails/usernames if available, otherwise fall back to IDs
    if 'annotator_email' in multi_df.columns:
        unique_annotators = multi_df['annotator_email'].unique().tolist()
        annotator_column = 'annotator_email'
    else:
        unique_annotators = multi_df['annotator'].unique().tolist()
        annotator_column = 'annotator'

    # Calculate pairwise annotator agreements for matrix visualization
    annotator_pairs = {}
    for i, annotator1 in enumerate(unique_annotators):
        for j, annotator2 in enumerate(unique_annotators):
            if i != j:
                # Find tasks where both annotators provided annotations
                pair_agreements = []
                for task_id in multi_annotated_tasks:
                    task_data = multi_df[multi_df['id'] == task_id]
                    ann1_data = task_data[task_data[annotator_column] == annotator1]
                    ann2_data = task_data[task_data[annotator_column] == annotator2]

                    if len(ann1_data) > 0 and len(ann2_data) > 0:
                        # Compare annotations (focusing on sentiment if available)
                        if 'sentiment' in multi_df.columns:
                            ann1_val = ann1_data['sentiment'].iloc[0]
                            ann2_val = ann2_data['sentiment'].iloc[0]
                            if pd.notna(ann1_val) and pd.notna(ann2_val):
                                pair_agreements.append(1.0 if ann1_val == ann2_val else 0.0)

                if pair_agreements:
                    pair_key = f"{annotator1}_{annotator2}"
                    annotator_pairs[pair_key] = np.mean(pair_agreements)

    logger.info(f"Computed agreements for {len(agreements)} fields: {list(agreements.keys())}")
    logger.info(f"Computed {len(annotator_pairs)} annotator pairs")

    return {
        "total_tasks": len(task_counts),
        "multi_annotated_tasks": len(multi_annotated_tasks),
        "unique_annotators": len(unique_annotators),
        "annotators": unique_annotators,
        "field_agreements": agreements,
        "annotator_pairs": annotator_pairs,
        "overall_agreement": np.mean([metrics["mean_agreement"] for metrics in agreements.values()]) if agreements else 0
    }

@router.get("/")
async def list_annotation_projects():
    """List available Label Studio annotation projects."""
    return {
        "available_projects": [
            {
                "id": 75,
                "name": "Faculty Project",
                "description": "Faculty annotation project",
                "env_var": "FACULTY_PROJECT_ID"
            },
            {
                "id": int(DEPARTMENT_PROJECT_ID) if DEPARTMENT_PROJECT_ID else None,
                "name": "Department Project",
                "description": "Department annotation project",
                "env_var": "DEPARTMENT_PROJECT_ID"
            }
        ],
        "configuration": {
            "label_studio_url": LABEL_STUDIO_URL,
            "api_key_configured": bool(LABEL_STUDIO_API_KEY),
            "faculty_project_id": FACULTY_PROJECT_ID,
            "department_project_id": DEPARTMENT_PROJECT_ID
        }
    }

@router.get("/projects/{project_id}/export")
async def export_project_data(
    project_id: int,
    export_type: str = Query(default="CSV", description="Export format: CSV, JSON, etc."),
    force_refresh: bool = Query(default=False, description="Force fresh export (ignore cache)"),
    timeout: int = Query(default=300, description="Export timeout in seconds")
):
    """Export Label Studio project data."""
    try:
        export_data = export_snapshot(project_id, export_type, force_refresh, timeout)

        # Create filename
        filename = f"label_studio_project_{project_id}_export.{export_type.lower()}"

        return StreamingResponse(
            io.BytesIO(export_data),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"Export failed for project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/projects/{project_id}/agreement")
async def compute_project_agreement(
    project_id: int = 75,
    export_format: str = Query(default="json", description="Response format: json or csv"),
    force_refresh: bool = Query(default=False, description="Force fresh export (ignore cache)")
):
    """
    Compute inter-annotator agreement for a Label Studio project.
    Defaults to project ID 75 as specified.
    """
    try:
        # Export data from Label Studio
        export_data = export_snapshot(project_id, "CSV", force_refresh)

        # Convert to pandas DataFrame
        df = pd.read_csv(io.BytesIO(export_data))

        # Enrich with user information (email, username)
        df = enrich_annotator_data(df)

        # Compute agreement metrics
        agreement_results = compute_inter_annotator_agreement(df)

        if export_format.lower() == "csv":
            # Convert agreement results to CSV format
            if "field_agreements" in agreement_results:
                # Create a CSV-friendly format
                csv_data = []
                for field, metrics in agreement_results["field_agreements"].items():
                    csv_data.append({
                        "field": field,
                        "mean_agreement": metrics["mean_agreement"],
                        "std_agreement": metrics["std_agreement"],
                        "min_agreement": metrics["min_agreement"],
                        "max_agreement": metrics["max_agreement"],
                        "num_tasks": metrics["num_tasks"]
                    })

                df_results = pd.DataFrame(csv_data)

                # Convert to CSV bytes
                buffer = io.StringIO()
                df_results.to_csv(buffer, index=False)
                csv_bytes = buffer.getvalue().encode('utf-8')

                return StreamingResponse(
                    io.BytesIO(csv_bytes),
                    media_type="text/csv",
                    headers={"Content-Disposition": f"attachment; filename=project_{project_id}_agreement.csv"}
                )

        # Return JSON format by default
        return {
            "project_id": project_id,
            "agreement_analysis": agreement_results,
            "export_info": {
                "total_rows": len(df),
                "columns": list(df.columns)
            }
        }

    except Exception as e:
        logger.error(f"Agreement computation failed for project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agreement computation failed: {str(e)}")

@router.get("/projects/{project_id}/data")
async def get_project_data(
    project_id: int,
    format: str = Query(default="json", description="Data format: json, csv, or parquet"),
    force_refresh: bool = Query(default=False, description="Force fresh export (ignore cache)")
):
    """Get Label Studio project data in various formats."""
    try:
        # Export data from Label Studio
        export_data = export_snapshot(project_id, "CSV", force_refresh)

        # Convert to pandas DataFrame
        df = pd.read_csv(io.BytesIO(export_data))

        if format.lower() == "csv":
            return StreamingResponse(
                io.BytesIO(export_data),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=project_{project_id}_data.csv"}
            )

        elif format.lower() == "parquet":
            # Convert to parquet
            buffer = io.BytesIO()
            df.to_parquet(buffer, index=False, engine="pyarrow")
            buffer.seek(0)
            parquet_bytes = buffer.read()

            return StreamingResponse(
                io.BytesIO(parquet_bytes),
                media_type="application/octet-stream",
                headers={"Content-Disposition": f"attachment; filename=project_{project_id}_data.parquet"}
            )

        else:  # JSON format
            return {
                "project_id": project_id,
                "data": df.to_dict('records'),
                "metadata": {
                    "total_rows": len(df),
                    "columns": list(df.columns),
                    "shape": df.shape
                }
            }

    except Exception as e:
        logger.error(f"Data retrieval failed for project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data retrieval failed: {str(e)}")

# Admin-only endpoints
@admin_router.get("/projects/{project_id}/stats")
async def get_project_statistics(
    project_id: int,
    force_refresh: bool = Query(default=False, description="Force fresh export (ignore cache)"),
    _: User = Depends(get_admin_user)
):
    """Get detailed statistics for a Label Studio project (admin only)."""
    try:
        export_data = export_snapshot(project_id, "CSV", force_refresh)
        df = pd.read_csv(io.BytesIO(export_data))

        # Compute comprehensive statistics
        stats = {
            "project_id": project_id,
            "total_annotations": len(df),
            "unique_tasks": df['task'].nunique() if 'task' in df.columns else 0,
            "unique_annotators": df['user'].nunique() if 'user' in df.columns else 0,
            "data_shape": df.shape,
            "columns": list(df.columns),
            "missing_data": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.astype(str).to_dict()
        }

        # Add annotator-specific stats
        if 'user' in df.columns:
            annotator_stats = df.groupby('user').agg({
                'task': 'count'
            }).rename(columns={'task': 'annotations_count'})
            stats["annotator_stats"] = annotator_stats.to_dict('index')

        # Add task completion stats
        if 'task' in df.columns:
            task_stats = df.groupby('task').agg({
                'user': 'count'
            }).rename(columns={'user': 'annotators_count'})
            stats["task_completion_distribution"] = task_stats['annotators_count'].value_counts().to_dict()

        return stats

    except Exception as e:
        logger.error(f"Statistics computation failed for project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Statistics computation failed: {str(e)}")