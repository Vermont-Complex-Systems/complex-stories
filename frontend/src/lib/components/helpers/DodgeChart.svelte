<script>
  import * as d3 from 'd3';
  import Tooltip from './Tooltip.svelte';

  let { 
    displayData = [],
    width, 
    height,
    timeScale,
    gridStyle = 'full', // 'full' (0 to width) or 'margins' (respecting left/right margins)
    onPointClick = null,
    onChartClick = null,
    formatTooltip = null
  } = $props();
  
  // Constants
  const MARGIN_TOP = 50;
  const MARGIN_BOTTOM = 50;
  const MARGIN_LEFT = 40;
  const MARGIN_RIGHT = 40;

  // Check if we have data
  let hasData = $derived(displayData && displayData.length > 0);

  // Year ticks
  let yearTicks = $derived.by(() => {
    if (!timeScale) return [];
    const [startDate, endDate] = timeScale.domain();
    if (!startDate || !endDate) return [];
    const [startYear, endYear] = [startDate.getFullYear(), endDate.getFullYear()];
    const yearSpacing = Math.max(1, Math.floor((endYear - startYear) / 15));
    return d3.range(startYear, endYear + 1, yearSpacing);
  });

  // Grid line properties based on style
  let gridProps = $derived(() => {
    if (gridStyle === 'full') {
      return {
        x1: 0,
        x2: width,
        textX: 10,
        textAnchor: "start"
      };
    } else { // 'margins'
      return {
        x1: MARGIN_LEFT,
        x2: width - MARGIN_RIGHT,
        textX: MARGIN_LEFT - 5,
        textAnchor: "end"
      };
    }
  });

  // Tooltip state
  let showTooltip = $state(false);
  let tooltipContent = $state('');
  let mouseX = $state(0);
  let mouseY = $state(0);

  function showPointTooltip(event, point) {
    mouseX = event.clientX;
    mouseY = event.clientY;
    
    if (formatTooltip) {
      tooltipContent = formatTooltip(point);
    } else {
      // Default tooltip
      tooltipContent = `Data point\nX: ${point.x}\nY: ${point.y}`;
    }
    
    showTooltip = true;
  }

  function hideTooltip() {
    showTooltip = false;
  }

  function handleChartClick(event) {
    if (onChartClick) {
      onChartClick(event);
    }
  }

  function handlePointClick(event, point) {
    if (onPointClick) {
      event.stopPropagation();
      onPointClick(event, point);
    }
  }
</script>

<div class="chart-wrapper">
  <div class="viz-content">
    <div class="plot-container">
      <div class="chart-area">
        <!-- Main dodge chart visualization -->
        <svg 
          {width} 
          {height} 
          class="chart-svg" 
          onclick={handleChartClick} 
          role="button" 
          tabindex="0" 
          onkeydown={(e) => e.key === 'Enter' && handleChartClick(e)}
        >
          
          <!-- Grid lines and year labels -->
          <g class="grid-container">
            {#each yearTicks as year}
              {@const yearDate = new Date(year, 0, 1)}
              {@const y = timeScale(yearDate)}
              {@const isFullGrid = gridStyle === 'full'}
              {@const lineX1 = isFullGrid ? 0 : MARGIN_LEFT}
              {@const lineX2 = isFullGrid ? width : width - MARGIN_RIGHT}
              {@const labelX = isFullGrid ? 10 : MARGIN_LEFT - 5}
              {@const labelAnchor = isFullGrid ? "start" : "end"}
              <line 
                x1={lineX1} 
                x2={lineX2} 
                y1={y} 
                y2={y} 
                class="grid-line"
              />
              <text 
                x={labelX} 
                y={y - 5} 
                text-anchor={labelAnchor} 
                class="year-label"
              >
                {year}
              </text>
            {/each}
          </g>
          
          <!-- Data points -->
          <g>
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
                onclick={(e) => handlePointClick(e, point)}
                onkeydown={(e) => (e.key === 'Enter' || e.key === ' ') && handlePointClick(e, point)}
                onmouseenter={(e) => showPointTooltip(e, point)}
                onmouseleave={hideTooltip}
              />
            {/each}
          </g>
        </svg>
      </div>
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
    overflow: hidden;
  }

  .viz-content {
    width: 100%;
  }

  .plot-container {
    display: flex;
    justify-content: center;
    position: relative;
    width: 100%;
    overflow: hidden;
  }

  .chart-area {
    position: relative;
    width: 100%;
    max-width: 100%;
  }

  .chart-svg {
    display: block;
    overflow: visible;
    max-width: 100%;
    margin: 0 auto;
  }

  /* Chart styling */
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