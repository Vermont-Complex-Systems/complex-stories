# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Complex Stories is a scientific data essay platform built with SvelteKit, inspired by The Pudding. It showcases interactive visualizations and computational science research from the Vermont Complex Systems Institute. The platform features both internal stories (built with Svelte components) and external stories (links to other sites).

## Development Commands

### Core Development
- `npm run dev` - Start development server with hot reloading
- `npm run build` - Build for production (static site generation)
- `npm run preview` - Preview production build locally

### Code Quality
- `npm run check` - Type checking with svelte-check
- `npm run check:watch` - Type checking in watch mode
- `npm run format` - Format code with Prettier
- `npm run lint` - Check code formatting with Prettier

### Testing
No specific test framework is configured. Check individual story directories for any custom testing setups.

## Architecture

### Story Structure
Each story lives in `src/lib/stories/[story-slug]/` with the following structure:
```
story-slug/
├── components/
│   └── Index.svelte          # Main story component
├── data/
│   ├── copy.json            # Story metadata and text content
│   └── [other-data-files]   # Story-specific data files
├── utils/                   # Story-specific utilities (optional)
└── state.svelte.ts         # Story-specific state management (optional)
```

### Data Management
- Stories are configured in `src/data/stories.csv` which defines metadata, URLs, authors, keywords, and display settings
- Story components are dynamically loaded via `src/lib/utils/storyRegistry.js` using Vite's `import.meta.glob()`
- Global data files live in `src/data/` with path alias `$data`
- Static assets live in `static/`
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
- **Static site generation** via `@sveltejs/adapter-static`
- **D3.js** for data visualization and manipulation
- **DuckDB WASM** for client-side data processing
- **Vite** for build tooling with custom plugins for DSV files
- **TypeScript** for type safety

### Styling Approach
- No CSS framework - custom styling per story
- Global styles in `src/styles/` (app.css, base.css, theme.css, etc.)
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
- **Additional libraries**: P5.js integration, DOM-to-image conversion, PDF generation (jsPDF), Lucide icons, advanced data analysis tools

### Build Configuration
- **Vite** config includes custom path aliases: `$data` → `src/data`, `$styles` → `src/styles`
- **DSV plugin** for loading CSV/TSV files directly in components
- **Version/timestamp injection** via `__VERSION__` and `__TIMESTAMP__` globals
- **Node adapter** is currently configured (not static adapter)
- **DuckDB WASM** excluded from optimization, with d3-regression included in SSR
- **Worker format** set to 'es' for modern browser support
- **Experimental features** enabled: remote functions and async compiler options

## Adding New Stories

1. Create story directory in `src/lib/stories/[new-story-slug]/`
2. Add required `components/Index.svelte` and `data/copy.json`
3. Add story entry to `src/data/stories.csv` with required fields:
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
- **Key Utilities**: 
  - `storyRegistry.js` - Dynamic story component loading system
  - `duckdb.js` - DuckDB WASM initialization and query utilities
  - `filterStoryProps.js` - Story metadata filtering for display
  - Various data processing utilities (slugify, tokenize, numberAsText, etc.)

## Story Development Workflow

1. Check existing stories in `src/lib/stories/` for patterns and conventions
2. Use the GitHub issue template for story proposals and planning
3. Follow the story structure with required `components/Index.svelte` and `data/copy.json`
4. Test stories thoroughly in development mode before adding to `stories.csv`
5. Consider technical features that showcase best practices in data science and software development