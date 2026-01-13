---
name: data-engineering
description: Build ETL data pipelines for Complex Stories using Dagster, DuckDB, PostgreSQL, and FastAPI. Use when tasks involve creating data pipelines, processing external API data, setting up incremental sync patterns, bulk uploads to PostgreSQL, or exposing data through FastAPI endpoints. Also use for questions about the data engineering architecture, database schema design, or pipeline patterns.
---

# Data Engineering for Complex Stories

This skill guides creation of data pipelines following the Complex Stories platform's ETL patterns: External APIs → DuckDB (Processing) → PostgreSQL (Storage) → FastAPI (Access).

## Architecture Overview

**Pipeline Flow:**
1. **Extract**: Fetch from external APIs (OpenAlex, Semantic Scholar, etc.)
2. **Transform**: Process and normalize in DuckDB with SQL/pandas
3. **Export**: Bulk upload to PostgreSQL via FastAPI
4. **Access**: Query via FastAPI endpoints

**Technologies:**
- **Dagster 1.11.12**: Pipeline orchestration
- **DuckDB**: High-performance analytical processing (local `~/[project].duckdb`)
- **PostgreSQL**: Production data storage with async SQLAlchemy
- **FastAPI**: RESTful API with role-based auth

## Quick Reference

### File Locations
```
backend/
├── projects/[project-name]/           # Dagster pipeline project
│   ├── pyproject.toml                 # Dependencies
│   └── src/[project-name]/
│       └── defs/
│           ├── extract/               # API fetching assets
│           ├── transform/             # DuckDB transformations
│           ├── export/                # PostgreSQL bulk uploads
│           └── resources.py           # Dagster resources
├── app/
│   ├── models/[domain].py             # SQLAlchemy models
│   └── routers/[project-name].py      # FastAPI endpoints
└── shared/shared/clients/             # Reusable API clients
```

### Database Schemas
**DuckDB** (processing):
```
[project].raw.*        - Raw API data
[project].cache.*      - Performance caching
[project].transform.*  - Processed data
```

**PostgreSQL** (production): Flat tables matching SQLAlchemy models

## Creating a New Pipeline

### 1. Initialize Dagster Project

Create project structure in `backend/projects/[project-name]/`:

```bash
cd backend/projects
mkdir -p [project-name]/src/[project-name]/defs/{extract,transform,export}
```

**Create `pyproject.toml`:**
```toml
[project]
name = "project-name"
version = "0.1.0"
dependencies = [
    "dagster>=1.11.12",
    "duckdb>=1.1.3",
    "pandas>=2.0.0",
]

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
```

**Register in workspace** (`backend/dg.toml`):
```toml
[[workspace]]
module = "project_name.defs"
location = "projects/project-name"
```

### 2. Define Resources

**File:** `backend/projects/[project-name]/src/[project-name]/defs/resources.py`

```python
from dagster import ConfigurableResource
import duckdb
from pathlib import Path

class InitDuckDBResource(ConfigurableResource):
    """Initialize DuckDB with project schemas"""

    db_path: str = str(Path.home() / "project.duckdb")

    def setup_for_execution(self, context) -> None:
        conn = duckdb.connect(self.db_path)
        conn.execute("CREATE SCHEMA IF NOT EXISTS project")
        conn.execute("CREATE SCHEMA IF NOT EXISTS project.raw")
        conn.execute("CREATE SCHEMA IF NOT EXISTS project.cache")
        conn.execute("CREATE SCHEMA IF NOT EXISTS project.transform")
        conn.close()

class DuckDBResource(ConfigurableResource):
    """DuckDB connection for assets"""

    db_path: str = str(Path.home() / "project.duckdb")

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(self.db_path)
```

### 3. Extract Assets (API → DuckDB)

**File:** `backend/projects/[project-name]/src/[project-name]/defs/extract/fetch_data.py`

