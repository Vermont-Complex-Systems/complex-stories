<script>
  import * as d3 from 'd3';
  
  let { 
    embeddingData = [], 
    width = 800, 
    height = 600,
    margin = { top: 20, right: 20, bottom: 20, left: 20 },
    highlightedIds = [] // Array of ego_aid values to highlight
  } = $props();

  // Calculate inner dimensions
  let innerWidth = $derived(width - margin.left - margin.right);
  let innerHeight = $derived(height - margin.top - margin.bottom);

  // Create scales
  let xScale = $derived.by(() => {
    if (!embeddingData.length) return d3.scaleLinear();
    
    const extent = d3.extent(embeddingData, d => +d.umap_1);
    return d3.scaleLinear()
      .domain(extent)
      .range([0, innerWidth])
      .nice();
  });

  let yScale = $derived.by(() => {
    if (!embeddingData.length) return d3.scaleLinear();
    
    const extent = d3.extent(embeddingData, d => +d.umap_2);
    return d3.scaleLinear()
      .domain(extent)
      .range([innerHeight, 0]) // Flip Y axis
      .nice();
  });

  // Generate axis ticks
  let xTicks = $derived(xScale.ticks(8));
  let yTicks = $derived(yScale.ticks(6));

  // Tooltip state
  let showTooltip = $state(false);
  let tooltipContent = $state('');
  let mouseX = $state(0);
  let mouseY = $state(0);

  function handleMouseEnter(event, point) {
    // Only show tooltip if point is highlighted (or if no selection is active)
    const isHighlighted = highlightedIds.includes(point.ego_aid);
    if (highlightedIds.length === 0 || isHighlighted) {
      mouseX = event.clientX;
      mouseY = event.clientY;
      tooltipContent = `title: ${point.title}\nauthors: ${point.authors}\ndoi: ${point.doi}\npub_year: ${point.pub_year}`;
      showTooltip = true;
    }
  }

  function handleMouseLeave() {
    showTooltip = false;
  }
</script>

<div class="plot-container">
  <svg {width} {height}>
    <!-- Background -->
    <rect width={width} height={height} fill="var(--color-bg)" />
    
    <!-- Main plot area -->
    <g transform="translate({margin.left},{margin.top})">
      
      <!-- Grid lines -->
      {#each xTicks as tick}
        <line 
          x1={xScale(tick)} 
          x2={xScale(tick)} 
          y1="0" 
          y2={innerHeight}
          stroke="var(--color-border)"
          stroke-width="1"
          opacity="0.3"
        />
      {/each}
      
      {#each yTicks as tick}
        <line 
          x1="0" 
          x2={innerWidth} 
          y1={yScale(tick)} 
          y2={yScale(tick)}
          stroke="var(--color-border)"
          stroke-width="1"
          opacity="0.3"
        />
      {/each}
      
      <!-- Data points -->
      {#each embeddingData as point, i}
        {@const isHighlighted = highlightedIds.includes(point.ego_aid)}
        <circle
          cx={xScale(+point.umap_1)}
          cy={yScale(+point.umap_2)}
          r={isHighlighted ? "6" : "4"}
          fill={isHighlighted ? "#FF5722" : "#4CAF50"}
          stroke="#333"
          stroke-width="1"
          opacity={highlightedIds.length > 0 ? (isHighlighted ? 1 : 0.3) : 0.7}
          class="data-point"
          onmouseenter={(e) => handleMouseEnter(e, point)}
          onmouseleave={handleMouseLeave}
        />
      {/each}
      
      <!-- No axes -->
      
    </g>
  </svg>

  <!-- Tooltip -->
  {#if showTooltip}
    <div 
      class="tooltip" 
      style="left: {mouseX + 10}px; top: {mouseY - 30}px;"
    >
      {tooltipContent}
    </div>
  {/if}
</div>

<style>
  .plot-container {
    position: relative;
    width: 100%;
  }

  .data-point {
    cursor: pointer;
    transition: r 0.2s ease, opacity 0.2s ease;
  }

  .data-point:hover {
    r: 6;
    opacity: 1;
  }

  .tooltip {
    position: fixed;
    background: var(--color-bg);
    color: var(--color-fg);
    border: 1px solid var(--color-border);
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 12px;
    white-space: pre-line;
    pointer-events: none;
    z-index: 1000;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  :global(.dark) .tooltip {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }
</style>