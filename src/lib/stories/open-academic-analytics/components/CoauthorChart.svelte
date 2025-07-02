<script>
  import * as d3 from 'd3';
  import { processCoauthorData, getCombinedDateRange, ageColorScale, acquaintanceColorScale, collaborationColorScale } from '../utils/combinedChartUtils.js';
  import Tooltip from './Tooltip.svelte';
  import Legend from './Legend.svelte';
  import { dashboardState } from '../state.svelte.ts';

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
  const MARGIN_LEFT = 40;
  const MARGIN_RIGHT = 40;
  const MAX_CIRCLE_RADIUS = 12;

  // Check if we have data
  let hasData = $derived(coauthorData && coauthorData.length > 0);

  // Simple institution color scale - Observable Plot style
  let institutionColorScale = $derived.by(() => {
    if (!hasData) return null;
    const uniqueInstitutions = [...new Set(coauthorData.map(d => d.shared_institutions))]
      .filter(inst => inst != null);
    return d3.scaleOrdinal(d3.schemeCategory10).domain(uniqueInstitutions);
  });

  // Time scale
  let timeScale = $derived.by(() => {
    if (!hasData) return d3.scaleTime();
    const dateRange = getCombinedDateRange(paperData, coauthorData);
    return d3.scaleTime()
      .domain(dateRange)
      .range([MARGIN_TOP, height - MARGIN_BOTTOM - MAX_CIRCLE_RADIUS]);
  });

  // Year ticks
  let yearTicks = $derived.by(() => {
    if (!hasData) return [];
    const dateRange = getCombinedDateRange(paperData, coauthorData);
    const [startYear, endYear] = d3.extent(dateRange, d => d.getFullYear());
    const yearSpacing = Math.max(1, Math.floor((endYear - startYear) / 15));
    return d3.range(startYear, endYear + 1, yearSpacing);
  });

  // Process coauthor data
  let plotData = $derived.by(() => {
    if (!hasData) return [];
    return processCoauthorData(coauthorData, width, height, timeScale);
  });

  // Simple Observable Plot-style display data
  let displayData = $derived.by(() => {
    if (!plotData.length) return [];
    
    return plotData.map(point => {
      // Get the value for coloring (like Observable Plot)
      let colorValue;
      if (colorMode === 'age_diff') {
        colorValue = point.age_category;
      } else if (colorMode === 'acquaintance') {
        colorValue = point.acquaintance;
      } else if (colorMode === 'institutions') {
        // Use the institution column specifically
        colorValue = point.institution;
      } else if (colorMode === 'shared_institutions') {
        // Use the shared_institutions column specifically  
        colorValue = point.shared_institutions;
      }

      // Simple Observable Plot-style logic
      const isNull = colorValue == null;
      let displayColor, opacity, strokeWidth;

      if (isNull) {
        displayColor = "#888888";
        opacity = 0.3;
        strokeWidth = 0.1;
      } else {
        // Get color based on mode
        if (colorMode === 'age_diff') {
          displayColor = ageColorScale(colorValue);
        } else if (colorMode === 'acquaintance') {
          displayColor = acquaintanceColorScale(colorValue);
        } else if (colorMode === 'institutions') {
          displayColor = institutionColorScale(colorValue);
        } else if (colorMode === 'shared_institutions') {
          displayColor = institutionColorScale(colorValue);
        }
        opacity = 0.9;
        strokeWidth = 0.3;
      }
      
      // Apply highlight filter
      if (highlightedCoauthor) {
        const isHighlightedCoauthor = point.name === highlightedCoauthor;
        opacity *= isHighlightedCoauthor ? 1 : 0.2;
      }
      
      return {
        ...point,
        displayColor,
        opacity,
        strokeWidth
      };
    });
  });

  // Tooltip state
  let showTooltip = $state(false);
  let tooltipContent = $state('');
  let mouseX = $state(0);
  let mouseY = $state(0);

  function showPointTooltip(event, point) {
    mouseX = event.clientX;
    mouseY = event.clientY;
    
    tooltipContent = `Coauthor: ${point.name}\nYear: ${point.year}\nAge difference: ${point.age_diff} years\nTotal collaborations: ${point.all_times_collabo}\nShared Institution: ${point.shared_institutions || 'Unknown'}\n(click to see collaborations over time)`;
    
    showTooltip = true;
  }

  function hideTooltip() {
    showTooltip = false;
  }

  function handleChartClick(event) {
    // Reset highlighted coauthor when clicking on chart background
    dashboardState.highlightedCoauthor = null;
  }

  function handleCoauthorClick(event, point) {
    // Stop event from bubbling to chart background
    event.stopPropagation();
    // Set highlighted coauthor
    dashboardState.highlightedCoauthor = point.name;
  }
</script>

<div class="chart-wrapper">
  <div class="viz-content">
    <div class="plot-container">
      <svg {width} {height} class="chart-svg" onclick={handleChartClick} role="button" tabindex="0" onkeydown={(e) => e.key === 'Enter' && handleChartClick(e)}>
        
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
        <g transform="translate({MARGIN_LEFT}, 0)">
          {#each displayData as point}
            <circle
              cx={point.x}
              cy={point.y}
              r={point.r}
              fill={point.displayColor}
              stroke="black"
              stroke-width={point.strokeWidth}
              fill-opacity={point.opacity}
              class="data-point"
              role="button"
              tabindex="0"
              onclick={(e) => handleCoauthorClick(e, point)}
              onkeydown={(e) => (e.key === 'Enter' || e.key === ' ') && handleCoauthorClick(e, point)}
              onmouseenter={(e) => showPointTooltip(e, point)}
              onmouseleave={hideTooltip}
            />
          {/each}
        </g>
      </svg>

      <!-- Legend -->
      <Legend 
        {colorMode}
        {coauthorData}
        visible={hasData}
      />
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