```python
from dagster import asset, AssetExecutionContext, DagsterEventType
from typing import Optional

@asset(
    key_prefix=["project"],
    compute_kind="duckdb",
    group_name="import"
)
def raw_data(
    context: AssetExecutionContext,
    duckdb_resource: DuckDBResource,
    api_client: ExternalAPIResource
) -> Optional[DagsterEventType]:
    """Fetch data from external API and store in DuckDB"""

    conn = duckdb_resource.get_connection()

    # Create raw table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS project.raw.data (
            id VARCHAR PRIMARY KEY,
            field1 VARCHAR,
            field2 INTEGER,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Fetch from API
    records = api_client.fetch_all()
    context.log.info(f"Fetched {len(records)} records")

    # Insert into DuckDB
    conn.executemany(
        "INSERT OR REPLACE INTO project.raw.data (id, field1, field2) VALUES (?, ?, ?)",
        [(r['id'], r['field1'], r['field2']) for r in records]
    )

    conn.close()
    context.log.info("Data successfully loaded")
```

**Incremental Sync Pattern** (see [open-academic-analytics/extract/uvm_publications.py](../../backend/projects/open-academic-analytics/src/open_academic_analytics/defs/extract/uvm_publications.py)):

```python
# Track sync status per entity
conn.execute("""
    CREATE TABLE IF NOT EXISTS project.cache.sync_status (
        entity_id VARCHAR PRIMARY KEY,
        last_synced_date TIMESTAMP,
        last_data_update TIMESTAMP
    )
""")

# Fetch only new data
status = conn.execute("""
    SELECT last_synced_date, last_data_update
    FROM project.cache.sync_status
    WHERE entity_id = ?
""", [entity_id]).fetchone()

if status:
    fetch_from = max(status[0], ground_truth_start)
else:
    fetch_from = ground_truth_start
```

### 4. Transform Assets (DuckDB SQL/pandas)

**File:** `backend/projects/[project-name]/src/[project-name]/defs/transform/process_data.py`

```python
from dagster import asset, AssetExecutionContext

@asset(
    key_prefix=["project"],
    deps=["project/raw_data"],  # Explicit dependency
    compute_kind="duckdb",
    group_name="transform"
)
def processed_data(
    context: AssetExecutionContext,
    duckdb_resource: DuckDBResource
) -> None:
    """Transform raw data with SQL aggregations"""

    conn = duckdb_resource.get_connection()

    conn.execute("""
        CREATE OR REPLACE TABLE project.transform.processed_data AS
        SELECT
            id,
            field1,
            COUNT(*) as count,
            AVG(field2) as avg_field2,
            MAX(field2) as max_field2
        FROM project.raw.data
        WHERE field2 > 0
        GROUP BY id, field1
    """)

    row_count = conn.execute(
        "SELECT COUNT(*) FROM project.transform.processed_data"
    ).fetchone()[0]

    context.log.info(f"Processed {row_count} records")
    conn.close()
```

### 5. Export Assets (DuckDB → PostgreSQL)

**File:** `backend/projects/[project-name]/src/[project-name]/defs/export/upload_data.py`

```python
from dagster import asset, AssetExecutionContext
import pandas as pd

@asset(
    key_prefix=["project"],
    deps=["project/processed_data"],
    compute_kind="api",
    group_name="export"
)
def export_to_postgres(
    context: AssetExecutionContext,
    duckdb_resource: DuckDBResource,
    api_client: ComplexStoriesAPIClient
) -> None:
    """Export transformed data to PostgreSQL via FastAPI"""

    conn = duckdb_resource.get_connection()

    # Query transformed data
    df = conn.execute("""
        SELECT
            id,
            field1,
            count,
            avg_field2,
            max_field2
        FROM project.transform.processed_data
    """).df()

    # Pandas transformations
    df['field1_clean'] = df['field1'].str.strip().str.lower()
    df['created_at'] = pd.Timestamp.now()

    # Convert dates for API compatibility
    for col in df.select_dtypes(include=['datetime64']).columns:
        df[col] = df[col].dt.strftime('%Y-%m-%dT%H:%M:%S')

    # Bulk upload
    records = df.to_dict('records')
    context.log.info(f"Uploading {len(records)} records")

    api_client.bulk_upload(
        endpoint="project-name/data/bulk",
        data=records,
        batch_size=10000
    )

    conn.close()
```

### 6. Define Dagster Definitions

**File:** `backend/projects/[project-name]/src/[project-name]/defs/__init__.py`

