---
name: frontend-design
description: Build interactive data stories for Complex Stories using SvelteKit 2, Svelte 5 runes, D3.js visualizations, and scrollytelling patterns. Use when tasks involve creating new stories, building interactive visualizations, implementing scrolly-based narratives, adding Svelte 5 reactive components, styling stories, or working with D3.js integrations. Also use for questions about story structure, component patterns, or responsive design.
---

# Frontend Design for Complex Stories

This skill guides creation of interactive data stories following the Complex Stories platform's patterns: SvelteKit 2 + Svelte 5 runes + D3.js + scrollytelling.

## Architecture Overview

**Story Flow:**
1. **Structure**: Each story in `frontend/src/lib/stories/[story-slug]/`
2. **Components**: Index.svelte entry point + child components
3. **Data**: Static (JSON/CSV) or dynamic (remote functions)
4. **State**: Svelte 5 runes ($state, $derived, $effect)
5. **Visualization**: D3.js scales + SVG rendering
6. **Narrative**: Scrollytelling with sticky visualizations

**Technologies:**
- **SvelteKit 2**: Node.js adapter with remote functions
- **Svelte 5**: Runes syntax ($state, $derived, $effect, $props)
- **D3.js**: Scales, colors, data manipulation
- **CSS**: Story-scoped with :global() selectors
- **Vite**: Path aliases ($lib, $stories, $data)

## Quick Reference

### Story Directory Structure
```
frontend/src/lib/stories/[story-slug]/
├── components/
│   └── Index.svelte              # Main entry point
├── data/
│   ├── copy.json                 # Story text and metadata
│   ├── data.remote.js            # API calls (optional)
│   └── [data-files].{json,csv}   # Static data
├── utils/                        # Story utilities (optional)
│   ├── dynamics.ts               # Simulation logic
│   └── colorScales.js            # D3 scales
└── state.svelte.ts               # Centralized state (optional)
```

### Key Patterns
- **Routing**: `/[slug]/+page.svelte` loads story via `Index.svelte`
- **Content**: All text in `copy.json`, rendered with shared snippets
- **Responsive**: Use `innerWidth.current` from `svelte/reactivity/window`
- **Styling**: Story-scoped with `:global(body:has(#story-id))`
- **State**: Svelte 5 runes for all reactivity

## Creating a New Story

### 1. Initialize Story Structure

Create directory structure:

```bash
cd frontend/src/lib/stories
mkdir -p my-story/components my-story/data
touch my-story/components/Index.svelte
touch my-story/data/copy.json
```

### 2. Create copy.json

**File:** `frontend/src/lib/stories/my-story/data/copy.json`

```json
{
  "title": "Story Title",
  "subtitle": "Story subtitle text",
  "author1": "<a href='...'>Author Name</a>",
  "date": "Jan 12, 2026",
  "intro": [
    {
      "type": "markdown",
      "value": "Introduction paragraph with **markdown** support."
    },
    {
      "type": "component",
      "component": "custom-viz"
    }
  ],
  "steps": [
    {
      "type": "markdown",
      "value": "Step 1 text for scrollytelling"
    },
    {
      "type": "html",
      "value": "<p>Raw HTML if needed</p>"
    }
  ]
}
```

**Content Types:**
- `markdown`: Rendered with Markdown parser
- `html`: Raw HTML (use {@html} in Svelte)
- `component`: Reference to custom component
- `math`: Markdown with LaTeX support

### 3. Create Index.svelte

**File:** `frontend/src/lib/stories/my-story/components/Index.svelte`

