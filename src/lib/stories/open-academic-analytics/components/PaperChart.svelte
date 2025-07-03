<script>
  import * as d3 from 'd3';
  import { processPaperData, getCombinedDateRange } from '../utils/combinedChartUtils.js';
  import Tooltip from './Tooltip.svelte';

  let { paperData, coauthorData, width, height, highlightedAuthor = null } = $props();

  // Constants - Add horizontal margins
  const MARGIN_TOP = 50;
  const MARGIN_BOTTOM = 50;
  const MARGIN_LEFT = 40;
  const MARGIN_RIGHT = 40;
  const MAX_CIRCLE_RADIUS = 15;

  // Check if we have data
  let hasData = $derived(paperData && paperData.length > 0);

  // Time scale using COMBINED date range from both datasets
  let timeScale = $derived.by(() => {
    if (!hasData) return d3.scaleTime();
    const dateRange = getCombinedDateRange(paperData, coauthorData);
    return d3.scaleTime()
      .domain(dateRange)
      .range([MARGIN_TOP, height - MARGIN_BOTTOM]); // Remove MAX_CIRCLE_RADIUS subtraction
  });

  // Year ticks for the timeline
  let yearTicks = $derived.by(() => {
    if (!hasData) return [];
    const dateRange = getCombinedDateRange(paperData, coauthorData);
    const [startYear, endYear] = d3.extent(dateRange, d => d.getFullYear());
    const yearSpacing = Math.max(1, Math.floor((endYear - startYear) / 15));
    return d3.range(startYear, endYear + 1, yearSpacing);
  });

  // Process paper data into plot points
  let plotData = $derived.by(() => {
    if (!hasData) return [];
    return processPaperData(paperData, width, height, timeScale);
  });

  // Filter and style data for display
  let displayData = $derived.by(() => {
    if (!plotData.length) return [];
    
    return plotData.map(point => {
      let opacity = 1;
      
      // Apply author highlight filter if provided
      if (highlightedAuthor) {
        const isHighlightedAuthor = point.ego_aid === highlightedAuthor;
        opacity *= isHighlightedAuthor ? 1 : 0.2;
      }
      
      return {
        ...point,
        opacity,
        displayColor: point.color
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
    
    tooltipContent = `Title: ${point.title}\nYear: ${point.year}\nCitations: ${point.cited_by_count}\nCoauthors: ${point.nb_coauthors}\nType: ${point.work_type}`;
    
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
            <!-- Update grid lines to respect margins -->
            <line x1={MARGIN_LEFT} x2={width - MARGIN_RIGHT} y1={y} y2={y} class="grid-line"/>
            <text x={MARGIN_LEFT - 5} y={y - 5} text-anchor="end" class="year-label">{year}</text>
          {/each}
        </g>
        
        <!-- Points group with proper margins -->
        <g transform="translate({MARGIN_LEFT}, 0)">
          {#each displayData as point}
            <circle
              cx={point.x}
              cy={point.y}
              r={point.r}
              fill={point.displayColor}
              stroke="black"
              stroke-width="0.8"
              fill-opacity={point.opacity}
              class="data-point"
              onmouseenter={(e) => showPointTooltip(e, point)}
              onmouseleave={hideTooltip}
            />
          {/each}
        </g>
      </svg>
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