# CLAUDE.md

  
  This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

  ## Project Overview

  Complex Stories is a scientific data essay platform built with SvelteKit, inspired by The Pudding. It
  showcases interactive visualizations and computational science research from the Vermont Complex Systems
  Institute. The platform features both internal stories (built with Svelte components) and external stories
  (links to other sites).

  ## Development Commands

  ### Frontend Development
  ```bash
  cd frontend
  npm run dev     # Start development server with hot reloading
  npm run build   # Build for production (Node.js server)
  npm run preview # Preview production build locally
  ```

  ### Backend Development

  **FastAPI Server:**
  ```bash
  cd backend
  uv run fastapi dev app/main.py  # Development server on port 8000
  ```

  **Dagster Workspace (Open Academic Analytics):**
  ```bash
  cd backend/projects/open-academic-analytics
  ./run_dagster.sh  # Dagster webserver with shared modules (auto-assigns port)
  # Alternative: uv run dg dev (if shared modules properly installed)
  ```

  **Environment Setup:**
  - Set `DAGSTER_HOME=~/.dagster` for persistent storage
  - Backend uses uv for dependency management with pyproject.toml
  - Shared clients in `backend/shared/clients/` for reusable API resources
  - Backend includes PostgreSQL support (asyncpg, psycopg2-binary) and Alembic for migrations

### Code Quality
- `npm run check` - Type checking with svelte-check
- `npm run check:watch` - Type checking in watch mode
- `npm run format` - Format code with Prettier
- `npm run lint` - Check code formatting with Prettier

### Database (Drizzle ORM)
- `npm run db:push` - Push schema changes to database
- `npm run db:generate` - Generate migration files
- `npm run db:migrate` - Run database migrations
- `npm run db:studio` - Open Drizzle Studio for database management

You are able to use the Svelte MCP server, where you have access to comprehensive Svelte 5 and SvelteKit documentation. Here's how to use the available tools effectively:

## Available MCP Tools:

### 1. list-sections

Use this FIRST to discover all available documentation sections. Returns a structured list with titles, use_cases, and paths.
When asked about Svelte or SvelteKit topics, ALWAYS use this tool at the start of the chat to find relevant sections.

### 2. get-documentation

Retrieves full documentation content for specific sections. Accepts single or multiple sections.
After calling the list-sections tool, you MUST analyze the returned documentation sections (especially the use_cases field) and then use the get-documentation tool to fetch ALL documentation sections that are relevant for the user's task.

### 3. svelte-autofixer

Analyzes Svelte code and returns issues and suggestions.
You MUST use this tool whenever writing Svelte code before sending it to the user. Keep calling it until no issues or suggestions are returned.

### 4. playground-link

