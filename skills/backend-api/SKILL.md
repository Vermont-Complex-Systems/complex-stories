---
name: backend-api
description: Build FastAPI endpoints for Complex Stories with authentication, validation, and CRUD operations. Use when tasks involve creating new API routes, adding authentication/authorization, building CRUD endpoints, implementing request validation, handling file uploads/downloads, or adding rate limiting. NOT for data pipelines (use data-engineering skill instead). Also use for questions about FastAPI patterns, JWT auth, Pydantic validation, or API architecture.
---

# Backend API Design for Complex Stories

This skill guides creation of FastAPI endpoints following Complex Stories API patterns: authentication, validation, CRUD operations, and response formatting.

## Skill Separation

**This skill (backend-api):**
- ✅ Creating API routers and endpoints
- ✅ Authentication and authorization (JWT, RBAC)
- ✅ Request validation (Pydantic schemas)
- ✅ CRUD operations (read, create, update, delete)
- ✅ File uploads/downloads
- ✅ Rate limiting
- ✅ Error handling

**Use data-engineering skill for:**
- ❌ Dagster pipelines (extract, transform, export)
- ❌ DuckDB processing
- ❌ Bulk data uploads (10k+ records)
- ❌ ETL workflows

## Architecture Overview

**API Stack:**
- **FastAPI**: Async web framework with auto-docs
- **SQLAlchemy 2.0+**: Async ORM with PostgreSQL
- **Pydantic**: Request/response validation
- **JWT**: Token-based authentication
- **SlowAPI**: Rate limiting middleware
- **Argon2**: Password hashing

**URL Structure:**
- Public endpoints: `/project-name/resource`
- Admin endpoints: `/admin/project-name/resource`
- Auth endpoints: `/auth/*` (hidden from docs)

## Quick Reference

### File Locations
```
backend/app/
├── main.py                    # App setup, middleware, routers
├── core/
│   ├── auth.py                # JWT, password hashing, RBAC
│   ├── config.py              # Settings (env vars)
│   └── database.py            # DB connections, session factory
├── models/
│   └── [domain].py            # SQLAlchemy models
└── routers/
    └── [project-name].py      # API endpoints
```

### Common Imports
```python
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from pydantic import BaseModel, Field
from typing import Optional, List
from app.core.database import get_db_session
from app.core.auth import get_current_active_user, get_admin_user
from app.models.domain import Model
from ..main import limiter
```

## Creating a New API Router

### 1. Define SQLAlchemy Model

**File:** `backend/app/models/my_domain.py`

```python
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class MyResource(Base):
    __tablename__ = "my_resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String)
    status = Column(String(50), default="active")
    created_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
```

### 2. Define Pydantic Schemas

**File:** `backend/app/routers/my_project.py`

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Request schema (POST/PUT)
class ResourceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = Field("active", pattern="^(active|inactive|pending)$")

class ResourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|pending)$")

# Response schema (GET)
class ResourceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str
    created_by: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True  # Enables SQLAlchemy model conversion
```

### 3. Create Router with CRUD Endpoints

**File:** `backend/app/routers/my_project.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sql_func
from typing import List, Optional
from app.core.database import get_db_session
from app.core.auth import get_current_active_user, get_admin_user, User
from app.models.my_domain import MyResource
from ..main import limiter

# Public router
router = APIRouter(prefix="/my-project", tags=["my-project"])

# Admin router (hidden from docs)
admin_router = APIRouter(
    prefix="/admin/my-project",
    tags=["admin-my-project"],
    include_in_schema=False
)

# LIST - Public, with pagination and filtering
@router.get("/resources", response_model=List[ResourceResponse])
async def list_resources(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in name/description"),
    db: AsyncSession = Depends(get_db_session)
):
    """List all resources with optional filtering and pagination."""

    # Build query
    query = select(MyResource).where(MyResource.is_active == True)

    # Apply filters
    if status:
        query = query.where(MyResource.status == status)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            MyResource.name.ilike(search_pattern) |
            MyResource.description.ilike(search_pattern)
        )

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute
    result = await db.execute(query)
    resources = result.scalars().all()

    return resources

