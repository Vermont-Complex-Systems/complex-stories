# FastAPI Patterns Reference

Complete reference for FastAPI patterns used in Complex Stories.

## Table of Contents

1. [Request Validation](#request-validation)
2. [Response Models](#response-models)
3. [Query Parameters](#query-parameters)
4. [Path Parameters](#path-parameters)
5. [Request Bodies](#request-bodies)
6. [Dependencies](#dependencies)
7. [Background Tasks](#background-tasks)
8. [WebSockets](#websockets)
9. [Middleware](#middleware)
10. [Exception Handling](#exception-handling)

---

## Request Validation {#request-validation}

### Basic Pydantic Model

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=8)
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric')
        return v.lower()

    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v):
        return v.lower()
```

### Field Constraints

```python
from pydantic import Field, constr, conint, confloat

class Product(BaseModel):
    # String constraints
    name: str = Field(..., min_length=1, max_length=255)
    sku: constr(pattern=r'^[A-Z]{3}-\d{4}$')  # Pattern: ABC-1234

    # Numeric constraints
    price: float = Field(..., gt=0, le=10000)  # 0 < price <= 10000
    quantity: conint(ge=0)  # >= 0
    discount: confloat(ge=0, le=1)  # 0 <= discount <= 1

    # Enums
    status: str = Field(..., pattern='^(active|inactive|pending)$')
```

### Nested Models

```python
class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str = Field(..., pattern=r'^\d{5}$')

class UserWithAddress(BaseModel):
    username: str
    email: str
    address: Address  # Nested model
    addresses: List[Address] = []  # List of nested models
```

### Model Config

```python
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        # Convert SQLAlchemy models to Pydantic
        from_attributes = True

        # Example data for docs
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "johndoe",
                "email": "john@example.com",
                "created_at": "2024-01-01T00:00:00"
            }
        }
```

---

## Response Models {#response-models}

### Basic Response Model

```python
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db_session)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user  # Automatically converted to UserResponse
```

### Multiple Response Models

```python
from fastapi import status

@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid input"},
        409: {"description": "User already exists"}
    }
)
async def create_user(user: UserCreate):
    # ...
    return new_user
```

### Response Model Customization

```python
# Exclude fields from response
@router.get("/users", response_model=List[UserResponse], response_model_exclude={"password_hash"})

# Include only specific fields
@router.get("/users", response_model=List[UserResponse], response_model_include={"id", "username"})

# Exclude None values
@router.get("/users", response_model=UserResponse, response_model_exclude_none=True)
```

### Union Response Types

```python
from typing import Union

class SuccessResponse(BaseModel):
    success: bool = True
    data: dict

class ErrorResponse(BaseModel):
    success: bool = False
    error: str

@router.post("/action", response_model=Union[SuccessResponse, ErrorResponse])
async def perform_action():
    if condition:
        return SuccessResponse(data={"result": "ok"})
    else:
        return ErrorResponse(error="Something went wrong")
```

---

## Query Parameters {#query-parameters}

### Basic Query Parameters

```python
from fastapi import Query

@router.get("/items")
async def list_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max items to return"),
    search: Optional[str] = Query(None, min_length=3, max_length=50),
    sort_by: str = Query("created_at", pattern="^(created_at|name|price)$"),
    order: str = Query("desc", pattern="^(asc|desc)$")
):
    # Use parameters
    pass
```

### Required vs Optional

```python
# Required (no default, or use ...)
@router.get("/search")
async def search(
    q: str = Query(..., min_length=1),  # Required
    category: str  # Also required (no default)
):
    pass

# Optional (with default)
@router.get("/filter")
async def filter_items(
    status: Optional[str] = Query(None),  # Optional, defaults to None
    limit: int = Query(10)  # Optional, defaults to 10
):
    pass
```

### List Query Parameters

```python
@router.get("/items")
async def filter_by_tags(
    tags: List[str] = Query([])  # /items?tags=a&tags=b&tags=c
):
    # tags will be ['a', 'b', 'c']
    pass

# Or with default
@router.get("/items")
async def filter_by_status(
    statuses: List[str] = Query(["active", "pending"])
):
    pass
```

### Query Parameter Aliases

```python
@router.get("/items")
async def get_items(
    item_id: Optional[str] = Query(None, alias="item-id")  # Accept "item-id" in URL
):
    # /items?item-id=123
    pass
```

---

## Path Parameters {#path-parameters}

### Basic Path Parameters

```python
@router.get("/users/{user_id}")
async def get_user(user_id: int):  # Auto-validates as int
    pass

@router.get("/posts/{post_slug}")
async def get_post(post_slug: str):
    pass
```

### Path Parameter Validation

```python
from fastapi import Path

@router.get("/items/{item_id}")
async def get_item(
    item_id: int = Path(..., gt=0, description="The ID of the item")
):
    pass

@router.get("/users/{username}")
async def get_user(
    username: str = Path(..., min_length=3, max_length=50, pattern="^[a-z0-9_]+$")
):
    pass
```

### Multiple Path Parameters

```python
@router.get("/orgs/{org_id}/projects/{project_id}")
async def get_project(
    org_id: int = Path(..., gt=0),
    project_id: int = Path(..., gt=0)
):
    pass
```

---

## Request Bodies {#request-bodies}

### Single Body Model

```python
@router.post("/users")
async def create_user(user: UserCreate):
    # user is validated Pydantic model
    pass
```

### Multiple Body Parameters

```python
@router.post("/items")
async def create_item(
    item: ItemCreate,
    user: User = Depends(get_current_user),
    importance: int = Body(..., ge=1, le=5)
):
    pass
```

### Embedded Body

```python
from fastapi import Body

@router.post("/items")
async def create_item(
    item: ItemCreate = Body(..., embed=True)
):
    # Expected JSON: {"item": {"name": "...", "price": ...}}
    pass
```

### Raw JSON Body

```python
@router.post("/webhook")
async def webhook(data: dict):
    # Accepts any JSON object
    pass
```

### Form Data

```python
from fastapi import Form

@router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    pass
```

### File Upload

```python
from fastapi import File, UploadFile

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...)
):
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }

