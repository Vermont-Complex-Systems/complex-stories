<script>
  import * as d3 from 'd3';
  import { processCoauthorData, processPaperData, getCombinedDateRange, ageColorScale, acquaintanceColorScale } from '../utils/combinedChartUtils.js';
  import Tooltip from './Tooltip.svelte';
  import ChangePointChart from './ChangePointChart.svelte';
  import Legend from './Legend.svelte';
  import { dashboardState } from '../state.svelte.ts';

  let { 
    // Data props
    coauthorData = null, 
    paperData = null,
    trainingData = null,
    // Layout props
    width, 
    height, 
    // Chart type and configuration
    chartType = 'coauthor', // 'coauthor' or 'paper'
    colorMode = 'age_diff', // Only applies to coauthor charts
    // Highlight props
    highlightedCoauthor = null,
    highlightedAuthor = null
  } = $props();
  
  // Constants
  const MARGIN_TOP = 50;
  const MARGIN_BOTTOM = 50;
  const MARGIN_LEFT = 40;
  const MARGIN_RIGHT = 40;
  const MAX_CIRCLE_RADIUS = chartType === 'coauthor' ? 12 : 15;

  // Check if we have data based on chart type
  let hasData = $derived(() => {
    if (chartType === 'coauthor') {
      return coauthorData && coauthorData.length > 0;
    } else {
      return paperData && paperData.length > 0;
    }
  });

  let hasTrainingData = $derived(trainingData && trainingData.length > 0);

  // Institution color scales - only for coauthor charts
  let institutionColorScale = $derived.by(() => {
    if (!hasData || chartType !== 'coauthor' || colorMode !== 'institutions') return null;
    
    const institutionField = coauthorData.some(d => d.institution_normalized) 
      ? 'institution_normalized' 
      : 'institution';
    
    const uniqueInstitutions = [...new Set(coauthorData.map(d => d[institutionField]))]
      .filter(inst => inst != null && inst !== '' && inst !== 'Unknown');
    return d3.scaleOrdinal(d3.schemeTableau10).domain(uniqueInstitutions);
  });

  let sharedInstitutionColorScale = $derived.by(() => {
    if (!hasData || chartType !== 'coauthor' || colorMode !== 'shared_institutions') return null;
    
    const sharedField = coauthorData.some(d => d.shared_institutions_normalized) 
      ? 'shared_institutions_normalized' 
      : 'shared_institutions';
    
    const uniqueSharedInstitutions = [...new Set(coauthorData.map(d => d[sharedField]))]
      .filter(inst => inst != null && inst !== '' && inst !== 'Unknown');
    return d3.scaleOrdinal(d3.schemeTableau10).domain(uniqueSharedInstitutions);
  });

  // Time scale
  let timeScale = $derived.by(() => {
    if (!hasData) return d3.scaleTime();
    const dateRange = getCombinedDateRange(paperData, coauthorData);
    return d3.scaleTime()
      .domain(dateRange)
      .range([MARGIN_TOP, height - MARGIN_BOTTOM ]);
  });

  // Year ticks
  let yearTicks = $derived.by(() => {
    if (!hasData) return [];
    const dateRange = getCombinedDateRange(paperData, coauthorData);
    const [startYear, endYear] = d3.extent(dateRange, d => d.getFullYear());
    const yearSpacing = Math.max(1, Math.floor((endYear - startYear) / 15));
    return d3.range(startYear, endYear + 1, yearSpacing);
  });

  // Filter data based on age (only for coauthor charts)
  let filteredCoauthorData = $derived.by(() => {
    if (chartType !== 'coauthor' || !coauthorData || !dashboardState.ageFilter) return coauthorData;
    
    const [minAge, maxAge] = dashboardState.ageFilter;
    return coauthorData.filter(d => {
      const age = +d.author_age || 0;
      return age >= minAge && age <= maxAge;
    });
  });
  
  // Process data based on chart type
  let plotData = $derived.by(() => {
    if (!hasData) return [];
    
    if (chartType === 'coauthor') {
      return processCoauthorData(filteredCoauthorData, width, height, timeScale);
    } else {
      return processPaperData(paperData, width, height, timeScale);
    }
  });

  // Display data with styling
  let displayData = $derived.by(() => {
    if (!plotData.length) return [];
    
    return plotData.map(point => {
      if (chartType === 'coauthor') {
        return processCoauthorPoint(point);
      } else {
        return processPaperPoint(point);
      }
    });
  });

  function processCoauthorPoint(point) {
    // Get the value for coloring
    let colorValue;
    if (colorMode === 'age_diff') {
      colorValue = point.age_category;
    } else if (colorMode === 'acquaintance') {
      colorValue = point.acquaintance;
    } else if (colorMode === 'institutions') {
      colorValue = point.institution_normalized || point.institution;
    } else if (colorMode === 'shared_institutions') {
      colorValue = point.shared_institutions_normalized || point.shared_institutions;
    }

    // Styling logic
    const isNull = colorValue == null || colorValue === '' || colorValue === 'Unknown';
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
        const collabCount = +point.all_times_collabo || 0;
        displayColor = acquaintanceColorScale(collabCount);
      } else if (colorMode === 'institutions') {
        displayColor = institutionColorScale(colorValue);
      } else if (colorMode === 'shared_institutions') {
        displayColor = sharedInstitutionColorScale(colorValue);
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
  }

  function processPaperPoint(point) {
    let opacity = 1;
    
    // Apply author highlight filter if provided
    if (highlightedAuthor) {
      const isHighlightedAuthor = point.ego_aid === highlightedAuthor;
      opacity *= isHighlightedAuthor ? 1 : 0.2;
    }
    
    return {
      ...point,
      opacity,
      displayColor: point.color,
      strokeWidth: 0.8
    };
  }

  // Tooltip state
  let showTooltip = $state(false);
  let tooltipContent = $state('');
  let mouseX = $state(0);
  let mouseY = $state(0);

  function showPointTooltip(event, point) {
    mouseX = event.clientX;
    mouseY = event.clientY;
    
    if (chartType === 'coauthor') {
      const institutionName = point.shared_institutions_normalized || point.shared_institutions || 'Unknown';
      tooltipContent = `Coauthor: ${point.name}\nYear: ${point.year}\nAge difference: ${point.age_diff} years\nTotal collaborations: ${point.all_times_collabo}\nShared Institution: ${institutionName}`;
    } else {
      const citationInfo = point.citation_percentile !== undefined 
        ? `Citations: ${point.cited_by_count} (${Math.round(point.citation_percentile)}th percentile)`
        : `Citations: ${point.cited_by_count}`;
      
      const impactInfo = point.citation_category 
        ? `\nImpact: ${point.citation_category.replace('_', ' ')}`
        : '';
      
      tooltipContent = `Title: ${point.title}\nYear: ${point.year}\n${citationInfo}${impactInfo}\nCoauthors: ${point.authors}\nType: ${point.work_type}\nDOI: ${point.doi}`;
    }
    
    showTooltip = true;
  }

  function hideTooltip() {
    showTooltip = false;
  }

  function handleChartClick(event) {
    if (chartType === 'coauthor') {
      dashboardState.highlightedCoauthor = null;
    }
  }

  function handlePointClick(event, point) {
    if (chartType === 'coauthor') {
      event.stopPropagation();
      dashboardState.highlightedCoauthor = point.name;
    }
  }