```svelte
<script>
  import { innerWidth } from 'svelte/reactivity/window';
  import { base } from '$app/paths';
  import Scrolly from '$lib/components/helpers/Scrolly.svelte';
  import Md from '$lib/components/Md.svelte';
  import myData from '../data/data.json';

  // Props from page load
  let { story, data } = $props();

  // Reactive state
  let scrollyIndex = $state();
  let isMobile = $derived(innerWidth.current <= 768);

  // Derived visualization data
  let vizData = $derived.by(() => {
    if (!myData) return [];
    return myData.filter(d => d.visible);
  });

  // Side effects
  $effect(() => {
    console.log('Scrolly step changed:', scrollyIndex);
  });
</script>

<main id="my-story">
  <header>
    <h1>{data.title}</h1>
    <p class="subtitle">{data.subtitle}</p>
    <p class="meta">{@html data.author1} · {data.date}</p>
  </header>

  <section>
    {#each data.intro as item}
      {#if item.type === "markdown"}
        <Md text={item.value} />
      {:else if item.type === "html"}
        {@html item.value}
      {/if}
    {/each}
  </section>

  {#if !isMobile}
    <section class="scrolly-section">
      <div class="viz-container">
        <!-- Sticky visualization -->
      </div>

      <div class="steps-container">
        <Scrolly bind:value={scrollyIndex}>
          {#each data.steps as step, i}
            {@const active = scrollyIndex === i}
            <div class="step" class:active>
              <Md text={step.value} />
            </div>
          {/each}
        </Scrolly>
      </div>
    </section>
  {:else}
    <!-- Mobile fallback -->
    {#each data.steps as step, i}
      <div class="mobile-step">
        <img src="{base}/screenshots/step-{i}.jpg" alt="Step {i}" />
        <Md text={step.value} />
      </div>
    {/each}
  {/if}
</main>

<style>
  /* Story-scoped global overrides */
  :global(body:has(#my-story)) {
    background-color: #f5f5f5;
  }

  main {
    max-width: var(--width-column-regular);
    margin: 0 auto;
    padding: 2rem 1rem;
  }

  header {
    text-align: center;
    margin-bottom: 3rem;
  }

  h1 {
    font-size: var(--font-size-xlarge);
    margin-bottom: 0.5rem;
  }

  .scrolly-section {
    position: relative;
    margin: 4rem 0;
  }

  .viz-container {
    position: sticky;
    top: calc(50vh - 300px);
    width: 45%;
    float: right;
    margin-left: 5%;
  }

  .steps-container {
    width: 45%;
    float: left;
  }

  .step {
    min-height: 80vh;
    display: flex;
    align-items: center;
    opacity: 0.3;
    transition: opacity 300ms ease;
  }

  .step.active {
    opacity: 1;
  }

  @media (max-width: 768px) {
    .mobile-step {
      margin: 2rem 0;
    }

    .mobile-step img {
      width: 100%;
      height: auto;
      margin-bottom: 1rem;
    }
  }
</style>
```

### 4. Register Story

**File:** `frontend/src/data/stories.csv`

Add row:
```csv
my-story,My Story Title,Story description,author-name,2026-01-12,true,popular,false,#ffffff,#000000,data visualization interactive
```

**Columns:**
- `slug`: URL slug (matches directory name)
- `title`: Display title
- `description`: SEO description
- `author`: Author slug
- `date`: Publication date
- `external`: Is external link (false for local stories)
- `filters`: Category (popular, in_theory, dashboard, dataset)
- `faves`: Featured on homepage
- `bgColor`: Background color hex
- `fgColor`: Foreground/text color hex
- `keyword`: Space-separated tags

## Svelte 5 Runes Patterns

### $state - Reactive State

```javascript
// Simple values
let count = $state(0);
let isVisible = $state(false);
let selectedAuthor = $state('Peter Sheridan Dodds');

// Objects (reactive by default)
let surveyAnswers = $state({
  question1: '',
  question2: [],
  question3: null
});

// Arrays
let items = $state([1, 2, 3]);
items.push(4); // Reactive mutation
```

### $derived - Computed Values

```javascript
// Simple derivation
let doubled = $derived(count * 2);
let isMobile = $derived(innerWidth.current <= 768);

// Complex derivation with .by()
let filteredData = $derived.by(() => {
  if (!data?.length) return [];

  return data
    .filter(d => d.year >= minYear)
    .sort((a, b) => b.value - a.value)
    .slice(0, 10);
});

// Chained derivations
let maxValue = $derived(Math.max(...filteredData.map(d => d.value)));
let colorScale = $derived(
  d3.scaleSequential(d3.interpolateViridis)
    .domain([0, maxValue])
);
```

### $effect - Side Effects

```javascript
// Run when dependencies change
$effect(() => {
  console.log('Count changed:', count);
});

// With cleanup
$effect(() => {
  const interval = setInterval(() => {
    count++;
  }, 1000);

  return () => clearInterval(interval);
});

// IntersectionObserver pattern
$effect(() => {
  if (typeof window !== 'undefined' && elementRef) {
    const observer = new IntersectionObserver((entries) => {
      isVisible = entries[0].isIntersecting;
    }, { threshold: 0.5 });

    observer.observe(elementRef);
    return () => observer.disconnect();
  }
});

// Scrolly state updates
$effect(() => {
  switch (scrollyIndex) {
    case 0:
      resetVisualization();
      break;
    case 1:
      highlightNodes();
      break;
    case 2:
      animateTransition();
      break;
  }
});
```

### $props - Component Props

