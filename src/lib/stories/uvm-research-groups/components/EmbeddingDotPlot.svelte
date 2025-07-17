<script>
  import * as d3 from 'd3';
  import Legend from './EmbeddingDotPlot.Legend.svelte'; 
  import Select from './EmbeddingDotPlot.Select.svelte'; 
  
  let { 
    embeddingData = [], 
    width = 800, 
    height = 600,
    margin = { top: 10, right: 85, bottom: 20, left: 0 },
    selectedCoauthors = [], // Array of ego_aid values to highlight
    timeRange = null // [startpub_Year, endpub_Year] or null for no time filtering
  } = $props();


    // Step 1: Extract coauthor names from selection
  let selectedCoauthorNames = $derived(
    new Set(selectedCoauthors.map(c => c.name))
  );

  // Step 2: Filter embedding data to only Peter's papers
  let petersPapers = $derived(
    embeddingData.filter(point => point.ego_aid === 'A5040821463')
  );

  // Step 3: From Peter's papers, find which ones have selected coauthors
  let highlightedPaperIndices = $derived.by(() => {
    if (selectedCoauthors.length === 0) return new Set();
    
    const highlighted = new Set();
    
    petersPapers.forEach((paper, originalIndex) => {
      const hasSelectedCoauthor = [...selectedCoauthorNames].some(name => 
        paper.authors?.includes(name)
      );
      
      const isInTimeRange = !timeRange || 
        (paper.pub_year >= timeRange[0] && paper.pub_year <= timeRange[1]);
      
      if (hasSelectedCoauthor && isInTimeRange) {
        // Find the original index in embeddingData
        const embeddingIndex = embeddingData.indexOf(paper);
        highlighted.add(embeddingIndex);
      }
    });
    
    return highlighted;
  });

  // Calculate inner dimensions
  let innerWidth = $derived(width - margin.left - margin.right);
  let innerHeight = $derived(height - margin.top - margin.bottom);

  let colorFOS = $state('s2FieldsOfStudy')

  // Get unique fields of study
  const uniqueFields = $derived([...new Set(embeddingData.map(d => {
      const fieldValue = d[colorFOS];
      if (!fieldValue) return null;
      
      // Only split for s2FieldsOfStudy, use raw value for others
      if (colorFOS === 's2FieldsOfStudy') {
        return fieldValue.split("; ")[1];
      } else {
        return fieldValue;
      }
    }))].filter(Boolean));

  const fieldToIndex = $derived(new Map(uniqueFields.map((field, index) => [field, index])));

  // Create scales
  let zScale = $derived.by(() => {
    if (!embeddingData.length) return d3.scaleOrdinal();
    
      const baseScale = d3.scaleSequential()
        .domain([0, uniqueFields.length - 1])
        .interpolator(d3.interpolateTurbo);
      
      // Return a function that handles null values
      return (fieldIndex) => {
        if (fieldIndex === null || fieldIndex === undefined) {
          return '#d3d3d3'; // Light grey for null values
        }
        return baseScale(fieldIndex);
      };
  });

  
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

  function handleMouseEnter(event, point, i) {
    const isPeterDodds = point.ego_aid === 'A5040821463';
    const shouldHighlight = isPeterDodds && highlightedPaperIndices.has(i);
  
  const shouldShowTooltip = (selectedCoauthors.length === 0 && !timeRange) || shouldHighlight;
  
  if (shouldShowTooltip) {
    mouseX = event.clientX;
    mouseY = event.clientY;
    tooltipContent = `title: ${point.title}]\nfos (MAG): ${point.fieldsOfStudy}\nfos (S2): ${point.s2FieldsOfStudy?.split("; ")[1]}\nFaculty main department: ${point.host_dept}\nabstract: ${point.abstract}\nauthors: ${point.authors}\ndoi: ${point.doi}\npub_year: ${point.pub_year}`;
    showTooltip = true;
  }
}

  function handleMouseLeave() {
    showTooltip = false;
  }

  const getFieldValue = $derived.by(() => {
  return (point) => {
    const fieldValue = colorFOS === 's2FieldsOfStudy' 
      ? point[colorFOS]?.split("; ")[1] 
      : point[colorFOS];
    
    return fieldValue ? fieldToIndex.get(fieldValue) : null;
  };
});


</script>

<Select 
  bind:value={colorFOS}
  options={ [
    { value: 's2FieldsOfStudy', label: 'S2 Fields of Study' },
    { value: 'fieldsOfStudy', label: 'MAG Fields of Study' },
    { value: 'host_dept', label: 'Faculty main department' }
  ] }
  label="Color by:"
  maxWidthRatio={0.25}
/>

<Legend 
  uniqueFields={uniqueFields}
  colorScale={zScale}
  maxWidthRatio={0.7} 
  itemWidth={100}
/>

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
        {@const isPeterDodds = point.ego_aid === 'A5040821463'}
        {@const shouldHighlight = isPeterDodds && highlightedPaperIndices.has(i)}
        {@const fieldValue = getFieldValue(point)}
        {@const isNullField = fieldValue === null}
        <circle
          cx={xScale(+point.umap_1)}
          cy={yScale(+point.umap_2)}
          r={shouldHighlight ? "6" : "4"}
          fill={shouldHighlight ? "red" : zScale(fieldValue)}
          stroke={shouldHighlight ? "black" : null}
          opacity={
            shouldHighlight ? 1 : 
            (selectedCoauthors.length > 0 || timeRange) ? 
              (isNullField ? 0.15 : 0.3) : 
              (isNullField ? 0.3 : 0.7)
          }
          class="data-point"
          onmouseenter={(e) => handleMouseEnter(e, point, i)}
          onmouseleave={handleMouseLeave}
        />
      {/each}
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