Generates a Svelte Playground link with the provided code.
After completing the code, ask the user if they want a playground link. Only call this tool after user confirmation and NEVER if code was written to files in their project.

  ### Testing
  - **Frontend**: No specific test framework is configured. Check individual story directories for any custom testing setups.
  - **Backend**: Test directories exist at `backend/tests/` and `backend/projects/open-academic-analytics/tests/`

  ### Deployment
  - `pm2 start ecosystem.config.json` - Deploy using PM2 process manager
  - Built application serves from `./build/index.js` on port 3000 (production)
  - Frontend runs as Node.js server, not static site

  ### Dependency Management
  ```bash
  cd frontend
  npm install  # Install all Node.js dependencies

  cd backend
  uv sync      # Install Python dependencies
  ```
  - Frontend dependencies include specialized packages like `@duckdb/duckdb-wasm`, `allotaxonometer-ui`, `svelteplot`
  - Backend uses uv for Python dependency management with pyproject.toml
  - Optional dependencies configured for Linux x64 builds

  ## Architecture

  ### Story Structure
  Each story lives in `frontend/src/lib/stories/[story-slug]/` with the following structure:
  ```
  story-slug/
  ├── components/
  │ └── Index.svelte # Main story component
  ├── data/
  │ ├── copy.json # Story metadata and text content
  │ └── [other-data-files] # Story-specific data files
  ├── utils/ # Story-specific utilities (optional)
  └── state.svelte.ts # Story-specific state management (optional)
  ```

  ### Data Management
  - Stories are configured in `frontend/src/data/stories.csv` which defines metadata, URLs, authors, keywords, and display settings
  - Story components are dynamically loaded via `frontend/src/lib/utils/storyRegistry.js` using Vite's `import.meta.glob()`
  - Global data files live in `frontend/src/data/` with path alias `$data`
  - Static assets live in `frontend/static/`
  - CSV/TSV files can be imported directly as JS objects via the DSV plugin
  - Complex stories may include `data/loader.js` files for dynamic data processing

  ### Routing
  - `/` - Homepage with story grid
  - `/[slug]` - Individual story pages (dynamic routing)
  - `/blog/[slug]` - Blog posts
  - `/about` - About page
  - `/research-at-uvm` - Research groups page
  - `/author/[name]` - Author pages

  ### Key Technologies
  - **SvelteKit 2** with Svelte 5 (using runes syntax)
  - **Node.js server** via `@sveltejs/adapter-node` with remote functions support
  - **D3.js** for data visualization and manipulation
  - **DuckDB WASM** for client-side data processing
  - **Vite** for build tooling with custom plugins for DSV files
  - **TypeScript** for type safety

  ### Styling Approach
  - No CSS framework - custom styling per story
  - Global styles in `frontend/src/styles/` (app.css, base.css, theme.css, etc.)
  - Component-specific styles within `<style>` blocks
  - Story-wide styling decisions made in story's `Index.svelte`

  ### State Management
  - Stories may include `state.svelte.ts` files for complex state using Svelte 5 runes
  - Context API used for passing data between components
  - No global state management library

  ### External Dependencies
  - **Enhanced Images** for optimized image handling
  - **Rehype/Remark** plugins for markdown processing with math and syntax highlighting
  - **Sharp** for image optimization
  - **Reveal.js** for presentation components
  - **Allotaxonometer UI** for specialized taxonomy visualization components
  - **SveltePlot** for data plotting capabilities
  - **p5-svelte** for creative coding and generative art
  - **bits-ui** for accessible UI primitives

  ### Build Configuration
  - **Vite** config includes custom path aliases: `$data` → `frontend/src/data`, `$styles` → `frontend/src/styles`
  - **DSV plugin** for loading CSV/TSV files directly in components
  - **Version/timestamp injection** via `__VERSION__` and `__TIMESTAMP__` globals
  - **Node.js adapter** for server-side functionality
  - **Remote functions** enabled for dynamic data fetching
  - **PM2 deployment** via ecosystem.config.json

  

## Adding New Stories

  

1. Create story directory in `frontend/src/lib/stories/[new-story-slug]/`
2. Add required `components/Index.svelte` and `data/copy.json`
3. Add story entry to `frontend/src/data/stories.csv` with required fields:
- `url`: story slug (matches directory name)
- `url_alt`: external URL (for external stories)
- `external`: true/false flag for external vs internal stories
- `hed`, `dek`: headline and description
- `author`, `date`, `bgColor`, `fgColor`: display metadata
- `keyword`, `filters`, `faves`: categorization and homepage display
4. Story will be automatically registered via the story registry system

  ## Important Development Notes

- **External vs Internal Stories**: External stories (`external: true`) link to other sites via `url_alt` field, while internal stories are rendered as Svelte components
   - Use Svelte 5 runes syntax (`$state`, `$derived`, `$props`) instead of legacy reactive statements
   - Story positioning decisions should be made by parent components
   - The project uses `BASE_PATH` environment variable for deployment path configuration
   - DuckDB is excluded from SSR optimization in vite config
   - Worker format is set to 'es' for modern browser support

  

### Architecture Migration Status

**Current Status**: The migration to separate frontend and backend is actively underway. The `backend/` directory has been created with FastAPI infrastructure, and the frontend is already using the Node.js adapter with remote functions enabled.

