<script>
  import * as d3 from 'd3';
  import { processCombinedDataPoints, getCombinedDataDateRange } from '../utils/combinedChartUtils.js';
  import { getPointColor } from '../utils/colorScales.js';
  import Tooltip from './Tooltip.svelte';
  import Legend from './Legend.svelte';

  let { scrollyIndex, DoddsCoauthorData, DoddsPaperData, width, height } = $props();
  
  // Derived data
  let hasData = $derived(DoddsCoauthorData.length > 0 && DoddsPaperData.length > 0);

  // Constants
  const MARGIN_TOP = 50;
  const MAX_CIRCLE_RADIUS = 15;

  // Step configurations
  const stepConfigs = {
    0: { yearRange: [1999, 2025], colorMode: 'age_diff', highlightedAuthor: null, viewMode: 'normal' },
    1: { yearRange: [1999, 2006], colorMode: 'age_diff', highlightedAuthor: null, viewMode: 'normal', translateToYear: 2016 },
    2: { yearRange: [1999, 2025], colorMode: 'shared_institutions', highlightedAuthor: null, viewMode: 'normal', translateToYear: 2018 },
    3: { yearRange: [2006, 2017], colorMode: 'age_diff', highlightedAuthor: null, viewMode: 'normal', translateToYear: 2023 },
    4: { yearRange: [1999, 2025], colorMode: 'age_diff', highlightedAuthor: 'A5002034958', viewMode: 'overview' },
    5: { yearRange: [1999, 2025], colorMode: 'age_diff', highlightedAuthor: 'A5078987306', viewMode: 'overview' },
    6: { yearRange: [2006, 2025], colorMode: 'age_diff', highlightedAuthor: null, viewMode: 'normal', translateToYear: 2012 },
  };

  // Current config - derived directly from scrollyIndex
  let currentConfig = $derived(stepConfigs[scrollyIndex] || stepConfigs[0]);

  // BREAK THE CYCLE: Calculate marginBottom first, independently
  let marginBottom = $derived(currentConfig.viewMode === 'overview' ? 500 : 0);

  // Time scale - now only depends on marginBottom, not full chartState
  let timeScale = $derived.by(() => {
    if (!hasData) return d3.scaleTime();
    const dateRange = getCombinedDataDateRange(DoddsCoauthorData, DoddsPaperData);
    return d3.scaleTime()
      .domain(dateRange)
      .range([MARGIN_TOP, height - marginBottom - MAX_CIRCLE_RADIUS - MARGIN_TOP]);
  });

  // Chart state 
  let chartState = $derived.by(() => {
    const config = currentConfig;
    
    // Calculate view transform
    let viewTransform;
    if (config.viewMode === 'overview') {
      viewTransform = {
        scaleX: 0.8,
        scaleY: 0.8,
        translateY: -height / 3.5
      };
    } else if (config.translateToYear && hasData) {
      const targetDate = new Date(config.translateToYear, 0, 1);
      const centerY = timeScale(targetDate);
      const viewCenterY = height / 2;
      let translation = viewCenterY - centerY;
      
      const maxTranslation = height * 0.6;
      translation = Math.max(-maxTranslation, Math.min(maxTranslation, translation));
      
      viewTransform = {
        scaleX: 1,
        scaleY: 1,
        translateY: translation
      };
    } else {
      viewTransform = {
        scaleX: 1,
        scaleY: 1,
        translateY: 0
      };
    }

    return {
      yearFilterMin: config.yearRange[0],
      yearFilterMax: config.yearRange[1],
      colorMode: config.colorMode,
      highlightedAuthor: config.highlightedAuthor,
      marginBottom, // Include marginBottom for completeness
      ...viewTransform
    };
  });

  // Year ticks - derived
  let yearTicks = $derived.by(() => {
    if (!hasData) return [];
    const dateRange = getCombinedDataDateRange(DoddsCoauthorData, DoddsPaperData);
    const [startYear, endYear] = d3.extent(dateRange, d => d.getFullYear());
    const yearSpacing = Math.max(1, Math.floor((endYear - startYear) / 15));
    return d3.range(startYear, endYear + 1, yearSpacing);
  });

  // Plot data - derived
  let plotData = $derived.by(() => {
    if (!hasData) return [];
    return processCombinedDataPoints(DoddsCoauthorData, DoddsPaperData, width, height, timeScale);
  });

  // Display data - derived
  let displayData = $derived.by(() => {
    if (!plotData.length) return [];
    
    return plotData.map(point => {
      const pointYear = parseInt(point.year);
      const inYearRange = pointYear >= chartState.yearFilterMin && pointYear <= chartState.yearFilterMax;
      const yearOpacity = inYearRange ? 1 : 0.2;
      
      const isHighlightedAuthor = chartState.highlightedAuthor && point.coauth_aid === chartState.highlightedAuthor;
      const authorOpacity = chartState.highlightedAuthor ? (isHighlightedAuthor ? 1 : 0.2) : 1;
      
      return {
        ...point,
        opacity: yearOpacity * authorOpacity,
        displayColor: getPointColor(point, chartState.colorMode),
        isHighlighted: isHighlightedAuthor,
        r: point.r * (isHighlightedAuthor ? 1 : 1)
      };
    });
  });

  // Tooltip 
  let showTooltip = $state(false);
  let tooltipContent = $state('');
  let mouseX = $state(0);
  let mouseY = $state(0);

  function showPointTooltip(event, point) {
    mouseX = event.clientX;
    mouseY = event.clientY;
    
    if (point.type === 'paper') {
      tooltipContent = `Title: ${point.title}\nYear: ${point.year}\nCitations: ${point.cited_by_count}\nCoauthors: ${point.nb_coauthors}`;
    } else {
      tooltipContent = `Coauthor: ${point.name}\nYear: ${point.year}\nAge difference: ${point.age_diff} years\nCollaborations: ${point.collabs}`;
    }
    
    showTooltip = true;
  }

  function hideTooltip() {
    showTooltip = false;
  }

  // Keyboard event handler for data points
  function handlePointKeydown(event, point) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      showPointTooltip(event, point);
    } else if (event.key === 'Escape') {
      hideTooltip();
    }
  }
