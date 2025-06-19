<!-- SimplifiedMorphingChart.svelte -->
<script>
  import * as d3 from 'd3';
  import { processCombinedDataPoints, getCombinedDataDateRange } from '../utils/combinedChartUtils.js';
  import Legend from './Legend.svelte';

  let { scrollyIndex, coauthorData, paperData, width, height } = $props();

  console.log("Timeline chart loaded with:", coauthorData?.length, "coauthors,", paperData?.length, "papers");

  // Filter data for Dodds
  let DoddsCoauthorData = $derived(coauthorData?.filter(c => c.uvm_faculty_2023 === "False") || []);
  let DoddsPaperData = $derived(paperData?.filter(p => p.ego_aid === "A5040821463") || []);

  // State variables
  let colorMode = $state('age_diff');
  let highlightedAuthor = $state(null);
  let dataReady = $state(false);
  let yearFilterMin = $state(1999);
  let yearFilterMax = $state(2025);
  let scaleX = $state(1);
  let scaleY = $state(1);
  let translateY = $state(0);
  let plotData = $state([]);
  
  // Simple tooltip state
  let showTooltip = $state(false);
  let tooltipContent = $state('');
  let mouseX = $state(0);
  let mouseY = $state(0);

  // Check if data is ready
  let hasData = $derived(DoddsCoauthorData.length > 0 && DoddsPaperData.length > 0);

  // FIXED: Consistent margins with space for circle radius
  const MARGIN_TOP = 50;
  const MARGIN_BOTTOM = 415; // Extra space for circles at bottom
  const MAX_CIRCLE_RADIUS = 15; // From radiusScale max

  // FIXED: D3 time scale with proper margins accounting for circle radius
  let timeScale = $derived.by(() => {
    if (!hasData) return d3.scaleTime();
    const dateRange = getCombinedDataDateRange(DoddsCoauthorData, DoddsPaperData);
    return d3.scaleTime()
      .domain(dateRange)
      .range([MARGIN_TOP, height - MARGIN_BOTTOM - MAX_CIRCLE_RADIUS - MARGIN_TOP]); // More space at bottom
  });

  // D3 Color scales
  const ageColorScale = d3.scaleOrdinal()
    .domain(['older', 'same', 'younger'])
    .range(['#404788FF', '#20A387FF', '#FDE725FF']);

  const institutionColorScale = d3.scaleOrdinal()
    .domain([
      'University of Vermont',
      'Massachusetts Institute of Technology',
      'Earth Island Institute', 
      'Columbia University',
      'Santa Fe Institute'
    ])
    .range(['#2E8B57', '#FF6B35', '#4682B4', '#4682B4', '#B59410']);

  // FIXED: Year ticks using consistent date parsing
  let yearTicks = $derived.by(() => {
    if (!hasData) return [];
    const dateRange = getCombinedDataDateRange(DoddsCoauthorData, DoddsPaperData);
    const [startYear, endYear] = d3.extent(dateRange, d => d.getFullYear());
    
    // Create year range with reasonable spacing
    const yearSpacing = Math.max(1, Math.floor((endYear - startYear) / 15));
    return d3.range(startYear, endYear + 1, yearSpacing);
  });

  // Create timeline data
  function createTimelineData() {
    if (!hasData) {
      console.log("Data not ready yet...");
      return [];
    }
    console.log("Creating timeline with", DoddsCoauthorData.length, "coauthors and", DoddsPaperData.length, "papers");
    return processCombinedDataPoints(DoddsCoauthorData, DoddsPaperData, width, height, timeScale);
  }

  // Point color function using D3 scales
  function getPointColor(point) {
    if (point.type === 'paper') return "#888888";
    
    if (colorMode === 'shared_institutions' && point.type === 'coauthor') {
      const sharedInst = point.shared_institutions || 'None';
      if (sharedInst === 'None' || sharedInst === '') return "#D3D3D3";
      
      for (const institution of institutionColorScale.domain()) {
        if (sharedInst.includes(institution)) {
          return institutionColorScale(institution);
        }
      }
      return "#4682B4";
    } else if (colorMode === 'age_diff' && point.type === 'coauthor') {
      const ageDiff = +point.age_diff;
      if (ageDiff > 7) return ageColorScale('older');
      if (ageDiff < -7) return ageColorScale('younger');
      return ageColorScale('same');
    }
    return point.color;
  }

  // Simple tooltip functions
  function showPointTooltip(event, point) {
    mouseX = event.clientX;
    mouseY = event.clientY;
    
    if (point.type === 'paper') {
      tooltipContent = `${point.title}\nYear: ${point.year}\nCitations: ${point.cited_by_count}\nCoauthors: ${point.nb_coauthors}`;
    } else {
      tooltipContent = `${point.name}\nYear: ${point.year}\nAge difference: ${point.age_diff} years\nCollaborations: ${point.collabs}`;
    }
    
    showTooltip = true;
  }

  function hideTooltip() {
    showTooltip = false;
  }

  // Step configurations
  const stepConfigs = {
    0: { yearRange: [1999, 2025], colorMode: 'age_diff', highlightedAuthor: null, viewMode: 'normal' },
    1: { yearRange: [1999, 2006], colorMode: 'age_diff', highlightedAuthor: null, viewMode: 'normal', translateToYear: 2016 },
    2: { yearRange: [1999, 2025], colorMode: 'shared_institutions', highlightedAuthor: null, viewMode: 'normal', translateToYear: 2018 },
    3: { yearRange: [2006, 2017], colorMode: 'age_diff', highlightedAuthor: null, viewMode: 'normal', translateToYear: 2023 },
    4: { yearRange: [1999, 2025], colorMode: 'age_diff', highlightedAuthor: 'A5002034958', viewMode: 'overview' },
    5: { yearRange: [1999, 2025], colorMode: 'age_diff', highlightedAuthor: 'A5078987306', viewMode: 'overview' },
    6: { yearRange: [2006, 2025], colorMode: 'shared_institutions', highlightedAuthor: null, viewMode: 'normal' }
  };

  // Apply step configuration
  function applyStepConfig(config) {
    const {
      yearRange = [1999, 2025],
      colorMode: newColorMode = 'age_diff',
      highlightedAuthor: newHighlightedAuthor = null,
      viewMode = 'normal',
      translateToYear = null
    } = config;

    yearFilterMin = yearRange[0];
    yearFilterMax = yearRange[1];
    colorMode = newColorMode;
    highlightedAuthor = newHighlightedAuthor;

    if (viewMode === 'overview') {
      scaleX = 0.8;
      scaleY = 0.8;
      translateY = -height/4;
    } else if (translateToYear) {
      const targetDate = new Date(translateToYear, 0, 1);
      const centerY = timeScale(targetDate);
      const viewCenterY = height / 2;
      let translation = viewCenterY - centerY;
      
      const maxTranslation = height * 0.6;
      translation = d3.max([-maxTranslation, d3.min([maxTranslation, translation])]);
      
      scaleX = 1;
      scaleY = 1;
      translateY = translation;
    } else {
      scaleX = 1;
      scaleY = 1;
      translateY = 0;
    }
  }

  // Display data
  let displayData = $derived.by(() => {
    if (!plotData.length) return [];
    
    return plotData.map(point => {
      const pointYear = parseInt(point.year);
      const inYearRange = pointYear >= yearFilterMin && pointYear <= yearFilterMax;
      const yearOpacity = inYearRange ? 1 : 0.2;
      
      const isHighlightedAuthor = highlightedAuthor && point.coauth_aid === highlightedAuthor;
      const authorOpacity = highlightedAuthor ? (isHighlightedAuthor ? 1 : 0.2) : 1;
      
      return {
        ...point,
        opacity: yearOpacity * authorOpacity,
        displayColor: getPointColor(point),
        isHighlighted: isHighlightedAuthor,
        r: point.r * (isHighlightedAuthor ? 1.3 : 1)
      };
    });
  });

  // Effects
  $effect(() => {
    if (hasData) {
      console.log("Data is ready, creating timeline...");
      plotData = createTimelineData();
      dataReady = true;
    }
  });

  $effect(() => {
    if (!dataReady) return;
    const config = scrollyIndex !== undefined ? (stepConfigs[scrollyIndex] || stepConfigs[0]) : stepConfigs[0];
    console.log("Applying config for step", scrollyIndex, config);
    applyStepConfig(config);
  });

