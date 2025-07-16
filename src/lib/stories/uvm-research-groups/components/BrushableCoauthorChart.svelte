<script>
  import * as d3 from 'd3';
  import DodgeChart from '$lib/components/helpers/DodgeChart.svelte';
  
  let { 
    displayData = [], 
    rawData = [],
    width, height, timeScale, 
    colorMode = 'age_diff', 
    colorScale = null, 
    trainingData = null,
    onBrushSelection = () => {} // Callback for brush selection
  } = $props();

  // Check if we have training data
  let hasTrainingData = $derived(trainingData && trainingData.length > 0);
  let hasData = $derived(displayData && displayData.length > 0);

  // Brush state
  let brushSelection = $state(null);
  let svgElement = $state(null);
  let brush = null;

  // Use onMount instead of $effect to avoid infinite loops
  import { onMount } from 'svelte';
  
  onMount(() => {
    if (!svgElement) return;

    // Create vertical brush (brushY) instead of full brush
    brush = d3.brushY()
      .extent([[0, 0], [width, height]])
      .on('brush end', handleBrush);

    // Add brush to SVG
    d3.select(svgElement)
      .select('.brush-layer')
      .call(brush);

    return () => {
      if (svgElement) {
        d3.select(svgElement).select('.brush-layer').selectAll('*').remove();
      }
    };
  });

  function handleBrush(event) {
    const selection = event.selection;
    brushSelection = selection;

    if (selection) {
      // For vertical brush, selection is [y0, y1]
      const [y0, y1] = selection;
      
      const brushedPoints = displayData.filter(point => {
        return point.y >= y0 && point.y <= y1;
      });

      // Call callback with selected points
      onBrushSelection(brushedPoints);
    } else {
      // No selection - clear
      onBrushSelection([]);
    }
  }

  // Clear brush function (can be called from parent)
  export function clearBrush() {
    if (brush && svgElement) {
      d3.select(svgElement).select('.brush-layer').call(brush.clear);
      brushSelection = null;
      onBrushSelection([]);
    }
  }

  // Coauthor-specific tooltip formatter
  function formatCoauthorTooltip(point) {
    const institutionName = point.shared_institutions_normalized || point.shared_institutions || 'Unknown';
    return `Coauthor: ${point.name}\nYear: ${point.year}\nAge difference: ${point.age_diff} years\nTotal collaborations: ${point.all_times_collabo}\nShared Institution: ${institutionName}`;
  }

  // Coauthor-specific click handlers
  function handleCoauthorClick(event, point) {
    dashboardState.highlightedCoauthor = point.name;
  }

  function handleChartClick(event) {
    dashboardState.highlightedCoauthor = null;
  }

  // Enhanced display data with brush selection - using $derived.by to avoid side effects
  let enhancedDisplayData = $derived.by(() => {
    if (!brushSelection || !displayData.length) return displayData;

    const [y0, y1] = brushSelection; // Vertical brush gives [y0, y1]
    
    return displayData.map(point => ({
      ...point,
      isBrushed: point.y >= y0 && point.y <= y1,
      opacity: (point.y >= y0 && point.y <= y1) ? 1 : 0.3
    }));
  });
</script>

<div class="coauthor-chart" style="--chart-width: {width}px; --chart-height: {height}px;">
  <div class="rotation-wrapper">
    <div class="chart-container rotated">
      <!-- Overlay SVG for brush (positioned over the DodgeChart) -->
      <svg 
        bind:this={svgElement}
        {width} 
        {height}
        class="brush-overlay"
      >
        <g class="brush-layer"></g>
      </svg>
      
      <DodgeChart 
        displayData={enhancedDisplayData}
        {width}
        {height}
        {timeScale}
        gridStyle="full"
        formatTooltip={formatCoauthorTooltip}
        onPointClick={handleCoauthorClick}
        onChartClick={handleChartClick}
      />
    </div>
  </div>
  
  <!-- Brush controls -->
  <div class="brush-controls">
    <button onclick={clearBrush} class="clear-brush-btn">
      Clear Selection
    </button>
    {#if brushSelection}
      <span class="selection-info">
        {enhancedDisplayData.filter(d => d.isBrushed).length} points selected
      </span>
    {/if}
  </div>
</div>

<style>
  .coauthor-chart {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    height: var(--chart-width);
    gap: 1rem;
  }

  .rotation-wrapper {
    position: relative;
    overflow: visible;
    width: var(--chart-height);
    height: var(--chart-width);
  }

  .chart-container.rotated {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: rotate(270deg) translate(-40%, -50.7%);
    transform-origin: 0 0;
    border: 2px solid rgb(237, 237, 237);
    width: var(--chart-width);
    height: var(--chart-height);
  }

  .brush-overlay {
    position: absolute;
    top: 0;
    left: 0;
    pointer-events: all;
    z-index: 10;
  }

  /* D3 brush styling */
  .coauthor-chart :global(.brush .overlay) {
    fill: none;
    pointer-events: all;
  }

  .coauthor-chart :global(.brush .selection) {
    fill: rgba(70, 130, 180, 0.2);
    stroke: #4682b4;
    stroke-width: 2;
    stroke-dasharray: 5,5;
  }

  .coauthor-chart :global(.brush .handle) {
    fill: #4682b4;
    stroke: #fff;
    stroke-width: 1;
  }

  .brush-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-top: 1rem;
  }

  .clear-brush-btn {
    padding: 0.5rem 1rem;
    background: #4682b4;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.2s ease;
  }

  .clear-brush-btn:hover {
    background: #5a9bd3;
  }

  .selection-info {
    font-size: 14px;
    color: var(--color-fg);
    font-weight: 500;
  }
</style>