```javascript
// Destructure props
let { story, data, width = 500, height = 400 } = $props();

// With TypeScript
let {
  nodes,
  links,
  onNodeClick
}: {
  nodes: Node[],
  links: Link[],
  onNodeClick?: (node: Node) => void
} = $props();
```

### $bindable - Two-Way Binding

```javascript
// In child component (Scrolly.svelte)
let {
  value = $bindable(undefined),
  scrollProgress = $bindable(0)
} = $props();

// Parent can bind
<Scrolly bind:value={scrollyIndex} bind:scrollProgress />
```

## D3.js Integration Patterns

### Creating Scales

```javascript
import * as d3 from 'd3';

// In utils/colorScales.js
export const ageColorScale = d3.scaleOrdinal()
  .domain(['older', 'same', 'younger', null])
  .range(['#8e6dfb', '#20A387FF', '#dacc55', 'lightgrey']);

export function createRadiusScale(data) {
  const values = data.map(d => d.count);
  return d3.scaleSqrt()
    .domain(d3.extent(values))
    .range([2, 20])
    .clamp(true);
}

// In component
import { ageColorScale, createRadiusScale } from '../utils/colorScales.js';

let radiusScale = $derived.by(() => {
  if (!data?.length) return null;
  return createRadiusScale(data);
});
```

### Common D3 Scales

```javascript
// Sequential color scale
let colorScale = $derived(
  d3.scaleSequential(d3.interpolateViridis)
    .domain([minValue, maxValue])
);

// Ordinal scale with built-in colors
let categoryColors = $derived(
  d3.scaleOrdinal(d3.schemeCategory10)
    .domain(categories)
);

// Linear scale for positioning
let xScale = $derived(
  d3.scaleLinear()
    .domain([0, maxX])
    .range([0, width])
);

// Time scale
let timeScale = $derived(
  d3.scaleTime()
    .domain([startDate, endDate])
    .range([0, width])
);

// Threshold scale
let sizeScale = $derived(
  d3.scaleThreshold()
    .domain([10, 50, 100])
    .range(['small', 'medium', 'large', 'xlarge'])
);
```

### SVG Rendering with D3 Data

```svelte
<svg {width} {height}>
  <g transform="translate({margin.left}, {margin.top})">
    {#each data as d}
      {@const x = xScale(d.value)}
      {@const y = yScale(d.category)}
      {@const color = colorScale(d.value)}

      <circle
        cx={x}
        cy={y}
        r={radiusScale(d.count)}
        fill={color}
        opacity={0.7}
        onclick={() => handleClick(d)}
        style="cursor: pointer; transition: r 300ms ease;"
      />

      <text
        x={x}
        y={y}
        text-anchor="middle"
        dy="0.3em"
        font-size="12"
        fill="#333"
      >
        {d.label}
      </text>
    {/each}
  </g>
</svg>
```

### D3 Force Simulations

```javascript
// In utils/forceLayout.js
import * as d3 from 'd3';

export function createForceSimulation(nodes, links, width, height) {
  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(50))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(d => d.radius + 2));

  return simulation;
}

// In component
import { createForceSimulation } from '../utils/forceLayout.js';

let simulation = $state(null);
let positions = $state([]);

$effect(() => {
  if (nodes && links) {
    simulation = createForceSimulation(nodes, links, width, height);

    simulation.on('tick', () => {
      positions = nodes.map(n => ({ id: n.id, x: n.x, y: n.y }));
    });
  }

  return () => simulation?.stop();
});
```

## Scrollytelling Patterns

### Basic Scrolly Setup

```svelte
<script>
  import Scrolly from '$lib/components/helpers/Scrolly.svelte';

  let scrollyIndex = $state();

  $effect(() => {
    console.log('Step:', scrollyIndex);
  });
</script>

<section class="scrolly-section">
  <div class="viz-sticky">
    <!-- Visualization that changes based on scrollyIndex -->
  </div>

  <div class="steps">
    <Scrolly bind:value={scrollyIndex}>
      {#each steps as step, i}
        <div class="step" class:active={scrollyIndex === i}>
          <Md text={step.value} />
        </div>
      {/each}
    </Scrolly>
  </div>
</section>

<style>
  .scrolly-section {
    position: relative;
  }

  .viz-sticky {
    position: sticky;
    top: calc(50vh - 300px);
    width: 45%;
    float: right;
    margin-left: 5%;
  }

  .steps {
    width: 45%;
    float: left;
  }

  .step {
    min-height: 80vh;
    display: flex;
    align-items: center;
    opacity: 0.3;
    transition: opacity 300ms ease;
  }

  .step.active {
    opacity: 1;
  }
</style>
```