The project is being refactored to support external institutions and better data sharing between stories. The new architecture separates frontend and backend into distinct layers while maintaining the current performance benefits.

#### Current Issues Being Addressed

- **Data sharing**: Stories like `uvm-research-groups` need data from `open-academic-analytics` pipeline
- **External dependencies**: Raw datasets currently pulled from `vermont-complex-systems.github.io/datasets/`
- **Multi-tenancy**: Need to serve other research groups/institutions beyond UVM
- **Scalability**: Current per-story backend approach doesn't scale for shared data
- **Interactive features**: Survey forms and data collection require server-side processing

  

#### Current Structure

```
complex-stories-dev/
├── backend/ # FastAPI backend (in development)
│ ├── app/ # FastAPI application
│ │ ├── main.py # FastAPI app entry point
│ │ └── core/ # FastAPI core modules
│ ├── projects/ # Dagster project modules
│ │ └── open-academic-analytics/ # Open academic analytics pipeline
│ │     ├── pyproject.toml # Project-specific dependencies
│ │     └── src/open_academic_analytics/ # Source code
│ ├── shared/ # Shared backend resources
│ │ └── clients/ # Reusable API clients
│ ├── data/ # Raw datasets
│ └── pyproject.toml # Backend dependencies (fastapi, dagster, etc.)
├── frontend/ # SvelteKit frontend
│ ├── src/
│ │ ├── lib/
│ │ │ ├── stories/ # Story components
│ │ │ └── utils/ # Shared utilities
│ │ ├── routes/ # SvelteKit routes
│ │ ├── data/ # Static story metadata
│ │ └── styles/ # Global CSS
│ ├── static/ # Static assets and data files
│ ├── package.json # Node.js dependencies
│ └── svelte.config.js # SvelteKit config with Node.js adapter
└── ecosystem.config.json # PM2 configuration
```

#### Target Structure (Planned)

```
complex-stories/
├── backend/ # FastAPI + Dagster data pipelines
│ ├── app/ # FastAPI application
│ │ ├── main.py # FastAPI app entry point
│ │ ├── api/v1/ # Multi-tenant API endpoints
│ │ ├── core/ # FastAPI core (config, auth, db)
│ │ ├── models/ # Pydantic models
│ │ ├── services/ # Business logic
│ │ └── middleware/ # Auth, CORS, etc.
│ ├── pipelines/ # Dagster data processing (separate concern)
│ │ ├── definitions.py # Main Dagster definitions loader
│ │ ├── shared/ # Shared Dagster resources, clients
│ │ │ ├── resources/ # DuckDB, API clients, paths
│ │ │ └── clients/ # External API clients (OpenAlex, Semantic Scholar)
│ │ ├── open_academic_analytics/ # Migrated from story backend
│ │ │ ├── assets/ # Extract, transform, export assets
│ │ │ └── resources.py # Pipeline-specific resources
│ │ └── data_luminosity/ # Future pipeline
│ │ ├── assets/
│ │ └── resources.py
│ ├── data/ # raw datasets
│ │ ├── academic-department.parquet
│ │ └── academic-research-groups.parquet
│ ├── pyproject.toml # Python dependencies (dagster, fastapi, etc.)
│ └── tests/ # Backend tests
├── frontend/ # SvelteKit (current src/ moved here)
│ ├── src/
│ │ ├── lib/
│ │ │ ├── stories/ # Story components (frontend only)
│ │ │ └── api/ # Generated TypeScript types from OpenAPI
│ │ ├── routes/ # SvelteKit routes
│ │ └── data/ # Static story metadata
│ ├── static/data/ # Generated parquet files from backend
│ ├── package.json # Node.js dependencies
│ └── svelte.config.js # SvelteKit config with Node.js adapter
└── ecosystem.config.js # PM2 configuration
```

  

#### Deployment Strategy
- **Frontend**: `complexstories.uvm.edu` (SvelteKit Node.js adapter via PM2)
- **Backend**: `api.complexstories.uvm.edu` (FastAPI via PM2)
- **Infrastructure**: Research VM with PM2 process management (IT handles reverse proxy)
- **Monorepo**: Single repository with `/frontend` and `/backend` separation
- **Database**: External managed MongoDB instance

