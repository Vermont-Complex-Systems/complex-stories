# D3.js + Svelte 5 Integration Patterns

This reference covers best practices for integrating D3.js with Svelte 5 in Complex Stories.

## Core Philosophy

**Svelte handles DOM, D3 handles data.**

- ✅ Use D3 for: scales, colors, layouts, data manipulation, math
- ✅ Use Svelte for: rendering SVG elements, reactivity, user interaction
- ❌ Avoid: D3 DOM manipulation (`.append()`, `.select()`, etc.)

---

## Table of Contents

1. [Scales and Color Schemes](#scales)
2. [SVG Rendering Patterns](#svg-rendering)
3. [Force Simulations](#force-simulations)
4. [Layouts and Generators](#layouts)
5. [Data Manipulation](#data-manipulation)
6. [Transitions and Animations](#transitions)
7. [Axes and Legends](#axes-legends)
8. [Performance Optimization](#performance)

---

## Scales and Color Schemes {#scales}

### Creating Reusable Scales

**File:** `utils/colorScales.js`

```javascript
import * as d3 from 'd3';

// Static ordinal scale
export const ageColorScale = d3.scaleOrdinal()
  .domain(['older', 'same', 'younger', null])
  .range(['#8e6dfb', '#20A387FF', '#dacc55', 'lightgrey']);

// Threshold scale
export const collaborationScale = d3.scaleThreshold()
  .domain([2, 5, 10])
  .range(['#fee5d9', '#fcae91', '#fb6a4a', '#cb181d']);

// Factory function for dynamic scales
export function createRadiusScale(data) {
  const values = data.map(d => d.count);
  return d3.scaleSqrt()
    .domain(d3.extent(values))
    .range([2, 20])
    .clamp(true);
}

export function createInstitutionColorScale(institutions) {
  return d3.scaleOrdinal(d3.schemeCategory10)
    .domain(institutions);
}
```

### Using Scales in Components

```svelte
<script>
  import * as d3 from 'd3';
  import { ageColorScale, createRadiusScale } from '../utils/colorScales.js';

  let { data } = $props();

  // Reactive scale based on data
  let radiusScale = $derived.by(() => {
    if (!data?.length) return null;
    return createRadiusScale(data);
  });

  // Sequential color scale
  let colorScale = $derived.by(() => {
    const values = data.map(d => d.value);
    return d3.scaleSequential(d3.interpolateViridis)
      .domain(d3.extent(values));
  });

  // Linear position scale
  let xScale = $derived(
    d3.scaleLinear()
      .domain([0, d3.max(data, d => d.x)])
      .range([0, width])
  );
</script>

<svg {width} {height}>
  {#each data as d}
    <circle
      cx={xScale(d.x)}
      cy={yScale(d.y)}
      r={radiusScale(d.count)}
      fill={colorScale(d.value)}
    />
  {/each}
</svg>
```

### Common Scale Types

```javascript
// Linear scale
d3.scaleLinear()
  .domain([0, 100])      // Data space
  .range([0, 500])       // Pixel space

// Square root scale (better for area)
d3.scaleSqrt()
  .domain([0, 100])
  .range([2, 20])

// Log scale
d3.scaleLog()
  .domain([1, 1000])
  .range([0, 500])

// Time scale
d3.scaleTime()
  .domain([new Date(2020, 0, 1), new Date(2025, 0, 1)])
  .range([0, 500])

// Ordinal scale
d3.scaleOrdinal()
  .domain(['A', 'B', 'C'])
  .range(['red', 'blue', 'green'])

// Band scale (for bar charts)
d3.scaleBand()
  .domain(['A', 'B', 'C'])
  .range([0, 500])
  .padding(0.1)

// Sequential scale (continuous color)
d3.scaleSequential(d3.interpolateViridis)
  .domain([0, 100])

// Quantize scale (discrete buckets)
d3.scaleQuantize()
  .domain([0, 100])
  .range(['low', 'medium', 'high'])

// Threshold scale
d3.scaleThreshold()
  .domain([10, 50])  // Break points
  .range(['small', 'medium', 'large'])
```

### Color Schemes

```javascript
// Categorical colors
d3.schemeCategory10          // 10 distinct colors
d3.schemeAccent              // 8 colors
d3.schemePaired              // 12 colors
d3.schemeSet1                // 9 colors

// Sequential (single hue)
d3.interpolateBlues          // Light to dark blue
d3.interpolateGreens
d3.interpolateReds

// Sequential (multi-hue)
d3.interpolateViridis        // Purple to yellow
d3.interpolatePlasma         // Purple to yellow (brighter)
d3.interpolateInferno        // Black to yellow
d3.interpolateTurbo          // Blue to red (rainbow)

// Diverging (two-hue)
d3.interpolateRdYlGn         // Red to yellow to green
d3.interpolatePiYG           // Pink to yellow-green
d3.interpolateBrBG           // Brown to teal

// Usage
let colorScale = d3.scaleSequential(d3.interpolateViridis)
  .domain([0, 100]);

let categoryColors = d3.scaleOrdinal(d3.schemeCategory10)
  .domain(categories);
```

---

## SVG Rendering Patterns {#svg-rendering}

### Basic SVG Structure

```svelte
<script>
  import * as d3 from 'd3';

  let { data, width = 600, height = 400 } = $props();

  const margin = { top: 20, right: 20, bottom: 30, left: 40 };
  let innerWidth = $derived(width - margin.left - margin.right);
  let innerHeight = $derived(height - margin.top - margin.bottom);

  let xScale = $derived(
    d3.scaleLinear()
      .domain([0, d3.max(data, d => d.x)])
      .range([0, innerWidth])
  );

  let yScale = $derived(
    d3.scaleLinear()
      .domain([0, d3.max(data, d => d.y)])
      .range([innerHeight, 0])  // Inverted for SVG
  );
</script>

<svg {width} {height}>
  <g transform="translate({margin.left}, {margin.top})">
    <!-- Render data -->
    {#each data as d}
      <circle
        cx={xScale(d.x)}
        cy={yScale(d.y)}
        r={5}
        fill="steelblue"
      />
    {/each}
  </g>
</svg>
```

### Scatterplot Pattern

```svelte
<script>
  import * as d3 from 'd3';

  let { data, width = 600, height = 400 } = $props();

  let colorScale = $derived(
    d3.scaleOrdinal(d3.schemeCategory10)
      .domain([...new Set(data.map(d => d.category))])
  );

  let radiusScale = $derived(
    d3.scaleSqrt()
      .domain(d3.extent(data, d => d.size))
      .range([3, 15])
  );
</script>

<svg {width} {height}>
  {#each data as point}
    {@const x = xScale(point.x)}
    {@const y = yScale(point.y)}
    {@const r = radiusScale(point.size)}
    {@const fill = colorScale(point.category)}

    <circle
      cx={x}
      cy={y}
      r={r}
      fill={fill}
      opacity={0.7}
      stroke="#333"
      stroke-width={1}
      onclick={() => handleClick(point)}
      style="cursor: pointer;"
    />
  {/each}
</svg>
```

### Bar Chart Pattern

```svelte
<script>
  import * as d3 from 'd3';

  let { data, width = 600, height = 400 } = $props();

  let xScale = $derived(
    d3.scaleBand()
      .domain(data.map(d => d.category))
      .range([0, width])
      .padding(0.1)
  );

  let yScale = $derived(
    d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value)])
      .range([height, 0])
  );
</script>

<svg {width} {height}>
  {#each data as d}
    {@const x = xScale(d.category)}
    {@const y = yScale(d.value)}
    {@const barHeight = height - y}

    <rect
      x={x}
      y={y}
      width={xScale.bandwidth()}
      height={barHeight}
      fill="steelblue"
    />

    <text
      x={x + xScale.bandwidth() / 2}
      y={y - 5}
      text-anchor="middle"
      font-size="12"
    >
      {d.value}
    </text>
  {/each}
</svg>
```

### Line Chart Pattern

```svelte
<script>
  import * as d3 from 'd3';

  let { data, width = 600, height = 400 } = $props();

  let xScale = $derived(
    d3.scaleTime()
      .domain(d3.extent(data, d => d.date))
      .range([0, width])
  );

  let yScale = $derived(
    d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value)])
      .range([height, 0])
  );

  // Generate line path
  let linePath = $derived.by(() => {
    const line = d3.line()
      .x(d => xScale(d.date))
      .y(d => yScale(d.value))
      .curve(d3.curveMonotoneX);  // Smooth curve

    return line(data);
  });

  // Generate area path (optional)
  let areaPath = $derived.by(() => {
    const area = d3.area()
      .x(d => xScale(d.date))
      .y0(height)
      .y1(d => yScale(d.value))
      .curve(d3.curveMonotoneX);

    return area(data);
  });
</script>

<svg {width} {height}>
  <!-- Area -->
  <path
    d={areaPath}
    fill="steelblue"
    opacity={0.3}
  />

  <!-- Line -->
  <path
    d={linePath}
    stroke="steelblue"
    stroke-width={2}
    fill="none"
  />

  <!-- Points -->
  {#each data as d}
    <circle
      cx={xScale(d.date)}
      cy={yScale(d.value)}
      r={3}
      fill="steelblue"
    />
  {/each}
</svg>
```

---

## Force Simulations {#force-simulations}

### Basic Force Layout

```javascript
// utils/forceLayout.js
import * as d3 from 'd3';

export function createForceSimulation(nodes, links, width, height) {
  // Clone nodes to avoid mutation
  const nodesCopy = nodes.map(n => ({ ...n }));

  const simulation = d3.forceSimulation(nodesCopy)
    .force('link', d3.forceLink(links)
      .id(d => d.id)
      .distance(50))
    .force('charge', d3.forceManyBody()
      .strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide()
      .radius(d => d.radius + 2));

  return simulation;
}
```

### Using Force Simulation in Component

```svelte
<script>
  import { createForceSimulation } from '../utils/forceLayout.js';

  let { nodes, links, width, height } = $props();

  let simulation = $state(null);
  let positions = $state([]);

  $effect(() => {
    if (!nodes || !links) return;

    simulation = createForceSimulation(nodes, links, width, height);

    // Update positions on each tick
    simulation.on('tick', () => {
      positions = simulation.nodes().map(n => ({
        id: n.id,
        x: n.x,
        y: n.y
      }));
    });

    // Stop after 300 iterations for performance
    simulation.tick(300);

    // Cleanup
    return () => {
      simulation.stop();
    };
  });

  // Find position for each node
  function getNodePosition(nodeId) {
    return positions.find(p => p.id === nodeId) || { x: 0, y: 0 };
  }
</script>

<svg {width} {height}>
  <!-- Links -->
  {#each links as link}
    {@const source = getNodePosition(link.source.id || link.source)}
    {@const target = getNodePosition(link.target.id || link.target)}

    <line
      x1={source.x}
      y1={source.y}
      x2={target.x}
      y2={target.y}
      stroke="#999"
      stroke-width={1}
    />
  {/each}

  <!-- Nodes -->
  {#each nodes as node}
    {@const pos = getNodePosition(node.id)}

    <circle
      cx={pos.x}
      cy={pos.y}
      r={node.radius || 5}
      fill={node.color || 'steelblue'}
    />
  {/each}
</svg>
```

### Custom Radial Layout

```javascript
// utils/radialLayout.js
export function radialLayout({ nodes, links, width, height }) {
  const radius = Math.min(width, height) / 2 - 50;
  const centerX = width / 2;
  const centerY = height / 2;

  // Find the main node (highest degree)
  const degrees = new Map();
  links.forEach(link => {
    degrees.set(link.source, (degrees.get(link.source) || 0) + 1);
    degrees.set(link.target, (degrees.get(link.target) || 0) + 1);
  });

  const mainNodeId = Array.from(degrees.entries())
    .sort((a, b) => b[1] - a[1])[0][0];

  return nodes.map((node, i) => {
    if (node.id === mainNodeId) {
      return { ...node, x: centerX, y: centerY };
    }

    const angle = (2 * Math.PI * i) / (nodes.length - 1);
    return {
      ...node,
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle)
    };
  });
}
```

---

## Layouts and Generators {#layouts}

### Pie Chart with d3.pie()

```svelte
<script>
  import * as d3 from 'd3';

  let { data, width = 400, height = 400 } = $props();

  let radius = $derived(Math.min(width, height) / 2);

  let colorScale = $derived(
    d3.scaleOrdinal(d3.schemeCategory10)
      .domain(data.map(d => d.category))
  );

  let pieData = $derived.by(() => {
    const pie = d3.pie()
      .value(d => d.value)
      .sort(null);  // Don't sort

    return pie(data);
  });

  let arcGenerator = $derived(
    d3.arc()
      .innerRadius(0)  // 0 for pie, > 0 for donut
      .outerRadius(radius - 10)
  );
</script>

<svg {width} {height}>
  <g transform="translate({width/2}, {height/2})">
    {#each pieData as slice}
      {@const path = arcGenerator(slice)}
      {@const color = colorScale(slice.data.category)}

      <path
        d={path}
        fill={color}
        stroke="white"
        stroke-width={2}
      />

      <text
        transform={`translate(${arcGenerator.centroid(slice)})`}
        text-anchor="middle"
        fill="white"
        font-size="14"
      >
        {slice.data.category}
      </text>
    {/each}
  </g>
</svg>
```

### Stack Layout

```javascript
import * as d3 from 'd3';

let stackedData = $derived.by(() => {
  const stack = d3.stack()
    .keys(['series1', 'series2', 'series3'])
    .order(d3.stackOrderNone)
    .offset(d3.stackOffsetNone);

  return stack(data);
});

// Render stacked bars
{#each stackedData as series, i}
  {#each series as d, j}
    <rect
      x={xScale(j)}
      y={yScale(d[1])}
      width={xScale.bandwidth()}
      height={yScale(d[0]) - yScale(d[1])}
      fill={colorScale(series.key)}
    />
  {/each}
{/each}
```

---

## Data Manipulation {#data-manipulation}

### Common D3 Array Methods

```javascript
import * as d3 from 'd3';

// Extent (min, max)
const [min, max] = d3.extent(data, d => d.value);

// Max/Min
const maxValue = d3.max(data, d => d.value);
const minValue = d3.min(data, d => d.value);

// Sum
const total = d3.sum(data, d => d.value);

// Mean
const average = d3.mean(data, d => d.value);

// Median
const median = d3.median(data, d => d.value);

// Quantile
const q75 = d3.quantile(data, 0.75, d => d.value);

// Grouping
const grouped = d3.group(data, d => d.category);
// Returns Map: { 'A' => [...], 'B' => [...] }

// Rollup
const sumByCategory = d3.rollup(
  data,
  v => d3.sum(v, d => d.value),  // Aggregator
  d => d.category                 // Key
);

// Index
const indexed = d3.index(data, d => d.id);
// Returns Map: { 'id1' => {...}, 'id2' => {...} }

// Bin (histogram)
const histogram = d3.bin()
  .domain([0, 100])
  .thresholds(10);

const bins = histogram(data.map(d => d.value));
```

### Using D3 Data Methods

```javascript
let { data } = $props();

// Aggregate statistics
let stats = $derived.by(() => {
  return {
    count: data.length,
    sum: d3.sum(data, d => d.value),
    mean: d3.mean(data, d => d.value),
    median: d3.median(data, d => d.value),
    extent: d3.extent(data, d => d.value)
  };
});

// Group by category
let grouped = $derived.by(() => {
  const groups = d3.group(data, d => d.category);
  return Array.from(groups, ([key, values]) => ({
    category: key,
    count: values.length,
    total: d3.sum(values, d => d.value)
  }));
});

// Create histogram
let histogram = $derived.by(() => {
  const bins = d3.bin()
    .domain(d3.extent(data, d => d.value))
    .thresholds(20);

  return bins(data.map(d => d.value));
});
```

---

## Transitions and Animations {#transitions}

### CSS Transitions (Recommended)

```svelte
<style>
  circle {
    transition:
      cx 500ms cubic-bezier(0.76, 0, 0.24, 1),
      cy 500ms cubic-bezier(0.76, 0, 0.24, 1),
      r 300ms ease,
      fill 300ms ease;
  }

  :global(.network-viz line) {
    transition: opacity 200ms ease;
  }
</style>

<svg>
  {#each nodes as node}
    <circle
      cx={xScale(node.x)}
      cy={yScale(node.y)}
      r={radiusScale(node.size)}
      fill={colorScale(node.category)}
    />
  {/each}
</svg>
```

### Svelte Transitions

```svelte
<script>
  import { fade, fly, scale } from 'svelte/transition';
</script>

<!-- Fade in new elements -->
{#each data as d (d.id)}
  <circle
    in:fade={{ duration: 300 }}
    out:fade={{ duration: 200 }}
    cx={xScale(d.x)}
    cy={yScale(d.y)}
    r={5}
  />
{/each}

<!-- Fly in from left -->
<g in:fly={{ x: -100, duration: 500 }}>
  <!-- content -->
</g>
```

### Manual Animation with $effect

```javascript
let animationProgress = $state(0);
let isAnimating = $state(false);

// Animate on state change
$effect(() => {
  if (!isAnimating) return;

  const startTime = performance.now();
  const duration = 1000;

  function animate(currentTime) {
    const elapsed = currentTime - startTime;
    animationProgress = Math.min(elapsed / duration, 1);

    if (animationProgress < 1) {
      requestAnimationFrame(animate);
    } else {
      isAnimating = false;
    }
  }

  requestAnimationFrame(animate);
});

// Interpolate positions
let interpolatedData = $derived.by(() => {
  return data.map((d, i) => ({
    ...d,
    x: startPositions[i].x + (endPositions[i].x - startPositions[i].x) * animationProgress,
    y: startPositions[i].y + (endPositions[i].y - startPositions[i].y) * animationProgress
  }));
});
```

---

## Axes and Legends {#axes-legends}

### Custom Axis Component

```svelte
<!-- Axis.svelte -->
<script>
  let { scale, orientation = 'bottom', tickCount = 5 } = $props();

  let ticks = $derived(scale.ticks(tickCount));
  let tickFormat = $derived(scale.tickFormat());
</script>

{#if orientation === 'bottom'}
  <g class="axis axis-x">
    {#each ticks as tick}
      <g transform="translate({scale(tick)}, 0)">
        <line y2={6} stroke="currentColor" />
        <text y={9} dy="0.71em" text-anchor="middle">
          {tickFormat(tick)}
        </text>
      </g>
    {/each}
  </g>
{:else if orientation === 'left'}
  <g class="axis axis-y">
    {#each ticks as tick}
      <g transform="translate(0, {scale(tick)})">
        <line x2={-6} stroke="currentColor" />
        <text x={-9} dy="0.32em" text-anchor="end">
          {tickFormat(tick)}
        </text>
      </g>
    {/each}
  </g>
{/if}
```

### Simple Legend

```svelte
<script>
  let { colorScale, width } = $props();

  let categories = $derived(colorScale.domain());
</script>

<div class="legend" style="width: {width}px;">
  {#each categories as category}
    <div class="legend-item">
      <div
        class="legend-swatch"
        style="background-color: {colorScale(category)};"
      ></div>
      <span>{category}</span>
    </div>
  {/each}
</div>

<style>
  .legend {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .legend-swatch {
    width: 20px;
    height: 20px;
    border-radius: 3px;
  }
</style>
```

---

## Performance Optimization {#performance}

### 1. Limit Rendered Elements

```javascript
// Limit to visible data points
let visibleData = $derived.by(() => {
  if (data.length < 1000) return data;

  // Only render points in viewport
  return data.filter(d =>
    xScale(d.x) >= 0 && xScale(d.x) <= width &&
    yScale(d.y) >= 0 && yScale(d.y) <= height
  );
});
```

### 2. Use Canvas for Large Datasets

```svelte
<script>
  let canvasRef;
  let ctx;

  $effect(() => {
    if (!canvasRef) return;

    ctx = canvasRef.getContext('2d');

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw points
    data.forEach(d => {
      ctx.beginPath();
      ctx.arc(xScale(d.x), yScale(d.y), 3, 0, 2 * Math.PI);
      ctx.fillStyle = colorScale(d.category);
      ctx.fill();
    });
  });
</script>

<canvas
  bind:this={canvasRef}
  {width}
  {height}
/>
```

### 3. Memoize Expensive Computations

```javascript
// Cache scale computations
let scaleCache = $state(new Map());

function getCachedScale(key, factory) {
  if (!scaleCache.has(key)) {
    scaleCache.set(key, factory());
  }
  return scaleCache.get(key);
}
```

### 4. Debounce Updates

```javascript
let rawData = $state([]);
let debouncedData = $state([]);

$effect(() => {
  const timeout = setTimeout(() => {
    debouncedData = rawData;
  }, 100);

  return () => clearTimeout(timeout);
});

// Use debouncedData for rendering
```

---

## Summary

**Key Principles:**
1. D3 for data, Svelte for DOM
2. Create scales as $derived values
3. Render SVG with Svelte's {#each}
4. Use CSS transitions for smooth animations
5. Limit rendered elements for performance
6. Prefer Canvas for >5000 points

**When to Use What:**
- **Scales/Colors**: Always use D3
- **Layouts**: Use D3 generators, render with Svelte
- **Animations**: CSS transitions > Svelte transitions > D3 transitions
- **Large Datasets**: Canvas + D3 data manipulation
- **Interactive**: Svelte event handlers + D3 scales

For more D3 features, see: https://d3js.org/