### Progressive Visualization States

```javascript
let vizState = $derived.by(() => {
  if (!data) return null;

  switch (scrollyIndex) {
    case 0:
      // Initial state: all nodes centered
      return {
        nodes: data.nodes.map(n => ({ ...n, x: width/2, y: height/2 })),
        highlight: null
      };

    case 1:
      // Spread nodes out
      return {
        nodes: data.nodes.map((n, i) => ({
          ...n,
          x: (width / data.nodes.length) * i,
          y: height / 2
        })),
        highlight: null
      };

    case 2:
      // Highlight subset
      return {
        nodes: data.nodes,
        highlight: data.nodes.filter(n => n.category === 'A')
      };

    default:
      return { nodes: data.nodes, highlight: null };
  }
});
```

### Mobile Fallback Pattern

```svelte
<script>
  import { base } from '$app/paths';
  import { innerWidth } from 'svelte/reactivity/window';

  let isMobile = $derived(innerWidth.current <= 768);
</script>

{#if isMobile}
  <!-- Static images for mobile -->
  {#each steps as step, i}
    <div class="mobile-step">
      <img
        src="{base}/screenshots/my-story-step-{i}.jpg"
        alt="Step {i}"
      />
      <Md text={step.value} />
    </div>
  {/each}
{:else}
  <!-- Interactive scrolly for desktop -->
  <section class="scrolly-section">
    <!-- ... scrolly content ... -->
  </section>
{/if}
```

## State Management Patterns

### Simple Component State

For simple stories, use local component state:

```javascript
let selectedCategory = $state('all');
let hoveredNode = $state(null);
let isPlaying = $state(false);

let filteredData = $derived.by(() => {
  if (selectedCategory === 'all') return data;
  return data.filter(d => d.category === selectedCategory);
});
```

### Centralized State File

For complex dashboards, use `state.svelte.ts`:

**File:** `frontend/src/lib/stories/my-story/state.svelte.ts`

```typescript
import { loadPaperData } from './data.remote.js';

// Dashboard controls
export const dashboardState = $state({
  selectedAuthor: 'Peter Sheridan Dodds',
  selectedCollege: 'All',
  nodeColorBy: 'age_diff',
  nodeSizeBy: 'cited_by_count',
  filterBigPapers: true
});

// Loaded data
export const data = $state({
  isInitializing: true,
  papers: null,
  authors: null
});

// Derived data using class pattern
class DerivedData {
  filteredPapers = $derived.by(() => {
    if (!data.papers) return [];

    let papers = data.papers;

    if (dashboardState.filterBigPapers) {
      papers = papers.filter(p => p.cited_by_count < 1000);
    }

    return papers;
  });

  maxCitations = $derived(
    Math.max(...this.filteredPapers.map(p => p.cited_by_count))
  );
}

export const derived = new DerivedData();

// Actions
export async function initializeApp() {
  data.isInitializing = true;
  data.authors = await loadAvailableAuthors();
  data.isInitializing = false;
}

export async function loadSelectedAuthor() {
  data.papers = await loadPaperData({
    authorName: dashboardState.selectedAuthor,
    filterBigPapers: dashboardState.filterBigPapers
  });
}
```

**Usage in component:**

```svelte
<script>
  import { dashboardState, data, derived, initializeApp, loadSelectedAuthor }
    from '../state.svelte';

  initializeApp();

  $effect(() => {
    if (dashboardState.selectedAuthor && !data.isInitializing) {
      loadSelectedAuthor();
    }
  });
</script>

<select bind:value={dashboardState.selectedAuthor}>
  {#each data.authors as author}
    <option value={author.name}>{author.name}</option>
  {/each}
</select>

<p>Max citations: {derived.maxCitations}</p>
```

## Data Loading Patterns

### Static Data Imports

```javascript
// JSON
import myData from '../data/data.json';

// CSV (parsed via @rollup/plugin-dsv)
import nodes from '../data/nodes.csv';

// Use directly
{#each nodes as node}
  <p>{node.name}: {node.value}</p>
{/each}
```

### Remote Functions

**File:** `frontend/src/lib/stories/my-story/data/data.remote.js`

