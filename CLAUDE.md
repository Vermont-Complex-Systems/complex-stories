# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

Complex Stories is a scientific data essay platform built with SvelteKit, inspired by The Pudding. It showcases interactive visualizations and computational science research from the Vermont Complex Systems Institute.

**Architecture**: Monorepo with separate frontend (SvelteKit) and backend (FastAPI + Dagster)
- **Frontend**: `complexstories.uvm.edu` - Node.js server via PM2
- **Backend**: `api.complexstories.uvm.edu` - FastAPI + PostgreSQL via PM2
- **Database**: PostgreSQL for persistent data, DuckDB for backend analytics

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
uv sync                         # Install dependencies (uv workspace)
uv run fastapi dev app/main.py  # FastAPI on port 8000

# Dagster webserver (manages all workspace projects)
uv run dg dev                   # Web UI typically on port 3333
```

### Code Quality
```bash
cd frontend
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
- **SvelteKit 2** with Svelte 5 runes syntax (experimental async components enabled)
- **Node.js adapter** with remote functions for server-side operations
- **D3.js** for data visualization
- **FastAPI** backend with SQLAlchemy 2.0+ async
- **PostgreSQL** for persistent storage
- **Dagster** for data pipeline orchestration (uv workspace)
- **Path aliases**: `$data`, `$styles`, `$stories` for cleaner imports

### Data Flow
1. **Static data**: JSON/CSV files bundled via Vite imports for direct use in components
2. **Dynamic data**: Remote functions → FastAPI endpoints → PostgreSQL
3. **Pipelines**: External APIs → DuckDB (processing) → PostgreSQL (storage) via FastAPI
   - Extract: Dagster fetches from external APIs into DuckDB
   - Transform: SQL/pandas transformations in DuckDB
   - Export: Bulk uploads to PostgreSQL via FastAPI endpoints

### Remote Functions Pattern
Stories use `data.remote.js` for type-safe backend integration:
```javascript
// frontend/src/lib/stories/[story]/data/data.remote.js
import { command, query } from '$app/server';
import { API_BASE } from '$env/static/private';
import * as v from 'valibot';

const API_BASE_URL = API_BASE || 'http://localhost:3001';

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

For non-remote function API calls (in load functions, server actions):
```typescript
// frontend/src/lib/server/api.ts - Shared API utilities
import { API_BASE } from '$env/static/private';
const API_BASE_URL = API_BASE || 'http://localhost:3001';

export const api = {
  async getData(params: any) {
    const response = await fetch(`${API_BASE_URL}/endpoint`);
    if (!response.ok) throw Error(`Failed: ${response.status}`);
    return response.json();
  }
};
```

## Common Patterns

### Frontend Data Loading
Stories use three primary patterns for data:

1. **Static Imports**: JSON/CSV files imported directly from `data/` directory
   ```javascript
   import nodes from '../data/nodes.csv';
   import edges from '../data/edges.json';
   ```
   - CSV files parsed via `@rollup/plugin-dsv` in `vite.config.ts`
   - Bundled at build time for immediate availability

2. **Remote Functions**: Type-safe server-side API calls with Valibot validation
   ```javascript
   import { loadPaperData } from './data.remote.js';
   const papers = await loadPaperData({ authorName, filterBigPapers });
   ```
   - Used for dynamic data from PostgreSQL
   - Validation at runtime

3. **TanStack Query**: Reactive data fetching with caching (used in some stories)
   ```javascript
   import { createQuery } from '@tanstack/svelte-query';
   const query = createQuery(() => ({
     queryKey: ['data', params],
     queryFn: () => fetchData(params)
   }));
   ```

**State Management**: Complex stories use `state.svelte.ts` with Svelte 5 runes:
```typescript
export const dashboardState = $state({
  selectedAuthor: 'Peter Sheridan Dodds',
  filterBigPapers: true
});

export const data = $state({
  papers: null,
  isLoading: false
});
```

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
- Frontend: Node.js server on port 3000 (`complex-stories-main`)
- Backend: FastAPI on port 3001 (`complex-stories-api`)
- Dagster: Webserver via `uv run dg dev` (`dagster-webserver`)

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
- Tables auto-created on startup via `Base.metadata.create_all`
- UPSERT pattern: Check existing row → UPDATE or INSERT

### Authentication & Authorization
Backend implements role-based access control:
- **Admin**: Full access to all data and user management
- **Annotator**: Can edit all research group entries
- **Faculty**: Can only edit entries matching their `payroll_name`
- **Auth**: JWT tokens, default admin user (admin/admin123) created on startup

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
- Models: `backend/app/models/` (SQLAlchemy)
- Routers: `backend/app/routers/` (API endpoints)
- Dagster projects: `backend/projects/` (workspace members in `dg.toml`)
- Shared package: `backend/shared/` (API clients: OpenAlex, Semantic Scholar, Complex Stories API)
- Raw datasets: `backend/data/`

### Docs

- Offering: `docs/offering` (report about our service offering)

## Important Notes

- **Story-first architecture**: Each story can have custom components, data, and styling
- **No CSS framework**: Custom styling per story, global styles in `frontend/src/styles/`
- **Type safety**: Use Valibot schemas in remote functions for validation
- **Privacy**: Surveys use browser fingerprinting, not cookies/localStorage
- **Performance**: DuckDB for backend analytics, PostgreSQL for persistence (DuckDB WASM not currently implemented)
- **Backend workspace**: `uv` manages `backend/` and `backend/shared/` as a workspace
- **Vite path aliases**: Use `$data`, `$styles`, `$stories` for cleaner imports
- **Clean code**: Prefer existing patterns, avoid over-engineering

## Getting Help

- Documentation issues: https://github.com/anthropics/claude-code/issues
- Project includes `@anthropic-ai/claude-code` for enhanced development experience
