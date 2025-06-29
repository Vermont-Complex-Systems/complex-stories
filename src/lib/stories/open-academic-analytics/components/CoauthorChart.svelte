<script>
  import * as d3 from 'd3';
  import { processCoauthorData, getCombinedDateRange, getCoauthorColor, ageColorScale, acquaintanceColorScale } from '../utils/combinedChartUtils.js';
  import Tooltip from './Tooltip.svelte';

  let { 
    coauthorData, 
    paperData,
    width, 
    height, 
    colorMode = 'age_diff',
    highlightedCoauthor = null
  } = $props();
  
  // Constants
  const MARGIN_TOP = 50;
  const MARGIN_BOTTOM = 50;
  const MAX_CIRCLE_RADIUS = 12;

  // Check if we have data
  let hasData = $derived(coauthorData && coauthorData.length > 0);

  // Time scale using COMBINED date range from both datasets
  let timeScale = $derived.by(() => {
    if (!hasData) return d3.scaleTime();
    const dateRange = getCombinedDateRange(paperData, coauthorData);
    return d3.scaleTime()
      .domain(dateRange)
      .range([MARGIN_TOP, height - MARGIN_BOTTOM - MAX_CIRCLE_RADIUS]);
  });

  // Year ticks for the timeline
  let yearTicks = $derived.by(() => {
    if (!hasData) return [];
    const dateRange = getCombinedDateRange(paperData, coauthorData);
    const [startYear, endYear] = d3.extent(dateRange, d => d.getFullYear());
    const yearSpacing = Math.max(1, Math.floor((endYear - startYear) / 15));
    return d3.range(startYear, endYear + 1, yearSpacing);
  });

  // Process coauthor data into plot points
  let plotData = $derived.by(() => {
    if (!hasData) return [];
    return processCoauthorData(coauthorData, width, height, timeScale);
  });

  // Filter and style data for display
  let displayData = $derived.by(() => {
    if (!plotData.length) return [];
    
    return plotData.map(point => {
      let opacity = 1;
      
      // Apply coauthor highlight filter if provided
      if (highlightedCoauthor) {
        const isHighlightedCoauthor = point.coauth_aid === highlightedCoauthor;
        opacity *= isHighlightedCoauthor ? 1 : 0.2;
      }
      
      return {
        ...point,
        opacity,
        displayColor: getCoauthorColor(point, colorMode)
      };
    });
  });

  // Legend data
  let legendData = $derived.by(() => {
    if (colorMode === 'age_diff') {
      return [
        { label: 'Older (>7 years)', color: ageColorScale('older') },
        { label: 'Same age (±7 years)', color: ageColorScale('same') },
        { label: 'Younger (<-7 years)', color: ageColorScale('younger') }
      ];
    } else if (colorMode === 'acquaintance') {
      return [
        { label: 'New collaboration', color: acquaintanceColorScale('new_collab') },
        { label: 'Repeat collaboration', color: acquaintanceColorScale('repeat_collab') },
        { label: 'Long-term collaboration', color: acquaintanceColorScale('long_term_collab') }
      ];
    }
    return [];
  });

  // Tooltip state
  let showTooltip = $state(false);
  let tooltipContent = $state('');
  let mouseX = $state(0);
  let mouseY = $state(0);

  function showPointTooltip(event, point) {
    mouseX = event.clientX;
    mouseY = event.clientY;
    
    tooltipContent = `Coauthor: ${point.name}\nYear: ${point.year}\nAge difference: ${point.age_diff} years\nTotal collaborations: ${point.all_times_collabo}\nYearly collaborations: ${point.yearly_collabo}\nAcquaintance: ${point.acquaintance}`;
    
    showTooltip = true;
  }

  function hideTooltip() {
    showTooltip = false;
  }

  // Add this temporarily to debug
  $inspect(displayData)
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
        
        <!-- Coauthor points -->
        {#each displayData as point}
          <circle
            cx={point.x}
            cy={point.y}
            r={point.r}
            fill={point.displayColor}
            stroke="black"
            stroke-width="0.3"
            fill-opacity={point.opacity}
            class="data-point"
            on:mouseenter={(e) => showPointTooltip(e, point)}
            on:mouseleave={hideTooltip}
          />
        {/each}
      </svg>

      <!-- Legend -->
      {#if legendData.length > 0}
        <div class="legend">
          <h4>Legend</h4>
          {#each legendData as item}
            <div class="legend-item">
              <div class="legend-color" style="background-color: {item.color}"></div>
              <span class="legend-label">{item.label}</span>
            </div>
          {/each}
        </div>
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
    overflow: hidden; /* Add this */
  }

  .plot-container {
    display: flex;
    justify-content: center;
    position: relative;
    width: 100%;
    overflow: hidden; /* Add this */
  }

  .chart-svg {
    display: block;
    overflow: visible; /* Keep SVG overflow visible for tooltips */
    max-width: 100%; /* But constrain to container */
  }

  .legend {
    position: absolute;
    top: 10px;
    right: 20px;
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    padding: 12px;
    font-size: var(--font-size-xsmall);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .legend h4 {
    margin: 0 0 8px 0;
    font-size: var(--font-size-small);
    font-weight: var(--font-weight-bold);
  }

  .legend-item {
    display: flex;
    align-items: center;
    margin: 4px 0;
  }

  .legend-color {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
    border: 1px solid black;
  }

  .legend-label {
    color: var(--chart-text-color);
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
    stroke-width: 1;
  }

  /* Dark mode support */
  :global(.dark) .legend {
    background: var(--color-bg);
    border-color: var(--color-border);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }
</style>