#### Data Flow Architecture
- **Static files**: Continue using parquet + DuckDB WASM for high-performance exploration
- **Form actions**: SvelteKit form actions for surveys and interactive data collection
- **API calls**: SvelteKit server functions call backend API for dynamic queries
- **External API**: Public endpoints for other institutions at `api.complexstories.uvm.edu/`
- **Shared pipelines**: Centralized Dagster assets generate data for multiple stories

#### Benefits
- **Performance**: Keep current DuckDB WASM benefits while enabling server-side features
- **Scalability**: Multi-tenant backend can serve external institutions
- **Data governance**: Single source of truth for raw datasets and processing
- **Interactive capabilities**: Support for surveys, forms, and real-time data collection
- **Professional**: Clear API docs and subdomain structure for partnerships

#### Migration Progress

**Phase 1: Enable Interactive Stories** ✅ **COMPLETED**
1. ✅ Switch SvelteKit to Node.js adapter (`@sveltejs/adapter-node`)
2. ✅ Enable remote functions in SvelteKit configuration
3. ✅ Update deployment to PM2 Node.js app

**Phase 2: Extract Backend Infrastructure** ✅ **COMPLETED**
1. ✅ Create `backend/` directory structure with FastAPI skeleton
2. ✅ Implement PostgreSQL database layer with SQLAlchemy 2.0+ async
3. ✅ Create Paper and Coauthor models matching Dagster export structure
4. ✅ Build comprehensive API endpoints for academic data (GET/POST)
5. ✅ Add database table creation and management scripts
6. ✅ Deploy FastAPI backend via PM2 with environment configuration
7. ✅ Create datasets management API endpoints (parquet and CSV support)
8. ✅ Implement frontend datasets page with API connectivity monitoring
9. ✅ Configure shared clients architecture for Dagster pipelines
10. ✅ Update Dagster pipelines to consume API endpoints instead of raw URLs
11. ✅ **COMPLETED**: IT setup for reverse proxy (api.complexstories.uvm.edu → port 3001)

**Phase 3: Data Sharing Implementation** ✅ **COMPLETED**
1. ✅ Create datasets API endpoints for cross-story data access
2. ✅ Implement shared clients architecture (`backend/shared/clients/`)
3. ✅ Update `open-academic-analytics` pipeline to consume API datasets
4. ✅ Test end-to-end pipeline functionality with new API integration
5. ✅ Update frontend to call backend API for dynamic queries via localhost calls
6. ✅ Maintain DuckDB WASM for high-performance exploration
7. ✅ Fix SSL certificate issues with internal localhost API calls

**Phase 4: Multi-Tenant Platform** ⏳ **PLANNED**
1. Add institution-based data partitioning
2. Create external API documentation and authentication
3. Implement multi-tenant pipeline configuration
4. Add external institution onboarding workflows

#### Backend Migration Pattern
```bash
# Current structure (in progress)
frontend/src/lib/stories/[story]/backend/ → backend/projects/[story]/
frontend/static/data/[story]/ ← backend/projects/[story]/assets/export/

# Target structure
backend/projects/[story]/src/[story]/defs/ → backend/pipelines/[story]/assets/
backend/projects/[story]/clients/ → backend/shared/clients/ (shared)
```

## Remote Functions Architecture

The project will transition from server-side data loading to SvelteKit remote functions for cleaner client-side data management.

### API Design Principles

**Clean URL Structure**: API endpoints follow a simple, intuitive pattern without unnecessary nesting:
- ✅ `api.complexstories.uvm.edu/open-academic-analytics/profs`
- ✅ `api.complexstories.uvm.edu/embeddings/recalculate`
- ✅ `api.complexstories.uvm.edu/institutions/umich/research-groups`
- ❌ `api.complexstories.uvm.edu/v1/pipelines/open-academic-analytics/profs` (too verbose)