# GET - Public, single resource
@router.get("/resources/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a single resource by ID."""

    query = select(MyResource).where(
        MyResource.id == resource_id,
        MyResource.is_active == True
    )
    result = await db.execute(query)
    resource = result.scalar_one_or_none()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    return resource

# COUNT - Public, for pagination
@router.get("/resources/count")
async def count_resources(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """Get total count of resources (for pagination)."""

    query = select(sql_func.count(MyResource.id)).where(MyResource.is_active == True)

    if status:
        query = query.where(MyResource.status == status)

    result = await db.execute(query)
    count = result.scalar()

    return {"count": count}

# CREATE - Authenticated users only
@admin_router.post("/resources", response_model=ResourceResponse)
async def create_resource(
    resource: ResourceCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new resource (authenticated users only)."""

    # Check for duplicates
    existing_query = select(MyResource).where(MyResource.name == resource.name)
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Resource with this name already exists")

    # Create resource
    new_resource = MyResource(
        name=resource.name,
        description=resource.description,
        status=resource.status,
        created_by=current_user.username
    )

    db.add(new_resource)
    await db.commit()
    await db.refresh(new_resource)

    return new_resource

# UPDATE - Role-based access
@admin_router.put("/resources/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    resource_update: ResourceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update a resource (admins: any, others: own only)."""

    # Fetch resource
    query = select(MyResource).where(MyResource.id == resource_id)
    result = await db.execute(query)
    resource = result.scalar_one_or_none()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Role-based access control
    if current_user.role != "admin":
        # Non-admins can only edit their own resources
        if resource.created_by != current_user.username:
            raise HTTPException(
                status_code=403,
                detail="You can only edit resources you created"
            )

    # Apply updates (only non-None fields)
    update_data = resource_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)

    await db.commit()
    await db.refresh(resource)

    return resource

# DELETE - Admin only
@admin_router.delete("/resources/{resource_id}")
async def delete_resource(
    resource_id: int,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Soft delete a resource (admin only)."""

    # Fetch resource
    query = select(MyResource).where(MyResource.id == resource_id)
    result = await db.execute(query)
    resource = result.scalar_one_or_none()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Soft delete (set is_active = False)
    resource.is_active = False
    await db.commit()

    return {"message": "Resource deleted successfully"}
```

### 4. Register Router in main.py

**File:** `backend/app/main.py`

```python
from app.routers import my_project

# Include routers
app.include_router(my_project.router)
app.include_router(my_project.admin_router)
```

## Authentication Patterns

### Password-Based Authentication

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.core.auth import (
    get_password_hash,
    verify_password,
    create_access_token
)

auth_router = APIRouter(prefix="/auth", tags=["auth"], include_in_schema=False)
security = HTTPBearer()

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@auth_router.post("/login", response_model=Token)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Authenticate user and return JWT token."""

    # Fetch user
    query = select(User).where(User.username == credentials.username.lower())
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check if active
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Create token
    token = create_access_token(data={"sub": user.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }
```

### Using Authentication in Endpoints

```python
from app.core.auth import get_current_active_user, get_admin_user, User

# Any authenticated user
@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    return {"user": current_user.username, "role": current_user.role}

# Admin only
@admin_router.post("/admin-action")
async def admin_endpoint(
    current_user: User = Depends(get_admin_user)
):
    return {"message": "Admin access granted"}

# Custom role check
@router.put("/sensitive-action")
async def custom_role_check(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    # Allow admin and annotator roles
    if current_user.role not in ["admin", "annotator"]:
        raise HTTPException(
            status_code=403,
            detail="Requires admin or annotator role"
        )

    # Proceed with action
    return {"status": "success"}
```

## UPSERT Pattern (Surveys)

```python
from sqlalchemy.dialects.postgresql import insert

# Validation constants
VALID_FIELDS = {
    'consent': ['accepted', 'declined'],
    'privacy': ['private', 'mixed', 'public'],
    'preference': list(range(1, 8))  # 1-7 Likert scale
}

class SurveyUpsert(BaseModel):
    fingerprint: str = Field(..., min_length=10)
    field: str
    value: str

@router.post("/survey/upsert")
@limiter.limit("30/minute")
async def upsert_survey_answer(
    request: Request,  # Required for rate limiting
    survey_data: SurveyUpsert,
    db: AsyncSession = Depends(get_db_session)
):
    """UPSERT survey response (create or update)."""

    # Validate field
    if survey_data.field not in VALID_FIELDS:
        raise HTTPException(status_code=400, detail=f"Invalid field: {survey_data.field}")

    # Validate value
    if survey_data.value not in VALID_FIELDS[survey_data.field]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid value for {survey_data.field}"
        )

    # Check if exists
    query = select(Survey).where(Survey.fingerprint == survey_data.fingerprint)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        # UPDATE
        setattr(existing, survey_data.field, survey_data.value)
        await db.commit()
        return {"message": "Updated", "fingerprint": survey_data.fingerprint}
    else:
        # INSERT
        new_survey = Survey(
            fingerprint=survey_data.fingerprint,
            **{survey_data.field: survey_data.value}
        )
        db.add(new_survey)
        await db.commit()
        return {"message": "Created", "fingerprint": survey_data.fingerprint}

# Alternative: PostgreSQL UPSERT (more efficient)
@router.post("/survey/upsert-fast")
async def upsert_fast(
    survey_data: SurveyUpsert,
    db: AsyncSession = Depends(get_db_session)
):
    """UPSERT using PostgreSQL ON CONFLICT."""

    stmt = insert(Survey).values(
        fingerprint=survey_data.fingerprint,
        **{survey_data.field: survey_data.value}
    )

    # ON CONFLICT DO UPDATE
    stmt = stmt.on_conflict_do_update(
        index_elements=['fingerprint'],
        set_={survey_data.field: stmt.excluded[survey_data.field]}
    )

    await db.execute(stmt)
    await db.commit()

    return {"message": "Upserted"}
```

## File Upload/Download Patterns

### File Upload

```python
from fastapi import File, UploadFile
import shutil
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@admin_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_admin_user)
):
    """Upload file (admin only)."""

    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not allowed"
        )

    # Validate file size (10MB max)
    max_size = 10 * 1024 * 1024
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    # Save file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        f.write(file_content)

    return {
        "filename": file.filename,
        "size": len(file_content),
        "content_type": file.content_type
    }
```

### File Download (Parquet/CSV)

```python
from fastapi.responses import StreamingResponse
import pandas as pd
import io

@router.get("/export")
async def export_data(
    format: str = Query("json", pattern="^(json|parquet|csv)$"),
    db: AsyncSession = Depends(get_db_session)
):
    """Export data in multiple formats."""

    # Fetch data
    query = select(MyResource)
    result = await db.execute(query)
    resources = result.scalars().all()

    # Convert to dict
    data = [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "status": r.status
        }
        for r in resources
    ]

    # JSON response (default)
    if format == "json":
        return data

    # Parquet download
    elif format == "parquet":
        df = pd.DataFrame(data)
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False, engine="pyarrow")
        buffer.seek(0)

        return StreamingResponse(
            io.BytesIO(buffer.read()),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=export.parquet"
            }
        )

    # CSV download
    elif format == "csv":
        df = pd.DataFrame(data)
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)

        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=export.csv"
            }
        )
