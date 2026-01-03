# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Complex Stories is a full-stack scientific data storytelling platform built with SvelteKit (frontend) and FastAPI (backend). It showcases interactive visualizations and computational science research from the Vermont Complex Systems Institute, inspired by The Pudding.

## Repository Structure

This is a monorepo with two main components:

```
complex-stories-dev/
├── frontend/          # SvelteKit 2 + Svelte 5 application
├── backend/           # FastAPI + Dagster data pipelines
│   ├── app/          # FastAPI application
│   ├── projects/     # Dagster pipeline projects
│   ├── shared/       # Shared resources/clients
│   └── data/         # Raw datasets
└── ecosystem.config.json  # PM2 deployment config
```

## Development Commands

### Frontend Development

```bash
cd frontend
npm install                    # Install dependencies
npm run dev                    # Start dev server (localhost:5173)
npm run build                  # Build for production (static site)
npm run preview                # Preview production build
npm run check                  # TypeScript type checking
npm run check:watch            # Type checking in watch mode
npm run format                 # Format code with Prettier
npm run lint                   # Check code formatting
```

### Backend Development

```bash
cd backend

# Install dependencies
uv sync                        # Create venv and install deps

# Activate virtual environment
source .venv/bin/activate      # MacOS/Linux
.venv\Scripts\activate         # Windows

# Run FastAPI development server
uv run fastapi dev app/main.py  # Runs on port 8000

# Run Dagster development server
dg dev                         # Opens Dagster UI on localhost:3000

# Database connection (PostgreSQL)
psql -h localhost -U your_user -d complex_stories
```

### Production Deployment

```bash
# PM2 process manager
pm2 start ecosystem.config.json
pm2 status
pm2 logs complex-stories-main
pm2 logs complex-stories-api
pm2 logs dagster-webserver
```

## Architecture Overview

### Frontend (SvelteKit + Svelte 5)

**Tech Stack:**
- SvelteKit 2 with Svelte 5 runes syntax for reactive state
- Vite for build tooling with custom DSV plugin
- D3.js for data visualization
- DuckDB WASM for client-side data analysis
- Custom CSS (no framework) with story-specific styling
- SvelteKit remote functions for type-safe API calls

**Key Patterns:**

1. **Story-Based Architecture**: Each story is self-contained in `src/lib/stories/[story-slug]/`
   ```
   story-slug/
   ├── components/
   │   └── Index.svelte       # Main entry point
   ├── data/
   │   └── copy.json          # Story metadata
   ├── state.svelte.ts        # Svelte 5 runes state (optional)
   ├── data.remote.js         # API calls via remote functions (optional)
   └── utils/                 # Story-specific utilities (optional)
   ```

2. **State Management**: Uses Svelte 5 runes pattern with `$state`, `$derived`, and `$effect`
   - UI state (layout, appearance)
   - Dashboard state (filter selections)
   - Data state (fetched from API)
   - Derived state (computed values that auto-update)

3. **Remote Functions**: Server-validated API calls defined in `*.remote.js` files
   - Valibot schema validation
   - Type-safe across client/server boundary
   - Server-side cookie management

4. **Path Aliases**:
   - `$data` → `src/data/`
   - `$styles` → `src/styles/`
   - `$stories` → `src/lib/stories/`

5. **Story Registration**: Stories configured in `src/data/stories.csv` with metadata (slug, title, author, colors, filters, etc.)

### Backend (FastAPI + Dagster)

**Tech Stack:**
- FastAPI with async/await for API endpoints
- SQLAlchemy 2.0+ with async PostgreSQL (psycopg driver)
- Dagster for data pipeline orchestration
- JWT token-based authentication
- Role-based access control (admin, annotator, faculty)

**Key Patterns:**

1. **Modular Router Pattern**: Each domain has public and admin routers
   ```python
   # In routers/example.py
   router = APIRouter()        # Public endpoints
   admin_router = APIRouter()  # Admin-only endpoints

   # In main.py
   app.include_router(example.router, prefix="/example")
   app.include_router(example.admin_router, prefix="/admin/example")
   ```

2. **Dependency Injection**:
   ```python
   async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
       async with database.async_session() as session:
           yield session

   @router.get("/endpoint")
   async def endpoint(db: AsyncSession = Depends(get_db_session)):
       # Use db session
   ```

3. **Bulk Operations**: Efficient PostgreSQL upserts for pipeline data
   ```python
   stmt = insert(Model).on_conflict_do_update(
       index_elements=['id', 'composite_key'],
       set_={col.name: stmt.excluded[col.name] for col in Model.__table__.columns}
   )
   ```

4. **Database Configuration**:
   - Environment variables: `DATABASE_URL` or individual `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
   - Connection pooling: `pool_size=20, max_overflow=0`
   - Async engine: `postgresql+psycopg://user:pass@host/db`

5. **Authentication Flow**:
   - Login returns JWT token
   - Token stored in both cookies (httpOnly:false) and localStorage
   - Protected routes use `Depends(get_current_user)` or `Depends(get_admin_user)`

## Data Flow Pattern

```
User Interaction (Frontend Component)
    ↓
State Update (state.svelte.ts)
    ↓
$effect Triggers
    ↓
Remote Function Call (data.remote.js with Valibot validation)
    ↓
FastAPI Endpoint (app/routers/*.py)
    ↓
Dependency Injection (get_db_session)
    ↓
SQLAlchemy Query (async with PostgreSQL)
    ↓
JSON Response
    ↓
Process & Update State
    ↓
$derived Values Recompute
    ↓
Component Re-renders
```