**No Versioning by Default**: URLs start simple without version prefixes. Versioning can be added later via headers if needed:
```javascript
// Future versioning via headers if needed
fetch('/open-academic-analytics/profs', {
headers: { 'API-Version': '2024-01-01' }
});
```

### Stories Data Management

**Frontend-Owned Metadata**: Story configuration remains in the frontend via enhanced CSV + SQLite approach:
- Stories metadata (titles, authors, routing) stays in `stories.csv`
- Prerendered SQLite database enables complex queries at build time
- Remote functions used only for truly dynamic data (analytics, cross-story dependencies)

**Prerendered Queries**: Use SvelteKit `prerender` functions with better-sqlite3 + Drizzle:
```javascript
// src/lib/data.remote.js
export const getStories = prerender(
v.optional(v.object({ filters: v.optional(v.array(v.string())) })),
async (params = {}) => {
const db = initDB(); // SQLite from stories.csv
return db.select().from(stories).where(/* filter logic */).all();
}
);
```

### Remote Function Patterns

**Story-Specific Data Loading**: Each story gets a `data.remote.js` file for backend integration:
```javascript
// frontend/src/lib/stories/uvm-research-groups/data.remote.js
export const getProfs = query(
v.optional(v.object({ research_area: v.optional(v.string()) })),
async (filters = {}) => {
const response = await fetch('https://api.complexstories.uvm.edu/open-academic-analytics/profs', {
method: 'POST',
body: JSON.stringify(filters)
});
return response.json();
}
);
```

**Simplified Page Loading**: `+page.server.ts` only handles static copy.json, no async data:
```typescript
// frontend/src/routes/[slug]/+page.server.ts (uniform for all stories)
export async function load({ params }) {
const story = storiesData.find(d => d.slug === params.slug);
const copyData = await import(`$lib/stories/${params.slug}/data/copy.json`);
return { story, copyData };
}
```

**Component Integration**: Stories use remote functions directly with Svelte's await expressions:
```javascript
// Story components
let profs = $derived(await getProfs({ research_area: filter }));
```

### Benefits
- **No Server-Side Loading**: Eliminates complex `+page.server.ts` async patterns
- **Reactive Data**: Queries automatically re-run when parameters change
- **Type Safety**: Valibot schemas provide validation and TypeScript types
- **Performance**: Prerendered SQLite for stories, remote functions for dynamic data
- **Clean URLs**: Simple, readable API endpoints without unnecessary nesting

## Database Layer Implementation

The backend now includes a complete PostgreSQL database layer with academic data models:

### **Database Models** (`backend/app/models/academic.py`)
- **Paper model**: Complete structure matching Dagster pipeline exports with 80+ fields including:
  - Author and publication metadata (title, year, citations, etc.)
  - OpenAlex and Semantic Scholar integration data
  - UMAP embeddings for visualization
  - Collaboration metrics (coauthor counts, citation analysis)
  - Open access status and PDF availability
- **Coauthor model**: Collaboration analysis data including:
  - Ego/coauthor relationship data
  - Age and career stage analysis
  - Institution affiliations and shared collaborations
  - Temporal collaboration patterns

### **Database Configuration** (`backend/app/core/database.py`)
- SQLAlchemy 2.0+ with async PostgreSQL support via asyncpg
- Connection pooling and error handling
- Environment-based configuration (supports both `DATABASE_URL` and individual components)
- Automatic connection management in FastAPI lifecycle

### **API Endpoints**
- **Academic Data** (`backend/app/routers/open_academic_analytics.py`):
  - GET/POST endpoints for papers and coauthors data
  - Bulk data ingestion for Dagster pipeline integration
  - Metadata endpoints for departments and research areas
- **Datasets Management** (`backend/app/routers/datasets.py`):
  - File serving endpoints for raw parquet/CSV data
  - Preview endpoints for data exploration
  - Statistics endpoints for dataset metadata
  - Support for both parquet and CSV formats with proper NaN handling

