# Complex Stories

A scientific data storytelling platform built with SvelteKit, showcasing interactive visualizations and computational science research from the Vermont Complex Systems Institute. Inspired by [The Pudding](https://pudding.cool/).

## 🚀 Features

- **Interactive Data Stories**: Rich, scrollable narratives with embedded visualizations
- **Dual Story Types**: Internal stories built with Svelte components and external story links
- **Scientific Focus**: Computational science, complex systems, and data-driven research

## 🛠️ Tech Stack

- **Framework**: SvelteKit 2 with Svelte 5 (runes syntax)
- **Visualization**: D3.js for data visualization and manipulation
- **Data Processing**: DuckDB WASM for client-side data analysis
- **Styling**: Custom CSS (no framework) with story-specific aesthetics
- **Content**: Markdown with mathematical notation support (KaTeX)
- **Build**: Vite with custom plugins for CSV/TSV data loading
- **Deployment**: Static site generation via `@sveltejs/adapter-static`

## 🏗️ Project Structure

```
src/
├── lib/
│   ├── stories/                    # Story implementations
│   │   └── [story-slug]/
│   │       ├── components/
│   │       │   └── Index.svelte    # Main story component
│   │       ├── data/
│   │       │   ├── copy.json       # Story content and metadata
│   │       │   └── [data-files]    # Story-specific datasets
│   │       ├── utils/              # Story utilities (optional)
│   │       └── state.svelte.ts     # Story state management (optional)
│   ├── components/                 # Shared components
│   └── utils/                      # Global utilities
├── data/                          # Global data files
│   ├── stories.csv                # Story registry and metadata
│   ├── authors.csv                # Author information
│   └── [other-data].csv           # Additional datasets
├── routes/                        # SvelteKit routes
└── styles/                        # Global CSS files
```

## 🚦 Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd complex-stories
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The site will be available at `http://localhost:5173`

## 📝 Development Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with hot reloading |
| `npm run build` | Build for production (static site generation) |
| `npm run preview` | Preview production build locally |
| `npm run check` | Run TypeScript type checking |
| `npm run check:watch` | Type checking in watch mode |
| `npm run format` | Format code with Prettier |
| `npm run lint` | Check code formatting |

## 📚 Creating a New Story

1. **Create the story directory structure**:
```bash
mkdir -p src/lib/stories/my-new-story/{components,data}
```

2. **Create the main component** (`src/lib/stories/my-new-story/components/Index.svelte`):
```svelte
<script>
  import copy from '../data/copy.json';
</script>

<article>
  <h1>{copy.title}</h1>
  <p>{copy.subtitle}</p>
  <!-- Your story content here -->
</article>
```

3. **Create the story metadata** (`src/lib/stories/my-new-story/data/copy.json`):
```json
{
  "title": "My New Story",
  "subtitle": "An engaging subtitle",
  "author": "Your Name",
  "date": "2025-01-15"
}
```

4. **Register the story** in `src/data/stories.csv`:
```csv
url,external,hed,dek,author,date,bgColor,fgColor,keyword,filters,faves
my-new-story,false,My New Story,An engaging subtitle,Your Name,1/15/2025,#e3f2fd,#000000,research,dashboard,false
```

5. **Test your story** by navigating to `/my-new-story` in development mode.

## 🎨 Styling Guidelines

- **No CSS Framework**: Each story defines its own aesthetic
- **Global Styles**: Common elements in `src/styles/`
- **Component Styles**: Use Svelte's `<style>` blocks for component-specific styling
- **Story Styles**: Define story-wide styles in the main `Index.svelte` component
- **Responsive Design**: Mobile-first approach with appropriate breakpoints

## 📊 Working with Data

### CSV/TSV Files
Import data files directly as JavaScript objects:
```javascript
import myData from '$data/my-dataset.csv';
```

### DuckDB for Analysis
Use DuckDB WASM for complex data processing:
```javascript
import { getDuckDB } from '$lib/utils/duckdb.js';

const db = await getDuckDB();
const result = await db.query('SELECT * FROM my_table');
```

### Data Aliases
- `$data` → `src/data/`
- `$styles` → `src/styles/`

## 🔧 Advanced Features

### State Management
For complex stories, create a `state.svelte.ts` file using Svelte 5 runes:
```typescript
export const storyState = $state({
  currentStep: 0,
  selectedData: null,
  // ... other state
});
```

### External Stories
Link to external content by setting `external: true` in `stories.csv` and providing a `url_alt` field.

### Mathematical Notation
Stories support LaTeX math notation via KaTeX:
```json
{
  "type": "math",
  "value": "$E = mc^2$"
}
```

## 🚀 Deployment

The project builds to a static site that can be deployed to any static hosting service:

```bash
npm run build
```

Built files will be in the `build/` directory.

### Story Guidelines
- Focus on scientific accuracy and engaging presentation
- Include interactive elements where appropriate
- Provide clear data sources and methodology
- Follow accessibility best practices
- Test on both desktop and mobile devices

## 🙏 Acknowledgments

- Inspired by [The Pudding](https://pudding.cool/)
- Built by the [Vermont Complex Systems Institute](https://vermontcomplexsystems.org/)
- Powered by the Svelte ecosystem