</script>

<div class="chart-wrapper">
  <!-- <h2>
    <span>{scrollyIndex !== undefined ? `Step ${scrollyIndex}` : "Overview"}</span>
  </h2> -->
  <div class="viz-content">
    <div class="plot-container">
      <svg {width} {height} 
           style="transform: scaleX({scaleX}) scaleY({scaleY}) translateY({translateY}px); transition: transform 0.8s cubic-bezier(0.23, 1, 0.32, 1);">
        
        <g>
          <text x={width * 0.25} y={MARGIN_TOP - 30} text-anchor="middle" font-size="14" font-weight="bold" fill="#666">Coauthors</text>
          <text x={width * 0.6} y={MARGIN_TOP - 30} text-anchor="middle" font-size="14" font-weight="bold" fill="#666">Papers</text>

          {#each yearTicks as year}
            {@const yearDate = new Date(year, 0, 1)}
            {@const y = timeScale(yearDate)}
            <line x1="0" x2={width} y1={y} y2={y} stroke="#f0f0f0" stroke-width="0.1"/>
            <text x="10" y={y - 5} text-anchor="start" font-size="11" fill="#666">{year}</text>
          {/each}
          
        </g>
        
        <!-- Data points -->
        {#each displayData as point}
          <circle
            cx={point.x}
            cy={point.y}
            r={point.r}
            fill={point.displayColor}
            stroke="black"
            stroke-width={point.type === 'paper' ? "0.8" : "0.3"}
            fill-opacity={point.opacity}
            style="cursor: pointer; transition: fill 0.6s ease, fill-opacity 0.7s ease;"
            on:mouseenter={(e) => showPointTooltip(e, point)}
            on:mouseleave={hideTooltip}
          />
        {/each}
        
      </svg>
    
      <Legend {colorMode} visible={scaleX >= 0.9} />

    {#if scrollyIndex === undefined}
      <p class="start-message">Scroll down to explore the academic timeline</p>
    {/if}
  </div>
</div>
</div>

{#if showTooltip}
  <div class="tooltip" style="left: {mouseX + 10}px; top: {mouseY - 30}px;">
    {tooltipContent}
  </div>
{/if}


<style>


  .chart-wrapper {
    width: 100%;
  }


  .plot-container {
      display: flex;
      justify-content: center;
      position: relative; /* For absolute positioning of legend */
    }

  /* h2 {
    position: sticky;
    top: 0;
    z-index: 10;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    margin: 0 0 1rem 0;
    padding: 0.75rem 0;
    font-size: 1.2rem;
    color: #2d3748;
    font-family: system-ui, sans-serif;
    font-weight: 400;
    border-bottom: 1px solid #e2e8f0;
  }

  h2 span {
    color: #667eea;
    font-weight: bold;
  } */

  .start-message {
    color: #718096;
    font-size: 1rem;
    margin-top: 1rem;
    font-style: italic;
  }

  .tooltip {
    white-space: pre-line;
    line-height: 1.4;
    position: fixed;
    background: rgba(0, 0, 0, 0.9);
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 12px;
    pointer-events: none;
    z-index: 10000;
    max-width: 300px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    font-family: system-ui, sans-serif;
  }
</style>