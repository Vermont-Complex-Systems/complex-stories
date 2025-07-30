<script>
  import * as d3 from 'd3';
  import Tooltip from './Tooltip.svelte';
  import { dodgeX } from '$lib/utils/dodgeX.js'
  
  let { 
    data = [],
    yField,
    colorFunction = null,
    highlightedItem = null,
    highlightField = null, 
    width, 
    height,
    timeScale,
    radiusScale,
    onPointClick = null,
    onChartClick = null,
    formatTooltip = null
  } = $props();

  // Process data into positioned points with highlighting
  let dodgedData = $derived.by(() => {
    if (!data?.length || !timeScale || !width || !height) return [];
    
    const points = dodgeX(data, yField, colorFunction, radiusScale, timeScale, width, height);
    
    return points.map(point => {
      const isHighlighted = highlightedItem && highlightField ? 
        point.data[highlightField] === highlightedItem : true;
      
      return {
        ...point,
        opacity: highlightedItem ? (isHighlighted ? 1.0 : 0.2) : 1.0,
        strokeWidth: isHighlighted ? 1.2 : 0.8
      };
    });
  });

  // Year ticks for grid
  let yearTicks = $derived.by(() => {
    if (!timeScale) return [];
    const [startDate, endDate] = timeScale.domain();
    if (!startDate || !endDate) return [];
    
    const [startYear, endYear] = [startDate.getFullYear(), endDate.getFullYear()];
    const yearSpacing = Math.max(1, Math.floor((endYear - startYear) / 15));
    return d3.range(startYear, endYear + 1, yearSpacing);
  });

  // Tooltip state
  let showTooltip = $state(false);
  let tooltipContent = $state('');
  let mouseX = $state(0);
  let mouseY = $state(0);

  function showPointTooltip(event, point) {
    mouseX = event.clientX;
    mouseY = event.clientY;
    tooltipContent = formatTooltip ? formatTooltip(point) : null;
    showTooltip = true;
  }

  function hideTooltip() {
    showTooltip = false;
  }

  function handleChartClick(event) {
    onChartClick?.(event);
  }

  function handlePointClick(event, point) {
    if (onPointClick) {
      event.stopPropagation();
      onPointClick(event, point);
    }
  }
  

</script>

<div class="chart-wrapper">
  <svg 
    {width} 
    {height} 
    class="chart-svg" 
    onclick={handleChartClick}
  >
    <!-- Grid lines and year labels -->
    <g class="grid-container">
      {#each yearTicks as year}
        {@const yearDate = new Date(year, 0, 1)}
        {@const y = timeScale(yearDate)}
        <line x1={0} x2={width} y1={y} y2={y} class="grid-line" />
        <text x={10} y={y - 5} text-anchor="start" class="year-label">{year}</text>
      {/each}
    </g>
    
    <!-- Data points -->
    <g>
      {#each dodgedData as point}
        <circle
          cx={point.x}
          cy={point.y}
          r={point.r}
          fill={point.color}
          stroke="black"
          stroke-width={0.8}
          fill-opacity={point.opacity}
          class="data-point"
          onclick={(e) => handlePointClick(e, point)}
          onmouseenter={(e) => showPointTooltip(e, point)}
          onmouseleave={hideTooltip}
        />
      {/each}
    </g>
  </svg>
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
    overflow: hidden;
  }

  .chart-svg {
    display: block;
    overflow: visible;
    max-width: 100%;
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