```python
from dagster import Definitions, load_assets_from_modules
from . import extract, transform, export
from .resources import DuckDBResource, InitDuckDBResource

# Load all assets
extract_assets = load_assets_from_modules([extract])
transform_assets = load_assets_from_modules([transform])
export_assets = load_assets_from_modules([export])

defs = Definitions(
    assets=[*extract_assets, *transform_assets, *export_assets],
    resources={
        "duckdb_init": InitDuckDBResource(),
        "duckdb_resource": DuckDBResource(),
    }
)
```

### 7. Create Database Models

**File:** `backend/app/models/[domain].py`

```python
from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class ProjectData(Base):
    __tablename__ = "project_data"

    id = Column(String, primary_key=True)
    field1_clean = Column(String, nullable=False)
    count = Column(Integer)
    avg_field2 = Column(Float)
    max_field2 = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### 8. Create FastAPI Endpoints

**File:** `backend/app/routers/[project-name].py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from typing import List
from app.core.database import get_db
from app.models.domain import ProjectData
from app.core.auth import require_role

router = APIRouter(prefix="/project-name", tags=["project-name"])

# Public read endpoint
@router.get("/data/{id}")
async def get_data(id: str, db: AsyncSession = Depends(get_db)):
    """Fetch data by ID"""
    result = await db.execute(
        select(ProjectData).where(ProjectData.id == id)
    )
    data = result.scalar_one_or_none()
    if not data:
        raise HTTPException(status_code=404, detail="Data not found")
    return data

# Admin bulk upload endpoint
@router.post("/admin/data/bulk", dependencies=[Depends(require_role("admin"))])
async def bulk_upload(records: List[dict], db: AsyncSession = Depends(get_db)):
    """Bulk upload with UPSERT (admin only)"""

    if not records:
        return {"status": "success", "inserted": 0}

    # PostgreSQL UPSERT
    stmt = insert(ProjectData)
    stmt = stmt.on_conflict_do_update(
        index_elements=['id'],
        set_={col.name: stmt.excluded[col.name]
              for col in ProjectData.__table__.columns
              if col.name != 'id'}
    )

    await db.execute(stmt, records)
    await db.commit()

    return {"status": "success", "inserted": len(records)}
```

**Register router** in `backend/app/main.py`:
```python
from app.routers import project_name
app.include_router(project_name.router)
```

## Common Patterns

### Incremental Sync with Ground Truth
Track sync status per entity and only fetch new data:
- Store `last_synced_date` and `last_data_update` in cache table
- Compare against ground truth (manually curated start dates)
- Fetch from `max(last_synced, ground_truth_start)`

**Reference:** [open-academic-analytics/extract/uvm_publications.py](../../backend/projects/open-academic-analytics/src/open_academic_analytics/defs/extract/uvm_publications.py)

### External Entity Caching
Pre-fetch metadata for external entities to avoid repeated API calls:
- Identify all external references in main dataset
- Batch fetch metadata using API aggregation endpoints
- Cache results in DuckDB with fetch success tracking

**Reference:** [open-academic-analytics/extract/coauthor_cache.py](../../backend/projects/open-academic-analytics/src/open_academic_analytics/defs/extract/coauthor_cache.py)

### DuckDB → Pandas → API Pipeline
Combine SQL and pandas for complex transformations:
1. Use DuckDB for joins, aggregations, window functions
2. Use pandas for flexible transformations (string cleaning, date formatting)
3. Bulk upload via API client with batching

**Reference:** [open-academic-analytics/export/paper.py](../../backend/projects/open-academic-analytics/src/open_academic_analytics/defs/export/paper.py)

### Privacy-Preserving Exports
Add noise to sensitive temporal data:
```sql
-- Jitter dates by 1-28 days
publication_date::DATE + INTERVAL (FLOOR(RANDOM() * 28) + 1) DAYS
```

**Reference:** [open-academic-analytics/export/coauthor.py](../../backend/projects/open-academic-analytics/src/open_academic_analytics/defs/export/coauthor.py)

### Composite Primary Keys
Support multiple perspectives on the same entity:
```python
class Paper(Base):
    id = Column(String, primary_key=True)         # Paper ID
    ego_author_id = Column(String, primary_key=True)  # Viewer perspective