</script>


<div class="chart-wrapper">
  <div class="viz-content">
    <div class="plot-container">
      <svg {width} {height} 
           style="transform: scaleX({chartState.scaleX}) scaleY({chartState.scaleY}) translateY({chartState.translateY}px); transition: transform 0.8s cubic-bezier(0.23, 1, 0.32, 1);">
        
        <g>
          <text x={width * 0.25} y={MARGIN_TOP - 30} text-anchor="middle" class="chart-label">Coauthors</text>
          <text x={width * 0.6} y={MARGIN_TOP - 30} text-anchor="middle" class="chart-label">Papers</text>

          {#each yearTicks as year}
            {@const yearDate = new Date(year, 0, 1)}
            {@const y = timeScale(yearDate)}
            <line x1="0" x2={width} y1={y} y2={y} class="grid-line"/>
            <text x="10" y={y - 5} text-anchor="start" class="year-label">{year}</text>
          {/each}
        </g>
        
        <!-- Data points with proper accessibility -->
        {#each displayData as point, index}
          <circle
            cx={point.x}
            cy={point.y}
            r={point.r}
            fill={point.displayColor}
            stroke="black"
            stroke-width={point.type === 'paper' ? "0.8" : "0.3"}
            fill-opacity={point.opacity}
            class="data-point"
            role="button"
            tabindex="0"
            aria-label={point.type === 'paper' ? 
              `Paper: ${point.title}, Year: ${point.year}` : 
              `Coauthor: ${point.name}, Year: ${point.year}`}
            onmouseenter={(e) => showPointTooltip(e, point)}
            onmouseleave={hideTooltip}
            onkeydown={(e) => handlePointKeydown(e, point)}
            onfocus={(e) => showPointTooltip(e, point)}
            onblur={hideTooltip}
          />
        {/each}
      </svg>
    
      <Legend colorMode={chartState.colorMode} visible={chartState.scaleX >= 0.9} />
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
    --chart-tooltip-bg: var(--color-bg);
    width: 100%;
  }

  .plot-container {
    display: flex;
    justify-content: center;
    position: relative;
  }

  /* SVG element styling using design tokens */
  .chart-wrapper :global(.chart-label) {
    font-size: var(--font-size-small);
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
    transition: fill 0.6s ease, fill-opacity 0.7s ease;
  }

  .chart-wrapper :global(.data-point:focus) {
    outline: 2px solid var(--color-focus, #3b82f6);
    outline-offset: 2px;
  }
</style>