### **Deployment Infrastructure**
- **PM2 Configuration** (`ecosystem.config.json`): FastAPI service on port 3001
- **Environment Management**: PostgreSQL credentials and CORS configuration
- **Database Setup**: Complete table creation and user management scripts
- **Dependency Management**: Full parquet support with pyarrow and fastparquet

### **Frontend Integration**
- **Datasets Page** (`frontend/src/routes/datasets/`): API connectivity monitoring
- **Status Indicators**: Real-time API health checks and dataset availability
- **Download/Preview**: Direct access to datasets with proper error handling

### **Current Status**
✅ **COMPLETE**: Database models, API endpoints, PM2 deployment, frontend integration
⏳ **WAITING**: IT reverse proxy setup for api.complexstories.uvm.edu → port 3001

## API Layer Architecture Decision

The project uses a FastAPI backend layer instead of direct database access from the frontend for several strategic reasons:

### **Security & Multi-Tenancy**
- **Database credentials** never exposed to client-side code
- **Fine-grained authorization** - different institutions can have different data access levels
- **Data isolation** - API can enforce tenant boundaries that would be hard to manage with direct DB access

### **External Institution Support**
With the API approach, Complex Stories can serve other research groups/institutions through:
- **Clean public endpoints** like `api.complexstories.uvm.edu/institutions/umich/research-groups`
- **API documentation** for external developers
- **Rate limiting & monitoring** of external usage
- **Versioning** when needed via headers

### **Data Transformation & Business Logic**
Stories often need processed data, not raw database documents:
- **Cross-story data sharing** (e.g., `uvm-research-groups` using `open-academic-analytics` data)
- **Complex aggregations** that would be unwieldy in frontend code
- **Consistent data formats** across different data sources
- **Server-side caching** of expensive queries

### **Performance & Integration**
- **Data pipeline integration** - Dagster can populate the API's data store
- **Query optimization** centralized in one place
- **Multiple output formats** (raw CSV, JSON, previews) from single endpoints

**Example comparison:**
```javascript
// Direct MongoDB approach (problematic)
const client = new MongoClient(connectionString); // Security issue
const result = await client.db('complex_stories')
  .collection('professors')
  .aggregate([/* complex pipeline */]); // Business logic in frontend

// API layer approach (preferred)
const profs = await fetch('/open-academic-analytics/profs?department=cs');
```

### Claude Code Integration
- The project includes `@anthropic-ai/claude-code` as a dependency for enhanced development experience
- This CLAUDE.md file provides context for future Claude Code sessions

### Story Configuration Fields
Important CSV fields in `frontend/src/data/stories.csv`:
- `external`: Boolean flag for internal vs external stories
- `filters`: Used for homepage categorization (popular, in_theory, dashboard, dataset)
- `faves`: Boolean for featuring stories on homepage
- `bgColor`/`fgColor`: Story-specific color theming
- `keyword`: Space-separated tags for story classification

## Open Academic Analytics Pipeline

The `open-academic-analytics` Dagster pipeline processes academic publication data for UVM faculty research analysis. This pipeline demonstrates the complete data flow from extraction to final database upload.

### **Pipeline Architecture**

```
Raw Data Sources → Extract → Transform → Export → PostgreSQL
     ↓              ↓          ↓          ↓          ↓
OpenAlex API → uvm_publications → processed_papers → paper_database_upload
UVM Faculty  → coauthor_cache   → yearly_collaborations → coauthor_database_upload
```

### **Key Assets and Data Flow**

**Extract Phase** (`backend/projects/open-academic-analytics/src/open_academic_analytics/defs/extract/`):
- **`uvm_publications`**: Fetches publication data from OpenAlex API for UVM faculty
  - Creates normalized `oa.raw.publications` and `oa.raw.authorships` tables
  - Handles incremental updates and first publication year corrections
  - Uses composite keys to handle multiple UVM authors per paper
- **`coauthor_cache`**: Caches external coauthor first publication years

