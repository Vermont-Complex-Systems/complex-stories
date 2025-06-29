<script>
  import * as d3 from 'd3';
  import { getCombinedDateRange } from '../utils/combinedChartUtils.js';
  import Tooltip from './Tooltip.svelte';

  let { 
    paperData,
    coauthorData,
    width, 
    height,
    processDataFn, // Function to process the data for positioning
    dataToDisplay, // The actual data to display (with colors, opacity, etc.)
    pointComponent, // Snippet for rendering individual points
    legendComponent = null, // Optional legend snippet
    tooltipFormatter // Function to format tooltip content
  } = $props();

  // Constants
  const MARGIN_TOP = 50;
  const MARGIN_BOTTOM = 50;
  const MARGIN_LEFT = 40;
  const MARGIN_RIGHT = 40;

  // Check if we have data
  let hasData = $derived(dataToDisplay && dataToDisplay.length > 0);

  // Time scale using COMBINED date range from both datasets
  let timeScale = $derived.by(() => {
    if (!hasData) return d3.scaleTime();
    const dateRange = getCombinedDateRange(paperData, coauthorData);
    return d3.scaleTime()
      .domain(dateRange)
      .range([MARGIN_TOP, height - MARGIN_BOTTOM]);
  });

  // Year ticks for the timeline
  let yearTicks = $derived.by(() => {
    if (!hasData) return [];
    const dateRange = getCombinedDateRange(paperData, coauthorData);
    const [startYear, endYear] = d3.extent(dateRange, d => d.getFullYear());
    const yearSpacing = Math.max(1, Math.floor((endYear - startYear) / 15));
    return d3.range(startYear, endYear + 1, yearSpacing);
  });

  // Process data into plot points with positioning
  let plotData = $derived.by(() => {
    if (!hasData) return [];
    const positionedData = processDataFn(dataToDisplay, width, height, timeScale);
    
    // Merge positioning info with display data
    return dataToDisplay.map((displayPoint, i) => ({
      ...displayPoint,
      ...positionedData[i], // This adds x, y, r from positioning
    }));
  });

  // Tooltip state
  let showTooltip = $state(false);
  let tooltipContent = $state('');
  let mouseX = $state(0);
  let mouseY = $state(0);

  function showPointTooltip(event, point) {
    mouseX = event.clientX;
    mouseY = event.clientY;
    tooltipContent = tooltipFormatter(point);
    showTooltip = true;
  }

  function hideTooltip() {
    showTooltip = false;
  }
</script>

<div class="chart-wrapper">
  <div class="viz-content">
    <div class="plot-container">
      <svg {width} {height} class="chart-svg">
        
        <!-- Grid lines and year labels -->
        <g>
          {#each yearTicks as year}
            {@const yearDate = new Date(year, 0, 1)}
            {@const y = timeScale(yearDate)}
            <line x1="0" x2={width} y1={y} y2={y} class="grid-line"/>
            <text x="10" y={y - 5} text-anchor="start" class="year-label">{year}</text>
          {/each}
        </g>
        
        <!-- Data points group with proper margins -->
        <g transform="translate({MARGIN_LEFT}, 0)">
          {#each plotData as point}
            {@render pointComponent(point, showPointTooltip, hideTooltip)}
          {/each}
        </g>
      </svg>

      <!-- Optional legend -->
      {#if legendComponent}
        {@render legendComponent()}
      {/if}
    </div>
  </div>
</div>

<Tooltip 
  visible={showTooltip}
  x={mouseX}
  y={mouseY}
  content={tooltipContent}
/>

<style>
  .chart-wrapper {
    --chart-grid-color: var(--color-border);
    --chart-text-color: var(--color-secondary-gray);
    width: 100%;
  }

  .plot-container {
    display: flex;
    justify-content: center;
    position: relative;
    width: 100%;
  }

  .chart-svg {
    display: block;
  }

  /* SVG element styling using design tokens */
  .chart-wrapper :global(.chart-label) {
    font-size: var(--font-size-xsmall);
    font-weight: var(--font-weight-bold);
    font-family: var(--sans);
    fill: var(--chart-text-color);
  }

  .chart-wrapper :global(.year-label) {
    font-size: var(--font-size-xsmall);
    font-family: var(--mono);
    fill: var(--chart-text-color);
  }

  .chart-wrapper :global(.grid-line) {
    stroke: var(--chart-grid-color);
    stroke-width: 1;
  }

  .chart-wrapper :global(.data-point) {
    cursor: pointer;
    transition: fill-opacity 0.3s ease;
  }

  .chart-wrapper :global(.data-point:hover) {
    stroke-width: 2;
  }
</style>