## Database Models

Key models in `app/models/academic.py`:

- **Paper**: Academic publications with 60+ fields
  - Composite primary key: `(id, ego_author_id)`
  - OpenAlex and Semantic Scholar integration
  - UMAP embeddings for visualization

- **Coauthor**: Author collaboration analysis
  - Ego/coauthor relationship data
  - Career stage and institutional affiliations

- **Training**: Aggregated research metrics
  - Change point detection data
  - Career trajectory analysis

User model in `app/models/auth.py`:
- Role-based permissions (admin, annotator, faculty)
- Faculty users linked via `payroll_name` field

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - User registration
- `POST /auth/login` - Login with JWT token
- `GET /auth/me` - Current user info
- `GET /auth/users` - List users (admin only)
- `PUT /auth/users/{user_id}/role` - Update user role (admin only)

### Academic Data (`/open-academic-analytics`)
- `GET /papers/{author_name}` - Get papers for author
- `GET /coauthors/{author_name}` - Get collaboration data
- `GET /embeddings` - Get UMAP embeddings
- `POST /papers/bulk` - Bulk upload (admin only, used by Dagster)
- `POST /coauthors/bulk` - Bulk upload (admin only, used by Dagster)

### Datasets (`/datasets`)
- `GET /academic-research-groups` - Research group metadata
- Admin endpoints for data import/export

## Creating a New Story

1. **Create directory structure**:
   ```bash
   mkdir -p frontend/src/lib/stories/my-story/{components,data}
   ```

2. **Create main component** (`frontend/src/lib/stories/my-story/components/Index.svelte`):
   ```svelte
   <script>
     import copy from '../data/copy.json';
   </script>

   <article>
     <h1>{copy.title}</h1>
     <p>{copy.subtitle}</p>
   </article>
   ```

3. **Create metadata** (`frontend/src/lib/stories/my-story/data/copy.json`):
   ```json
   {
     "title": "My Story Title",
     "subtitle": "Engaging subtitle",
     "author": "Author Name",
     "date": "2025-01-15"
   }
   ```

4. **Register story** in `frontend/src/data/stories.csv`:
   ```csv
   url,external,hed,dek,author,date,bgColor,fgColor,keyword,filters,faves
   my-story,false,My Story,Subtitle,Author,1/15/2025,#f0f0f0,#333,research,dashboard,false
   ```

5. **Test**: Navigate to `/my-story` in dev mode

## Styling Guidelines

- No CSS framework - each story has its own aesthetic
- Global styles in `src/styles/` handle common elements
- Component-specific styles use Svelte `<style>` blocks
- Story-wide styles defined in main `Index.svelte`
- Positioning decisions made by parent components
- Mobile-first responsive design

## Working with Data

### CSV/TSV Files
```javascript
import myData from '$data/my-dataset.csv';  // Auto-parsed by DSV plugin
```

### DuckDB for Complex Analysis
```javascript
import { getDuckDB } from '$lib/utils/duckdb.js';

const db = await getDuckDB();
const result = await db.query('SELECT * FROM my_table');
```

### API Integration (Remote Functions)
```javascript
// In story/data.remote.js
import { query } from '@anthropic-ai/claude-code';
import * as v from 'valibot';

export const loadData = query(
  v.object({ param: v.string() }),
  async ({ param }) => {
    const response = await fetch(`${API_URL}/endpoint/${param}`);
    return await response.json();
  }
);

// In component
import { loadData } from '../data.remote.js';
const data = await loadData({ param: 'value' });
```

## Dagster Pipeline Integration

Pipelines in `backend/projects/`:
- Extract data from external APIs (OpenAlex, Semantic Scholar)
- Transform and enrich data
- Load to PostgreSQL via FastAPI bulk endpoints
- Shared clients in `backend/shared/clients/`

Run pipeline development:
```bash
cd backend
dg dev  # Opens Dagster UI
```

## Environment Variables

### Backend
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/complex_stories
# Or individual components:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=complex_stories
DB_USER=your_user
DB_PASSWORD=your_password

# Authentication
SECRET_KEY=your-secret-key
```

### Frontend
```bash
# API endpoint
VITE_API_URL=http://localhost:8000
```

## Important File Locations

### Frontend
- Main entry: `frontend/src/routes/+layout.svelte`
- Story routing: `frontend/src/routes/[slug]/+page.server.ts`
- Auth state: `frontend/src/lib/auth.svelte.ts`
- Shared components: `frontend/src/lib/components/helpers/`
- Global styles: `frontend/src/styles/`

### Backend
- App entry: `backend/app/main.py`
- Database config: `backend/app/core/database.py`
- Auth utilities: `backend/app/core/auth.py`
- API routers: `backend/app/routers/`
- Models: `backend/app/models/`
- Dagster projects: `backend/projects/`

## Testing

Currently no test infrastructure configured. When adding tests:
- Frontend: Consider Vitest for unit tests, Playwright for e2e
- Backend: Use pytest with FastAPI TestClient and async test support

## Deployment Notes

- Frontend builds to static site via `@sveltejs/adapter-node`
- Backend runs via PM2 process manager
- Three PM2 apps: frontend (port 3000), API (port 3001), Dagster webserver
- PostgreSQL database required
- Uses environment files for sensitive config