</script>

<div class="chart-wrapper">
  <div class="viz-content">
    <div class="plot-container">
      <div class="chart-area">
        <!-- Main timeline visualization -->
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
          <g>
            {#each yearTicks as year}
              {@const yearDate = new Date(year, 0, 1)}
              {@const y = timeScale(yearDate)}
              <line 
                x1={chartType === 'coauthor' ? 0 : MARGIN_LEFT} 
                x2={chartType === 'coauthor' ? width : width - MARGIN_RIGHT} 
                y1={y} 
                y2={y} 
                class="grid-line"
              />
              <text 
                x={chartType === 'coauthor' ? 10 : MARGIN_LEFT - 5} 
                y={y - 5} 
                text-anchor={chartType === 'coauthor' ? "start" : "end"} 
                class="year-label"
              >
                {year}
              </text>
            {/each}
          </g>
          
          <!-- Data points -->
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
                onclick={(e) => handlePointClick(e, point)}
                onkeydown={(e) => (e.key === 'Enter' || e.key === ' ') && handlePointClick(e, point)}
                onmouseenter={(e) => showPointTooltip(e, point)}
                onmouseleave={hideTooltip}
              />
            {/each}
          </g>
        </svg>

        <!-- Right side overlay container for Legend and ChangePoint Chart (only for coauthor charts) -->
        {#if chartType === 'coauthor'}
          <div class="right-overlay-container">
            <!-- Legend positioned on the right -->
            <div class="legend-container">
              <Legend 
                {colorMode}
                {coauthorData}
                visible={hasData}
              />
            </div>
            
            <!-- ChangePoint Chart positioned underneath legend -->
            {#if hasTrainingData && colorMode === 'age_diff'}
              <div class="changepoint-container">
                <ChangePointChart data={trainingData} visible={hasTrainingData && colorMode === 'age_diff'} />
              </div>
            {/if}
          </div>
        {/if}
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
  }

  /* Right side overlay container */
  .right-overlay-container {
    position: absolute;
    top: 2rem;
    right: 1rem;
    z-index: 10;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-end;
  }

  /* Legend positioning - now relative within container */
  .legend-container {
    pointer-events: none;
  }

  .legend-container :global(.legend) {
    pointer-events: auto;
  }

  /* ChangePoint Chart positioning - now relative within container */
  .changepoint-container {
    /* No positioning needed - handled by flex container */
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

  /* Responsive design */
  @media (max-width: 1024px) {
    .right-overlay-container {
      top: 1.5rem;
      right: 0.5rem;
    }
  }

  @media (max-width: 768px) {
    .right-overlay-container {
      top: 1rem;
      right: 0.25rem;
    }
    
    .legend-container :global(.legend) {
      font-size: 10px;
      padding: 8px;
      min-width: 150px;
      max-width: 180px;
    }
  }

  @media (max-width: 480px) {
    .plot-container {
      flex-direction: column;
    }

    .right-overlay-container {
      position: relative;
      top: 0;
      right: auto;
      margin-top: 1rem;
      align-items: center;
    }
  }
</style>