```

Same paper appears once per relevant author.

### UPSERT Operations
Use PostgreSQL's `ON CONFLICT` for idempotent bulk uploads:
```python
from sqlalchemy.dialects.postgresql import insert

stmt = insert(Model)
stmt = stmt.on_conflict_do_update(
    index_elements=['id'],  # Primary key columns
    set_={col.name: stmt.excluded[col.name] for col in Model.__table__.columns}
)
await db.execute(stmt, records)
```

## API Client Patterns

### Rate Limiting
Implement thread-safe rate limiting for external APIs:

```python
from threading import Lock
from time import sleep, time

class RateLimitedAPIClient:
    def __init__(self, per_second: int, per_day: int):
        self.per_second = per_second
        self.per_day = per_day
        self.lock = Lock()
        self.requests_this_second = 0
        self.requests_today = 0
        self.current_second = int(time())

    def request(self, url: str):
        with self.lock:
            now = int(time())
            if now > self.current_second:
                self.requests_this_second = 0
                self.current_second = now

            if self.requests_this_second >= self.per_second:
                sleep(1)
                self.requests_this_second = 0
                self.current_second = int(time())

            self.requests_this_second += 1
            self.requests_today += 1

        response = requests.get(url)
        if response.status_code == 429:
            sleep(60)  # Back off on rate limit
            return self.request(url)  # Retry

        return response.json()
```

**Reference:** [shared/clients/openalex.py](../../backend/shared/shared/clients/openalex.py)

### Bulk Upload Client
Create reusable API client for bulk operations:

```python
from typing import List, Dict, Any
import requests

class ComplexStoriesAPIClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:3001"):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def bulk_upload(
        self,
        endpoint: str,
        data: List[Dict[str, Any]],
        batch_size: int = 10000
    ):
        """Upload data in batches"""
        total = len(data)
        for i in range(0, total, batch_size):
            batch = data[i:i + batch_size]
            response = requests.post(
                f"{self.base_url}/admin/{endpoint}",
                json=batch,
                headers=self.headers
            )
            response.raise_for_status()
            print(f"Uploaded {i + len(batch)}/{total}")
```

**Reference:** [shared/clients/complex_stories_api.py](../../backend/shared/shared/clients/complex_stories_api.py)

## Running Pipelines

### Local Development
```bash
cd backend
uv run dg dev  # Start Dagster webserver (typically port 3333)
```

Navigate to UI and materialize assets.

### Command Line
```bash
cd backend
uv run dagster asset materialize -m project_name.defs --select "project/*"
```

### Selective Materialization
```bash
# Materialize specific asset group
uv run dagster asset materialize -m project_name.defs --select "tag:group_name=import"

# Materialize single asset
uv run dagster asset materialize -m project_name.defs --select "project/raw_data"
```

## Best Practices

1. **Schema Organization**: Use DuckDB schemas (`raw`, `cache`, `transform`) for clear data lineage
2. **Incremental Processing**: Track sync status to avoid re-fetching data
3. **Rate Limiting**: Respect external API limits with thread-safe tracking
4. **Batching**: Use bulk uploads (10k records) for efficiency
5. **Type Safety**: Use Valibot schemas for remote function validation
6. **Idempotency**: Use UPSERT for all uploads to support reruns
7. **Privacy**: Add noise to sensitive temporal data before export
8. **Dependencies**: Use `deps=[]` for explicit asset lineage
9. **Logging**: Log record counts at each stage for observability
10. **Error Handling**: Catch API errors and implement retry logic

## Common Issues

**DuckDB locked**: Close connections after use with `conn.close()`

**PostgreSQL connection pool exhausted**: Increase `pool_size` in `database.py`

**API rate limits**: Add exponential backoff and respect 429 responses

**Date format errors**: Convert datetime to ISO strings before API upload

**Memory issues**: Use batching for large datasets (10k-100k rows per batch)

## Reference Projects

Study these complete examples:
- **open-academic-analytics**: Full pipeline from OpenAlex/Semantic Scholar → PostgreSQL
  - Location: [backend/projects/open-academic-analytics/](../../backend/projects/open-academic-analytics/)
  - Includes: Incremental sync, caching, privacy-preserving exports, composite keys