**Transform Phase** (`backend/projects/open-academic-analytics/src/open_academic_analytics/defs/transform/`):
- **`processed_papers`**: Processes raw publications into analysis-ready format
- **`yearly_collaborations`**: Analyzes collaboration patterns between authors by year
- **`coauthor_institutions`**: Maps authors to their institutional affiliations

**Export Phase** (`backend/projects/open-academic-analytics/src/open_academic_analytics/defs/export/`):
- **`paper_database_upload`**: Exports processed papers to PostgreSQL via FastAPI bulk endpoint
- **`coauthor_database_upload`**: Exports collaboration data to PostgreSQL via FastAPI bulk endpoint

### **Critical Data Model Insights**

**Composite Primary Keys**: Papers use `(id, ego_author_id)` composite primary key because:
- Same paper can have multiple UVM faculty authors
- Each UVM author gets their own record for the same paper
- Prevents data loss during bulk uploads with `ON CONFLICT DO UPDATE`

**First Publication Year Logic**: The pipeline uses a hierarchical approach for first publication years:
```sql
-- For ego authors (UVM faculty)
COALESCE(prof.first_pub_year, calculated_from_raw.min_pub_year) as ego_first_pub_year

-- For coauthors
COALESCE(
    cc_coauthor.first_pub_year,           -- External coauthors from cache
    prof_coauthor.first_pub_year,         -- UVM coauthors from faculty table
    calculated_from_raw.min_pub_year      -- Calculated from oa.raw.authorships + publications
) as coauthor_first_pub_year
```

**Raw Data Calculation**: First publication years are calculated by joining:
```sql
SELECT a.author_id, MIN(p.publication_year) as min_pub_year
FROM oa.raw.authorships a
JOIN oa.raw.publications p ON a.work_id = p.id
WHERE p.publication_year IS NOT NULL
GROUP BY a.author_id
```

### **Bulk Upload Strategy**

**Batch Processing**: Both paper and coauthor exports use batch processing:
- **Papers**: 10,000 records per batch to PostgreSQL
- **Coauthors**: 100,000 records per batch to PostgreSQL
- **Error Handling**: Individual batch failures don't affect other batches
- **Progress Logging**: Detailed logging for troubleshooting upload issues

**FastAPI Integration**: Export assets POST to FastAPI bulk endpoints:
- `POST /open-academic-analytics/papers/bulk` - Bulk paper upload
- `POST /open-academic-analytics/coauthors/bulk` - Bulk coauthor upload
- Uses `ON CONFLICT DO UPDATE` for upsert operations
- Handles field mapping between Dagster exports and PostgreSQL models

### **Common Issues and Solutions**

**Missing Papers**: Initially lost ~85,000 papers due to single primary key conflicts
- **Solution**: Implemented composite primary key `(id, ego_author_id)` in PostgreSQL model
- **Root Cause**: Same paper had multiple UVM authors, causing overwrites instead of inserts

**NULL First Publication Years**: UVM coauthors showed NULL publication years
- **Root Cause**: UVM faculty weren't in external coauthor cache
- **Solution**: Added JOIN to UVM faculty table + fallback to calculated years from raw data

**Sync Strategy**: UVM faculty publications use intelligent incremental updates:
- Tracks sync status in `oa.cache.uvm_profs_sync_status`
- Uses corrected first publication years to filter historical data
- Continues from latest existing publication date to avoid gaps

### **Development Workflow**

**Testing Pipeline Changes**:
```bash
cd backend/projects/open-academic-analytics
./run_dagster.sh  # Start Dagster webserver
# Navigate to localhost:{assigned_port} to trigger assets
```

**Database Management**:
```bash
# Connect to PostgreSQL
psql -h localhost -U jstonge1 -d complex_stories

# Drop and recreate tables after schema changes
DROP TABLE papers CASCADE;
DROP TABLE coauthors CASCADE;
```

**FastAPI Development**:
```bash
cd backend
uv run fastapi dev app/main.py  # Development server on port 8000
```

This pipeline demonstrates enterprise-grade data processing with proper error handling, incremental updates, and efficient bulk operations for academic research data analysis.