```

## Rate Limiting

```python
from ..main import limiter

# Per-IP rate limit
@router.post("/public-endpoint")
@limiter.limit("10/minute")
async def rate_limited(
    request: Request,  # REQUIRED for rate limiting
    db: AsyncSession = Depends(get_db_session)
):
    return {"message": "Rate limited to 10 requests per minute per IP"}

# Different limits for authenticated users
@router.post("/authenticated-endpoint")
@limiter.limit("100/minute")
async def higher_limit(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    return {"message": "Higher limit for authenticated users"}
```

## Error Handling Best Practices

```python
# 400 - Bad Request (client error)
if not data.is_valid():
    raise HTTPException(status_code=400, detail="Invalid data format")

# 401 - Unauthorized (authentication failed)
raise HTTPException(
    status_code=401,
    detail="Invalid credentials",
    headers={"WWW-Authenticate": "Bearer"}
)

# 403 - Forbidden (insufficient permissions)
if current_user.role != "admin":
    raise HTTPException(status_code=403, detail="Admin access required")

# 404 - Not Found
if not resource:
    raise HTTPException(status_code=404, detail="Resource not found")

# 409 - Conflict (duplicate)
if existing_resource:
    raise HTTPException(status_code=409, detail="Resource already exists")

# 500 - Internal Server Error
try:
    await db.commit()
except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")
```

## Database Transaction Patterns

```python
# Auto-commit with error handling
try:
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record
except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=500, detail=str(e))

