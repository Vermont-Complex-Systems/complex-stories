<script>
  import * as d3 from 'd3';
  import DodgeChart from '$lib/components/helpers/DodgeChart.svelte';
  
  let {
    displayData = [],
    width, height, timeScale,
    onBrushSelection = () => {} // Callback for brush selection
  } = $props();

  let hasData = $derived(displayData && displayData.length > 0);

  // Brush state
  let brushSelection = $state(null);
  let svgElement = $state(null);
  let brush = null;

  $effect(() => {
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
    brushSelection = event.selection;

    if (event.selection) {
      const [y0, y1] = event.selection;
      const brushedPoints = displayData.filter(point => point.y >= y0 && point.y <= y1);
      onBrushSelection(brushedPoints);
    } else {
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
    const institutionName = point.shared_institutions || 'Unknown';
    return `Coauthor: ${point.coauthor_display_name}\nYear: ${point.publication_year}\nAge difference: ${point.age_diff} years\nTotal collaborations: ${point.all_times_collabo}\nShared Institution: ${institutionName}`;
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
      />
    </div>
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
    transform: rotate(270deg) translate(-45%, -56.4%);
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
</style>