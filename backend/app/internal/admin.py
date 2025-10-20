from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from ..core.database import get_db_session
from ..core.auth import get_password_hash
from ..models.auth import User
from ..routers.auth import get_admin_user

router = APIRouter(
    dependencies=[Depends(get_admin_user)],
    responses={404: {"description": "Not found"}},
)

class AdminUserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


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


# ================================
# User Management
# ================================

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: AdminUserCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new user (admin only)."""
    # Validate role
    valid_roles = ["admin", "annotator", "faculty"]
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )

    # Check if username already exists
    query = select(User).where(User.username == user_data.username)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role,
        is_active=True
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user