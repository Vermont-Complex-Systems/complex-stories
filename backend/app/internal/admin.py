from fastapi import APIRouter, Depends

from ..dependencies import get_token_header

router = APIRouter(
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def update_admin():
    return {"message": "Admin getting schwifty"}


@router.get("/pipeline-status")
async def get_pipeline_status():
    """Get status of all data pipelines."""
    return {
        "pipelines": {
            "open_academic_analytics": {"status": "running", "last_run": "2025-01-15T10:30:00Z"},
            "data_luminosity": {"status": "idle", "last_run": "2025-01-14T22:15:00Z"}
        }
    }


@router.post("/pipeline/{pipeline_name}/trigger")
async def trigger_pipeline(pipeline_name: str):
    """Trigger a specific data pipeline."""
    valid_pipelines = ["open_academic_analytics", "data_luminosity"]
    if pipeline_name not in valid_pipelines:
        return {"error": f"Unknown pipeline: {pipeline_name}"}

    return {"message": f"Pipeline {pipeline_name} triggered", "status": "queued"}