```javascript
import { query, command } from '$app/server';
import { API_BASE } from '$env/static/private';
import * as v from 'valibot';

const API_BASE_URL = API_BASE || 'http://localhost:3001';

// Query (read)
export const loadPapers = query(
  v.object({
    authorName: v.string(),
    filterBigPapers: v.boolean()
  }),
  async ({ authorName, filterBigPapers }) => {
    const response = await fetch(
      `${API_BASE_URL}/open-academic-analytics/papers/${authorName}?filter_big_papers=${filterBigPapers}`
    );
    if (!response.ok) throw new Error('Failed to load papers');
    return response.json();
  }
);

// Command (write)
export const saveSurveyResponse = command(
  v.object({
    fingerprint: v.string(),
    field: v.string(),
    value: v.union([v.string(), v.number()])
  }),
  async (data) => {
    const response = await fetch(
      `${API_BASE_URL}/my-story/save`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      }
    );
    return response.json();
  }
);
```

**Usage:**

```javascript
import { loadPapers } from '../data/data.remote.js';

let papers = $state(null);

async function fetchData() {
  papers = await loadPapers({
    authorName: 'Peter Dodds',
    filterBigPapers: true
  });
}
```

### Async Data with Loading States

```svelte
<script>
  const dataPromise = loadData();
</script>

{#await dataPromise}
  <div class="loading">
    <Spinner />
    <p>Loading data...</p>
  </div>
{:then data}
  <Visualization {data} />
{:catch error}
  <div class="error">
    <p>Error loading data: {error.message}</p>
  </div>
{/await}
```

## Styling Patterns

### Story-Scoped Global Overrides

```css
/* Override only when this story is present */
:global(body:has(#my-story)) {
  background-color: #f5f5f5;
  font-family: var(--serif);
}

/* Change main width for this story */
:global(main#content:has(#my-story)) {
  max-width: var(--width-column-wide);
}

/* Story-specific heading styles */
:global(#my-story h1) {
  font-size: var(--font-size-giant);
  color: var(--color-uvm-green);
  text-align: center;
}
```

### Responsive Breakpoints

```css
@media (max-width: 1200px) {
  .viz-sticky {
    width: 100%;
    position: relative;
    top: 0;
    float: none;
    margin: 2rem auto;
  }

  .steps {
    width: 100%;
  }
}

@media (max-width: 768px) {
  h1 {
    font-size: 2rem !important;
  }

  .step {
    min-height: 100vh;
    font-size: 1.2rem;
  }
}
```

### Transitions

```css
/* Smooth opacity transitions */
.element {
  opacity: 0.3;
  transition: opacity 300ms ease;
}

.element.active {
  opacity: 1;
}

/* SVG transitions (scoped with :global) */
:global(.my-viz circle) {
  transition:
    cx 500ms cubic-bezier(0.76, 0, 0.24, 1),
    cy 500ms cubic-bezier(0.76, 0, 0.24, 1),
    r 300ms ease,
    fill 300ms ease;
}
```

## Common Patterns

### Interactive Survey

See [dark-data-survey](../../frontend/src/lib/stories/dark-data-survey/) for complete example:
- Browser fingerprinting with @fingerprintjs/fingerprintjs
- UPSERT via remote functions
- Progressive question reveal based on scroll
- Privacy consent tracking

### Network Visualization

See [networks-fast-and-slow](../../frontend/src/lib/stories/networks-fast-and-slow/) for complete example:
- D3 force simulation
- Scroll-driven animation states
- Node infection/highlighting
- Dynamic link rewiring

### Dashboard with Filters

See [open-academic-analytics](../../frontend/src/lib/stories/open-academic-analytics/) for complete example:
- Centralized state management
- Multiple linked visualizations
- Filter controls
- Remote data loading

## Best Practices

1. **State Management**: Use $state for mutable, $derived for computed, $effect for side effects
2. **Responsive**: Always provide mobile fallbacks (static images for complex interactives)
3. **Content**: Store all text in copy.json, render with shared snippets
4. **Styling**: Use story-scoped :global() to avoid style leakage
5. **D3 Integration**: Create scales as $derived values, render with Svelte {#each}
6. **Performance**: Avoid expensive computations in render, use $derived.by() for filtering
7. **Accessibility**: Add aria labels, keyboard navigation, focus states
8. **Loading**: Show loading states with {#await} or isLoading flag
9. **Scrolly**: Use sticky positioning, clear active states, test on mobile
10. **Reusability**: Extract common logic to utils/, scales to colorScales.js

## Reference Stories

Study these complete examples:
- **dark-data-survey**: Survey with fingerprinting
- **open-academic-analytics**: Dashboard with remote data
- **networks-fast-and-slow**: Network simulation with scrolly
- **allotax-scrolly**: Complex scrollytelling with multiple states
- **tokenization**: Multiple scrolly sections in one story