# Multiple files
@router.post("/upload-multiple")
async def upload_multiple(
    files: List[UploadFile] = File(...)
):
    return [{"filename": f.filename} for f in files]
```

---

## Dependencies {#dependencies}

### Basic Dependency

```python
async def get_db_session() -> AsyncSession:
    async with async_session() as session:
        yield session

@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_db_session)):
    # db is injected
    pass
```

### Dependency with Parameters

```python
def pagination_params(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    return {"skip": skip, "limit": limit}

@router.get("/items")
async def list_items(pagination: dict = Depends(pagination_params)):
    # Use pagination["skip"] and pagination["limit"]
    pass
```

### Class-Based Dependencies

```python
class PaginationParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100)
    ):
        self.skip = skip
        self.limit = limit

@router.get("/items")
async def list_items(pagination: PaginationParams = Depends()):
    # Use pagination.skip and pagination.limit
    pass
```

### Nested Dependencies

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session)  # Nested dependency
):
    # Validate token, fetch user
    return user

@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user)  # Uses nested deps
):
    return current_user
```

### Global Dependencies

```python
# Apply to all routes in router
router = APIRouter(dependencies=[Depends(verify_api_key)])

# Apply to entire app
app = FastAPI(dependencies=[Depends(verify_api_key)])
```

---

## Background Tasks {#background-tasks}

### Basic Background Task

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Slow operation
    time.sleep(10)
    print(f"Sending email to {email}: {message}")

@router.post("/send-notification")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "Welcome!")
    return {"message": "Notification will be sent in background"}
```

### Multiple Background Tasks

```python
@router.post("/register")
async def register_user(
    user: UserCreate,
    background_tasks: BackgroundTasks
):
    # Create user immediately
    new_user = await create_user_in_db(user)

    # Queue background tasks
    background_tasks.add_task(send_welcome_email, user.email)
    background_tasks.add_task(log_registration, user.username)
    background_tasks.add_task(update_analytics, "new_user")

    return {"user": new_user, "message": "Account created"}
```

---

## WebSockets {#websockets}

### Basic WebSocket

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
```

### WebSocket with Authentication

```python
@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    # Validate token
    user = await verify_token(token)
    if not user:
        await websocket.close(code=1008)  # Policy violation
        return

    await websocket.accept()
    # ...
```

---

## Middleware {#middleware}

### Custom Middleware

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"{request.method} {request.url}")
        response = await call_next(request)
        print(f"Status: {response.status_code}")
        return response

app.add_middleware(LoggingMiddleware)
```

### CORS Middleware

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### GZip Middleware

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress > 1KB
```

---

## Exception Handling {#exception-handling}

### Custom Exception Handler

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class CustomException(Exception):
    def __init__(self, detail: str):
        self.detail = detail

@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=418,
        content={"message": "Custom error", "detail": exc.detail}
    )

# Use in route
@router.get("/test")
async def test():
    raise CustomException("Something went wrong")
```

### Override Default Handlers

```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)
```

---

## Advanced Patterns

### Conditional Response Models

```python
@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    include_private: bool = False,
    current_user: User = Depends(get_current_user)
):
    user = await fetch_user(user_id)

    if include_private and current_user.is_admin:
        return UserPrivateResponse(**user.dict())
    else:
        return UserPublicResponse(**user.dict())
```

### Dynamic Path Operations

```python
# Add route programmatically
def create_crud_routes(model: Type[Base], router: APIRouter):
    @router.get(f"/{model.__tablename__}")
    async def list_items(db: AsyncSession = Depends(get_db_session)):
        return await db.execute(select(model))

    @router.post(f"/{model.__tablename__}")
    async def create_item(item: dict):
        # ...
        pass

# Use
create_crud_routes(User, router)
create_crud_routes(Post, router)
```

---

This covers all common FastAPI patterns. For Complex Stories-specific patterns, refer to the backend-api SKILL.md.
