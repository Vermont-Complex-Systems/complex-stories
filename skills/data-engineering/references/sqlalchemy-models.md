# SQLAlchemy Model Patterns

This reference covers SQLAlchemy 2.0+ patterns for defining database models in Complex Stories.

## Model Basics

### Simple Model
```python
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Model with Composite Primary Key
```python
class Paper(Base):
    __tablename__ = "papers"

    # Composite primary key: same paper can appear for multiple authors
    id = Column(String, primary_key=True)
    ego_author_id = Column(String, primary_key=True)

    title = Column(String, nullable=False)
    publication_date = Column(DateTime)
    cited_by_count = Column(Integer)
```

### Model with JSON Column
```python
from sqlalchemy.dialects.postgresql import JSONB

class DataRecord(Base):
    __tablename__ = "data_records"

    id = Column(String, primary_key=True)
    metadata = Column(JSONB)  # Queryable JSON in PostgreSQL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

## Column Types

### Common Types
```python
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, Date
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

# Text types
name = Column(String)           # VARCHAR (no length = unlimited in PostgreSQL)
name = Column(String(255))      # VARCHAR(255)
bio = Column(Text)              # TEXT (for long content)

# Numeric types
count = Column(Integer)         # INTEGER
price = Column(Float)           # DOUBLE PRECISION
is_active = Column(Boolean)     # BOOLEAN

# Date/time types
created_at = Column(DateTime(timezone=True))  # TIMESTAMP WITH TIME ZONE
birth_date = Column(Date)                     # DATE

# PostgreSQL-specific
tags = Column(ARRAY(String))    # VARCHAR[]
data = Column(JSONB)            # JSONB (queryable JSON)
```

### Nullable vs Non-Nullable
```python
# Nullable by default
optional_field = Column(String)
optional_field = Column(String, nullable=True)

# Require value
required_field = Column(String, nullable=False)
```

## Default Values

### Database Defaults
```python
# Current timestamp (computed by database)
created_at = Column(DateTime(timezone=True), server_default=func.now())

# Updated on every update
updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Static default value
status = Column(String, server_default="pending")
is_active = Column(Boolean, server_default="true")
count = Column(Integer, server_default="0")
```

### Application Defaults
```python
from datetime import datetime

# Computed by Python
created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

# Static value
status = Column(String, default="pending")
```

**Prefer `server_default`** for timestamps and static values - ensures consistency even when data is inserted outside the application.

## Indexes

### Single Column Index
```python
from sqlalchemy import Index

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String, index=True)  # Simple index
    email = Column(String, unique=True)  # Unique index
```

### Composite Index
```python
class Paper(Base):
    __tablename__ = "papers"

    id = Column(String, primary_key=True)
    ego_author_id = Column(String, primary_key=True)
    publication_year = Column(Integer)
    cited_by_count = Column(Integer)

    # Composite index for common queries
    __table_args__ = (
        Index('idx_author_year', 'ego_author_id', 'publication_year'),
    )
```

### Partial Index (PostgreSQL)
```python
from sqlalchemy import Index, text

class DataRecord(Base):
    __tablename__ = "data_records"

    id = Column(String, primary_key=True)
    status = Column(String)
    created_at = Column(DateTime(timezone=True))

    # Index only active records
    __table_args__ = (
        Index(
            'idx_active_records',
            'created_at',
            postgresql_where=text("status = 'active'")
        ),
    )
```

## Relationships

### One-to-Many
```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Author(Base):
    __tablename__ = "authors"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    # One author has many papers
    papers = relationship("Paper", back_populates="author")

class Paper(Base):
    __tablename__ = "papers"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    author_id = Column(String, ForeignKey("authors.id"))

    # Many papers belong to one author
    author = relationship("Author", back_populates="papers")
```

### Many-to-Many
```python
from sqlalchemy import Table

# Association table
paper_tags = Table(
    'paper_tags',
    Base.metadata,
    Column('paper_id', String, ForeignKey('papers.id'), primary_key=True),
    Column('tag_id', String, ForeignKey('tags.id'), primary_key=True)
)

class Paper(Base):
    __tablename__ = "papers"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)

    # Many papers can have many tags
    tags = relationship("Tag", secondary=paper_tags, back_populates="papers")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    # Many tags can be on many papers
    papers = relationship("Paper", secondary=paper_tags, back_populates="tags")
```

## Authentication Models

### User with Role-Based Access
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # admin, annotator, faculty, user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
```

## Complex Stories Specific Patterns

### Survey Response Model
```python
class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    fingerprint = Column(String, primary_key=True)
    question = Column(String, primary_key=True)

    value = Column(String)  # Store as string, parse in application
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Academic Data Model
```python
class Paper(Base):
    __tablename__ = "papers"

    # Composite key: same paper from multiple author perspectives
    id = Column(String, primary_key=True)
    ego_author_id = Column(String, primary_key=True)

    # Paper metadata
    title = Column(String, nullable=False)
    publication_date = Column(DateTime)
    publication_year = Column(Integer, index=True)

    # Metrics
    cited_by_count = Column(Integer)
    citation_percentile = Column(Float)

    # UMAP embeddings for visualization
    umap_x = Column(Float)
    umap_y = Column(Float)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_author_year', 'ego_author_id', 'publication_year'),
    )
```