# Manual transaction control
async with db.begin():
    # Operations within transaction
    db.add(record1)
    db.add(record2)
    # Auto-commits on exit, rolls back on exception

# Explicit rollback
try:
    await db.commit()
except IntegrityError:
    await db.rollback()
    raise HTTPException(status_code=409, detail="Duplicate record")
```

## Query Optimization Patterns

```python
# Pagination with count (efficient)
from sqlalchemy import func as sql_func

@router.get("/resources/paginated")
async def paginated_list(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session)
):
    # Calculate offset
    offset = (page - 1) * per_page

    # Get total count
    count_query = select(sql_func.count(MyResource.id))
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Get page data
    query = select(MyResource).offset(offset).limit(per_page)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": (total + per_page - 1) // per_page
    }

# Eager loading relationships (avoid N+1 queries)
from sqlalchemy.orm import selectinload

query = select(Parent).options(
    selectinload(Parent.children)
)
```

## Best Practices

1. **Router Organization**: One router per domain/project, separate public/admin
2. **Response Models**: Always define Pydantic schemas for consistent responses
3. **Validation**: Use Pydantic Field() with constraints, validate at API boundary
4. **Authentication**: Use dependency injection, never bypass RBAC checks
5. **Rate Limiting**: Apply to all public/survey endpoints
6. **Transactions**: Always commit explicitly, rollback on errors
7. **Status Codes**: Use appropriate codes (200, 400, 401, 403, 404, 500)
8. **Pagination**: Implement skip/limit for large datasets
9. **Query Params**: Use Query() with descriptions for auto-docs
10. **Soft Deletes**: Prefer is_active flag over hard deletes

## Common Issues

**Missing request parameter for rate limiting:**
```python
# ❌ Bad - missing request
@limiter.limit("10/minute")
async def endpoint():
    pass

# ✅ Good
@limiter.limit("10/minute")
async def endpoint(request: Request):
    pass
```

**Forgot to commit transaction:**
```python
# ❌ Bad - no commit
db.add(record)
return record

# ✅ Good
db.add(record)
await db.commit()
await db.refresh(record)
return record
```

**Not using async session:**
```python
# ❌ Bad - sync session
db.query(Model).all()

# ✅ Good
result = await db.execute(select(Model))
models = result.scalars().all()
```

## Reference Examples

Study these complete routers:
- **auth.py**: JWT authentication, user registration
- **dark_data_survey.py**: UPSERT pattern with validation
- **datasets.py**: CRUD with RBAC, file exports
- **annotations.py**: File downloads, streaming responses

For data pipelines and bulk uploads, see the **data-engineering** skill.
