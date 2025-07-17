<script>
  import * as d3 from 'd3';
  import { innerWidth } from 'svelte/reactivity/window';
  
  let { 
    uniqueFields = [],
    colorScale = d3.scaleOrdinal(),
    maxWidthRatio = 0.8, // Use 80% of window width
    itemWidth = 120,
    itemHeight = 20,
    padding = 10,
    itemsPerRow = null // Auto-calculate if not provided
  } = $props();

  // Calculate max width based on window size
  let maxWidth = $derived((innerWidth.current || 800) * maxWidthRatio);

  // Calculate items per row based on maxWidth
  let calculatedItemsPerRow = $derived(
    itemsPerRow || Math.floor((maxWidth - padding * 2) / itemWidth)
  );

  // Calculate number of rows needed
  let numRows = $derived(Math.ceil(uniqueFields.length / calculatedItemsPerRow));

  // Calculate actual legend dimensions
  let legendWidth = $derived(Math.min(maxWidth, calculatedItemsPerRow * itemWidth + padding * 2));
  let legendHeight = $derived(numRows * itemHeight + padding * 2);
</script>

<div class="legend-container">
  <svg width={legendWidth} height={legendHeight}>
    <!-- Background -->
    <rect 
      width={legendWidth} 
      height={legendHeight} 
      fill="var(--color-bg)" 
      stroke="var(--color-border)"
      stroke-width="1"
      rx="4"
    />
    
    <!-- Legend items -->
    {#each uniqueFields as field, i}
      {@const row = Math.floor(i / calculatedItemsPerRow)}
      {@const col = i % calculatedItemsPerRow}
      <g transform="translate({padding + col * itemWidth}, {padding + row * itemHeight})">
        <!-- Color square -->
        <rect 
          x="0" 
          y="2" 
          width="12" 
          height="12" 
          fill={colorScale(i)}
        />
        
        <!-- Field label -->
        <text 
          x="18" 
          y="10" 
          font-size="11" 
          fill="var(--color-fg)"
          dominant-baseline="middle"
        >
          {field ? (field.length > 12 ? field.substring(0, 12) + '...' : field) : 'Unknown'}
        </text>
      </g>
    {/each}
  </svg>
</div>

<style>
  .legend-container {
    display: inline-block;
    margin: 5px 0 0 0;
  }
  
  text {
    font-family: system-ui, -apple-system, sans-serif;
  }
</style>