### Collaboration Model
```python
class Coauthor(Base):
    __tablename__ = "coauthors"

    # Composite key
    id = Column(String, primary_key=True)  # Coauthor OpenAlex ID
    ego_author_id = Column(String, primary_key=True)  # UVM faculty ID
    publication_year = Column(Integer, primary_key=True)

    # Coauthor info
    coauthor_name = Column(String)
    coauthor_institution = Column(String)

    # Metrics
    collaboration_count = Column(Integer)
    age_diff = Column(Float)  # Age difference from ego author

    # Privacy-preserving (jittered dates)
    first_collaboration = Column(Date)
    last_collaboration = Column(Date)

    __table_args__ = (
        Index('idx_ego_year', 'ego_author_id', 'publication_year'),
    )
```

## Querying Patterns

### Async Session Queries
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Simple query
async def get_project(db: AsyncSession, project_id: str):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    return result.scalar_one_or_none()

# Query with filtering
async def get_active_projects(db: AsyncSession):
    result = await db.execute(
        select(Project).where(Project.is_active == True)
    )
    return result.scalars().all()

# Query with joins (eager loading)
async def get_author_with_papers(db: AsyncSession, author_id: str):
    result = await db.execute(
        select(Author)
        .options(selectinload(Author.papers))
        .where(Author.id == author_id)
    )
    return result.scalar_one_or_none()

# Aggregation
async def count_papers_by_author(db: AsyncSession, author_id: str):
    from sqlalchemy import func
    result = await db.execute(
        select(func.count(Paper.id))
        .where(Paper.ego_author_id == author_id)
    )
    return result.scalar()
```

## UPSERT Pattern

### PostgreSQL ON CONFLICT
```python
from sqlalchemy.dialects.postgresql import insert

async def upsert_papers(db: AsyncSession, papers: list[dict]):
    """Bulk UPSERT papers"""

    stmt = insert(Paper)

    # Update all columns on conflict
    stmt = stmt.on_conflict_do_update(
        index_elements=['id', 'ego_author_id'],  # Composite key
        set_={
            col.name: stmt.excluded[col.name]
            for col in Paper.__table__.columns
            if col.name not in ['id', 'ego_author_id']  # Exclude keys
        }
    )

    await db.execute(stmt, papers)
    await db.commit()
```

### Selective Update on UPSERT
```python
async def upsert_with_selective_update(db: AsyncSession, records: list[dict]):
    """Only update specific fields on conflict"""

    stmt = insert(Paper)
    stmt = stmt.on_conflict_do_update(
        index_elements=['id', 'ego_author_id'],
        set_={
            'cited_by_count': stmt.excluded.cited_by_count,
            'citation_percentile': stmt.excluded.citation_percentile,
            'updated_at': func.now()
        }
    )

    await db.execute(stmt, records)
    await db.commit()
```

## Validation

### Pydantic Schemas for Validation
```python
from pydantic import BaseModel, Field
from datetime import datetime

# Request schema
class PaperCreate(BaseModel):
    id: str = Field(..., min_length=1)
    ego_author_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    publication_year: int = Field(..., ge=1900, le=2100)
    cited_by_count: int = Field(0, ge=0)

# Response schema
class PaperResponse(BaseModel):
    id: str
    ego_author_id: str
    title: str
    publication_year: int
    cited_by_count: int
    created_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode
```

## Best Practices

1. **Always use `server_default=func.now()`** for timestamps
2. **Add indexes** for frequently queried columns
3. **Use composite primary keys** when entity identity depends on multiple columns
4. **Use JSONB** for flexible schema data, but avoid for queryable structured data
5. **Use `nullable=False`** for required fields
6. **Use relationships sparingly** - Complex Stories typically uses flat schemas
7. **Use UPSERT** for all bulk uploads to support pipeline reruns
8. **Add `updated_at`** with `onupdate=func.now()` for tracking changes
9. **Use timezone-aware timestamps**: `DateTime(timezone=True)`
10. **Define models in domain files** (`app/models/academic.py`, `app/models/survey.py`) not one giant file

## Table Creation

Models are automatically created when the FastAPI app starts:

```python
# app/main.py
from app.core.database import engine
from app.models import Base

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

This is idempotent - tables are only created if they don't exist.

## Migration Note

Complex Stories doesn't currently use Alembic migrations. Schema changes are handled by:
1. Dropping and recreating tables (development)
2. Manual SQL migrations (production)

For future migration setup:
```bash
cd backend
uv add alembic
alembic init migrations
# Edit alembic.ini and migrations/env.py
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```
