<script>
  import * as d3 from 'd3';
  import Legend from './EmbeddingDotPlot.Legend.svelte'; 
  import Select from './EmbeddingDotPlot.Select.svelte'; 
  import Annotate from './EmbeddingDotPlot.Text.svelte'; 
  
  let { 
    embeddingData = [], 
    width = 800, 
    height = 600,
    margin = { top: 10, right: 155, bottom: 20, left: 0 },
    selectedCoauthors = [], // Array of ego_author_id values to highlight
    timeRange = null // [startpub_Year, endpub_Year] or null for no time filtering
  } = $props();

  // Adjust margin for mobile
  let adjustedMargin = $derived(
    width <= 500 ? { ...margin, right: 20 } : margin
  );


  // Step 1: Extract coauthor names from selection
  let selectedCoauthorNames = $derived(
    new Set(selectedCoauthors.map(c => c.coauthor_name))
  );

  // Create arrays for highlighted and non-highlighted points
  let { highlightedPoints, nonHighlightedPoints } = $derived.by(() => {
    const highlighted = [];
    const nonHighlighted = [];

    embeddingData.forEach((point, i) => {
      const isPeterDodds = point.ego_author_id === 'https://openalex.org/A5040821463';

      let shouldHighlight = false;
      if (isPeterDodds && selectedCoauthors.length > 0) {
        const hasSelectedCoauthor = [...selectedCoauthorNames].some(name =>
          point.coauthor_names?.includes(name)
        );

        const isInTimeRange = !timeRange ||
          (point.publication_year >= timeRange[0] && point.publication_year <= timeRange[1]);

        shouldHighlight = hasSelectedCoauthor && isInTimeRange;
      }

      const pointData = {
        ...point,
        index: i,
        fieldValue: getFieldValue(point),
        shouldHighlight
      };

      if (shouldHighlight) {
        highlighted.push(pointData);
      } else {
        nonHighlighted.push(pointData);
      }
    });

    return { highlightedPoints: highlighted, nonHighlightedPoints: nonHighlighted };
  });

  // Calculate inner dimensions
  let innerWidth = $derived(width - adjustedMargin.left - adjustedMargin.right);
  let innerHeight = $derived(height - adjustedMargin.top - adjustedMargin.bottom);

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
    const shouldShowTooltip = (selectedCoauthors.length === 0 && !timeRange) || point.shouldHighlight;
  
    if (shouldShowTooltip) {
      mouseX = event.clientX;
      mouseY = event.clientY;
      
      // FIXED: Updated tooltip to use correct column names
      tooltipContent = `title: ${point.title.toUpperCase()}\nfos (MAG): ${point.fieldsOfStudy || 'N/A'}\nfos (S2): ${point.s2FieldsOfStudy?.split("; ")[1] || 'N/A'}\nFaculty main department: ${point.host_dept || 'N/A'} (${point.college || 'N/A'})\nabstract: ${point.abstract || 'N/A'}\ncoauthors: ${point.coauthor_names || 'N/A'}\ndoi: ${point.doi || 'N/A'}\npub_year: ${point.publication_year || 'N/A'}`;
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

  // const annotations = [
  //   {
  //     x: 4.2,  
  //     y: 7, 
  //     text: "Biomedical",
  //     style: {
  //       color: "red",
  //       fontSize: "14px",
  //       fontWeight: "bold",
  //       textAnchor: "middle"
  //     }
  //   }
  // ]

</script>

<Select 
  bind:value={colorFOS}
  options={ [
    { value: 's2FieldsOfStudy', label: 'S2 Fields of Study' },
    { value: 'host_dept', label: 'Faculty main department' },
    { value: 'college', label: 'Faculty college' }
  ] }
  label="Color by:"
  maxWidthRatio={0.25}
/>

<Legend 
  uniqueFields={uniqueFields}
  colorScale={zScale}
  maxWidthRatio={0.7} 
  itemWidth={200}
/>

<div class="plot-container">
  <svg {width} {height}>
    <!-- Background -->
    <rect width={width} height={height} fill="var(--color-bg)" />
    
    <!-- Main plot area -->
    <g transform="translate({adjustedMargin.left},{adjustedMargin.top})">
      
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
      
      <!-- Non-highlighted points -->
      {#each nonHighlightedPoints as point}
        {@const isNullField = point.fieldValue === null}
        <circle
          cx={xScale(+point.umap_1)}
          cy={yScale(+point.umap_2)}
          r="4"
          fill={zScale(point.fieldValue)}
          opacity={
            (selectedCoauthors.length > 0 || timeRange) ?
              (isNullField ? 0.15 : 0.3) :
              (isNullField ? 0.3 : 0.7)
          }
          class="data-point"
          role="button"
          tabindex="0"
          onmouseenter={(e) => handleMouseEnter(e, point, point.index)}
          onmouseleave={handleMouseLeave}
        />
      {/each}

      <!-- Highlighted points on top -->
      {#each highlightedPoints as point}
        <circle
          cx={xScale(+point.umap_1)}
          cy={yScale(+point.umap_2)}
          r="6"
          fill="red"
          stroke="black"
          stroke-width="1"
          opacity="1"
          class="data-point highlighted"
          role="button"
          tabindex="0"
          onmouseenter={(e) => handleMouseEnter(e, point, point.index)}
          onmouseleave={handleMouseLeave}
        />
      {/each}

      <!-- {#each annotations as annotation}
        <text
          x={xScale(annotation.x)}
          y={yScale(annotation.y)}
          fill={annotation.style?.color || "var(--color-fg)"}
          font-size={annotation.style?.fontSize || "12px"}
          font-weight={annotation.style?.fontWeight || "normal"}
          text-anchor={annotation.style?.textAnchor || "start"}
          dominant-baseline={annotation.style?.dominantBaseline || "middle"}
          opacity={annotation.style?.opacity || 1}
          class="annotation-text"
        >
          {annotation.text}
        </text>
      {/each} -->
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