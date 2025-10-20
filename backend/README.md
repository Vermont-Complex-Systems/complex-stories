# Complex Stories Backend

FastAPI backend for the Complex Stories platform, providing API endpoints for academic data analysis and user authentication.

## Quick Start

```bash
# Install dependencies
uv sync

# Start development server
uv run fastapi dev app/main.py  # Runs on port 8000
```

## Architecture

### Core Components

- **FastAPI Application** (`app/main.py`) - Main API server with CORS configuration
- **Database Layer** (`app/core/database.py`) - Async PostgreSQL with SQLAlchemy 2.0+
- **Authentication** (`app/core/auth.py`) - JWT token management and password hashing
- **Models** (`app/models/`) - SQLAlchemy database models
- **Routers** (`app/routers/`) - API endpoints with inline Pydantic schemas

### Key Features

- **Role-Based Access Control** - Admin, annotator, and faculty user roles
- **Faculty Self-Service** - Faculty users can edit only their own research group entries
- **Academic Data APIs** - Endpoints for papers, coauthors, and research group data
- **Dataset Management** - File serving and preview for parquet/CSV datasets
- **Bulk Operations** - Efficient batch processing for large dataset imports

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - User registration
- `POST /auth/login` - User login with JWT token
- `GET /auth/me` - Current user information
- `GET /auth/users` - List all users (admin only)
- `PUT /auth/users/{user_id}/role` - Update user role (admin only)
- `POST /auth/create-users-from-payroll` - Bulk create faculty users (admin only)

### Academic Data (`/open-academic-analytics`)
- `GET /open-academic-analytics/papers` - Retrieve papers data
- `POST /open-academic-analytics/papers/bulk` - Bulk upload papers
- `GET /open-academic-analytics/coauthors` - Retrieve collaboration data
- `POST /open-academic-analytics/coauthors/bulk` - Bulk upload coauthors

### Datasets (`/datasets`)
- `GET /datasets/{filename}` - Serve parquet/CSV files
- `GET /datasets/{filename}/preview` - Preview dataset contents
- `GET /datasets/{filename}/stats` - Dataset metadata and statistics

## Database Models

### User Authentication
- **User** (`models/auth.py`) - User accounts with role-based permissions
  - Supports admin, annotator, and faculty roles
  - Faculty users linked via `payroll_name` field
  - JWT token-based authentication

### Academic Data
- **Paper** (`models/academic.py`) - Academic publications with full metadata
  - OpenAlex and Semantic Scholar integration
  - UMAP embeddings for visualization
  - Collaboration and citation metrics
- **Coauthor** (`models/academic.py`) - Author collaboration analysis
  - Ego/coauthor relationship data
  - Career stage and institutional affiliations

## Permission System

### Role Hierarchy
- **Admin** - Full access to all data and user management
- **Annotator** - Can edit all research group entries
- **Faculty** - Can only edit entries matching their `payroll_name`

### Data Access Patterns
```python
# Faculty users can only edit their own entries
if current_user.role == 'faculty':
    return current_user.payroll_name == row.payroll_name
```

## Development

### Environment Setup
```bash
# Database configuration
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/complex_stories

# Or individual components
DB_HOST=localhost
DB_PORT=5432
DB_NAME=complex_stories
DB_USER=your_user
DB_PASSWORD=your_password
```

### Database Management
```bash
# Connect to PostgreSQL
psql -h localhost -U your_user -d complex_stories

# Create tables (auto-created on startup)
# Tables: users, papers, coauthors
```

### Bulk User Creation
Faculty users are automatically created from `AcademicResearchGroups` payroll data:
```python
# Creates users with format: "lastname_firstname" from "Lastname,Firstname"
# Default password: "changeMe123!"
# Default role: "faculty"
```

## Data Pipeline Integration

The backend integrates with Dagster pipelines in `projects/open-academic-analytics/`:

### Pipeline Flow
```
Dagster Assets → FastAPI Bulk Endpoints → PostgreSQL
```

### Shared Resources
- **Clients** (`shared/clients/`) - Reusable API clients for external services
- **Resources** - Database connections and configuration management

## Deployment

### PM2 Configuration
```bash
# Production deployment
pm2 start ecosystem.config.json

# Backend runs on port 3001 (waiting for reverse proxy setup)
```

### External Dependencies
- PostgreSQL database
- OpenAlex API access
- Semantic Scholar API access

## Project Structure

```
backend/
├── app/                    # FastAPI application
│   ├── main.py            # Application entry point
│   ├── core/              # Core functionality
│   │   ├── database.py    # Database configuration
│   │   └── auth.py        # Authentication utilities
│   ├── models/            # SQLAlchemy models
│   │   ├── auth.py        # User model
│   │   └── academic.py    # Academic data models
│   └── routers/           # API endpoints
│       ├── auth.py        # Authentication endpoints
│       ├── datasets.py    # Dataset management
│       └── open_academic_analytics.py  # Academic data APIs
├── projects/              # Dagster pipelines
│   └── open-academic-analytics/  # Academic data processing
├── shared/                # Shared resources
│   └── clients/          # Reusable API clients
├── data/                 # Raw datasets
└── pyproject.toml        # Python dependencies
```

## Dagster Projects

### Open Academic Analytics

This pipeline processes academic publication data for UVM faculty research analysis, demonstrating complete data flow from extraction to database upload 