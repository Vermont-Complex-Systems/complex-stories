# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

Complex Stories is a scientific data essay platform built with SvelteKit, inspired by The Pudding. It showcases interactive visualizations and computational science research from the Vermont Complex Systems Institute.

**Architecture**: Monorepo with separate frontend (SvelteKit) and backend (FastAPI + Dagster)
- **Frontend**: `complexstories.uvm.edu` - Node.js server via PM2
- **Backend**: `api.complexstories.uvm.edu` - FastAPI + PostgreSQL via PM2
- **Database**: PostgreSQL for persistent data, DuckDB WASM for client-side analytics

## Quick Start

### Frontend Development
```bash
cd frontend
npm run dev     # Development server with hot reloading
npm run build   # Build for production (Node.js server)
```

### Backend Development
```bash
cd backend
uv run fastapi dev app/main.py  # FastAPI on port 8000

# Dagster pipeline (Open Academic Analytics)
cd backend/projects/open-academic-analytics
./run_dagster.sh  # Auto-assigns port
```

### Code Quality
```bash
npm run check   # Type checking
npm run format  # Prettier formatting
npm run lint    # Code linting
```

## Architecture

### Story Structure
Each story lives in `frontend/src/lib/stories/[story-slug]/`:
```
story-slug/
├── components/
│   └── Index.svelte          # Main story component
├── data/
│   ├── copy.json             # Story metadata and text
│   ├── data.remote.js        # Remote functions for API calls
│   └── [data-files]          # Story-specific data
├── utils/                    # Story utilities (optional)
└── state.svelte.ts           # State management (optional)
```

### Key Technologies
- **SvelteKit 2** with Svelte 5 runes syntax
- **Node.js adapter** with remote functions for server-side operations
- **D3.js** for data visualization
- **DuckDB WASM** for client-side data processing
- **FastAPI** backend with SQLAlchemy 2.0+ async
- **PostgreSQL** for persistent storage
- **Dagster** for data pipeline orchestration

### Data Flow
1. **Static data**: Parquet files + DuckDB WASM for high-performance client-side analytics
2. **Dynamic data**: Remote functions → FastAPI endpoints → PostgreSQL
3. **Pipelines**: Dagster processes raw data → exports to PostgreSQL via FastAPI

### Remote Functions Pattern
Stories use `data.remote.js` for backend integration:
```javascript
// frontend/src/lib/stories/[story]/data/data.remote.js
import { command, query } from '$app/server';

export const getData = query(
  v.object({ filter: v.optional(v.string()) }),
  async (params) => {
    const response = await fetch(`${API_BASE_URL}/endpoint`, {
      method: 'POST',
      body: JSON.stringify(params)
    });
    return response.json();
  }
);
```

## Common Patterns

### Interactive Surveys with Fingerprinting
See `dark-data-survey` story for complete pattern:
- Browser fingerprinting via `@fingerprintjs/fingerprintjs`
- UPSERT operations for incremental survey responses
- Remote functions for type-safe API calls
- Privacy-first design with consent tracking

**Key files**:
- `frontend/src/lib/stories/dark-data-survey/data/data.remote.js` - Remote functions
- `backend/app/routers/dark_data_survey.py` - API endpoints with UPSERT logic
- `backend/app/models/dark_data_survey.py` - Database model

### Data Pipeline Pattern
See `open-academic-analytics` for complete ETL pipeline:
- Extract: Fetch from external APIs (OpenAlex, Semantic Scholar)
- Transform: Process and normalize data in DuckDB
- Export: Bulk upload to PostgreSQL via FastAPI endpoints

**Key files**:
- `backend/projects/open-academic-analytics/src/open_academic_analytics/defs/` - Pipeline assets
- `backend/app/routers/open_academic_analytics.py` - Bulk upload endpoints
- `backend/app/models/academic.py` - Database models

## Deployment

### PM2 Configuration
```bash
pm2 start ecosystem.config.json  # Deploy both frontend and backend
```

**Services**:
- Frontend: Node.js server on port 3000
- Backend: FastAPI on port 3001
- Dagster: Runs separately via `./run_dagster.sh`

### Environment Variables
```bash
# Backend (.env)
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
API_BASE=https://api.complexstories.uvm.edu

# Frontend (.env)
API_BASE=https://api.complexstories.uvm.edu  # Production
API_BASE=http://localhost:3001               # Development
```

## Database

### PostgreSQL Setup
```bash
# Connect to database
psql -h localhost -U jstonge1 -d complex_stories

# Common operations
DROP TABLE table_name CASCADE;  # Drop table
\dt                             # List tables
\d table_name                   # Describe table
```

### Models & Migrations
- Models: `backend/app/models/` - SQLAlchemy models
- Migrations: Alembic support configured (not actively used yet)
- UPSERT pattern: Check existing row → UPDATE or INSERT

## API Design Principles

**Clean URLs** (no unnecessary nesting):
- ✅ `api.complexstories.uvm.edu/open-academic-analytics/profs`
- ✅ `api.complexstories.uvm.edu/dark-data-survey/upsert`
- ❌ `api.complexstories.uvm.edu/v1/pipelines/...` (too verbose)

**No versioning by default** - Add via headers when needed:
```javascript
fetch('/endpoint', {
  headers: { 'API-Version': '2024-01-01' }
});
```

## Svelte MCP Server

Available tools for Svelte development:
1. **list-sections** - Discover available documentation (use FIRST)
2. **get-documentation** - Fetch specific documentation sections
3. **svelte-autofixer** - Analyze and fix Svelte code (use before sending to user)
4. **playground-link** - Generate Svelte Playground links (ask user first)

## Story Configuration

Stories are defined in `frontend/src/data/stories.csv`:
- `external`: Boolean for internal vs external stories
- `filters`: Homepage categorization (popular, in_theory, dashboard, dataset)
- `faves`: Feature on homepage
- `bgColor`/`fgColor`: Story theming
- `keyword`: Space-separated tags

## Key Locations

### Frontend
- Stories: `frontend/src/lib/stories/`
- Routes: `frontend/src/routes/`
- Global styles: `frontend/src/styles/`
- Static assets: `frontend/static/`
- Data files: `frontend/src/data/`

### Backend
- FastAPI app: `backend/app/`
- Models: `backend/app/models/`
- Routers: `backend/app/routers/`
- Dagster pipelines: `backend/projects/`
- Shared clients: `backend/shared/clients/`
- Raw datasets: `backend/data/`

## Migration Status

✅ **Completed**:
- Frontend/backend separation
- Node.js adapter with remote functions
- PostgreSQL database layer
- FastAPI endpoints for academic data and surveys
- Dagster pipeline integration
- PM2 deployment for both services
- IT reverse proxy setup

⏳ **Planned**:
- Multi-tenant platform features
- External institution onboarding
- API authentication and rate limiting

## Important Notes

- **Story-first architecture**: Each story can have custom components, data, and styling
- **No CSS framework**: Custom styling per story, global styles in `frontend/src/styles/`
- **Type safety**: Use Valibot schemas in remote functions for validation
- **Privacy**: Surveys use browser fingerprinting, not cookies/localStorage
- **Performance**: DuckDB WASM for heavy client-side analytics, PostgreSQL for persistence
- **Clean code**: Prefer existing patterns, avoid over-engineering

## Getting Help

- Documentation issues: https://github.com/anthropics/claude-code/issues
- Project includes `@anthropic-ai/claude-code` for enhanced development experience
