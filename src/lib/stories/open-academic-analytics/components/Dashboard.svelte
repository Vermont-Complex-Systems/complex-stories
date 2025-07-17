<script>
  import { Plot, Dot, LineY, AreaY, HTMLTooltip } from 'svelteplot';

  import CoauthorChart from './CoauthorChart.svelte';
  import PaperChart from './PaperChart.svelte';
  import Toggle from './helpers/Toggle.svelte'
  import RangeFilter from './helpers/RangeFilter.svelte'
  import CollabChart from './Collaboration.Agg.svelte'
  import { dashboardState, dataState, uiState } from '../state.svelte.ts';
  import { innerWidth } from 'svelte/reactivity/window';
  import { getCombinedDateRange, ageColorScale, acquaintanceColorScale, processCoauthorData, processPaperData } from '../utils/combinedChartUtils.js';
  import * as d3 from 'd3';
  
  let { paperData, coauthorData, trainingAggData, productivityData, trainingData } = $props();

  // Calculate available width for charts considering sidebar and layout
  let chartWidth = $derived.by(() => {
    const screenWidth = innerWidth.current;
    if (!screenWidth) return 400; // SSR fallback
    
    // Calculate actual available space step by step
    const sidebarWidth = uiState.sidebarCollapsed ? 80 : 272; // 5rem or 17rem
    const mainContentPadding = 88; // 5.5rem left padding
    const dashboardPadding = 20; // Reduced from 40
    const chartsGridGap = 20; // gap between the two charts
    const chartPanelPadding = 20; // Reduced from 40
    
    // Available width for the entire charts container
    const availableForChartsContainer = screenWidth - sidebarWidth - mainContentPadding - dashboardPadding;
    
    // Each chart gets half the container minus gap and panel padding
    const availablePerChart = (availableForChartsContainer - chartsGridGap) / 2 - chartPanelPadding;
    
    // Ensure minimum and maximum sizes - increased max
    const finalWidth = Math.max(400, Math.min(700, availablePerChart)); // Increased from 300,500
    
    return finalWidth;
  });

  const chartHeight = $derived(coauthorData?.length > 600 ? coauthorData?.length < 1500 ? 1200 : 2200 : 800);

  // Create shared time scale for both charts
  let sharedTimeScale = $derived.by(() => {
    if (!paperData && !coauthorData) return d3.scaleTime();
    
    const dateRange = getCombinedDateRange(paperData, coauthorData);
    return d3.scaleTime()
      .domain(dateRange)
      .range([50, chartHeight - 50]); // MARGIN_TOP to height - MARGIN_BOTTOM
  });

  // Create color scales for coauthor chart based on current mode
  let coauthorColorScale = $derived.by(() => {
    if (!coauthorData || coauthorData.length === 0) return null;
    
    const colorMode = dashboardState.colorMode;
    
    if (colorMode === 'age_diff') {
      return ageColorScale;
    } else if (colorMode === 'acquaintance') {
      return acquaintanceColorScale;
    } else if (colorMode === 'institutions') {
      const institutionField = coauthorData.some(d => d.institution_normalized) 
        ? 'institution_normalized' 
        : 'institution';
      
      const uniqueInstitutions = [...new Set(coauthorData.map(d => d[institutionField]))]
        .filter(inst => inst != null && inst !== '' && inst !== 'Unknown');
      return d3.scaleOrdinal(d3.schemeTableau10).domain(uniqueInstitutions);
    } else if (colorMode === 'shared_institutions') {
      const sharedField = coauthorData.some(d => d.shared_institutions_normalized) 
        ? 'shared_institutions_normalized' 
        : 'shared_institutions';
      
      const uniqueSharedInstitutions = [...new Set(coauthorData.map(d => d[sharedField]))]
        .filter(inst => inst != null && inst !== '' && inst !== 'Unknown');
      return d3.scaleOrdinal(d3.schemeTableau10).domain(uniqueSharedInstitutions);
    }
    
    return null;
  });

  // Filter coauthor data based on age
  let filteredCoauthorData = $derived.by(() => {
    if (!coauthorData || !dashboardState.ageFilter) return coauthorData;
    
    const [minAge, maxAge] = dashboardState.ageFilter;
    return coauthorData.filter(d => {
      const age = +d.author_age || 0;
      return age >= minAge && age <= maxAge;
    });
  });

  // Process coauthor data into positioned points
  let processedCoauthorData = $derived.by(() => {
    if (!filteredCoauthorData || filteredCoauthorData.length === 0) return [];
    return processCoauthorData(filteredCoauthorData, chartWidth, chartHeight, sharedTimeScale);
  });

  // Process paper data into positioned points
  let processedPaperData = $derived.by(() => {
    if (!paperData || paperData.length === 0) return [];
    return processPaperData(paperData, chartWidth, chartHeight, sharedTimeScale);
  });

  // Apply styling and highlighting to coauthor data
  let styledCoauthorData = $derived.by(() => {
    if (!processedCoauthorData.length) return [];
    
    return processedCoauthorData.map(point => {
      // Get the value for coloring
      let colorValue;
      const colorMode = dashboardState.colorMode;
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
        // Use the color scale
        if (coauthorColorScale) {
          if (colorMode === 'acquaintance') {
            const collabCount = +point.all_times_collabo || 0;
            displayColor = coauthorColorScale(collabCount);
          } else {
            displayColor = coauthorColorScale(colorValue);
          }
        } else {
          displayColor = "#888888";
        }
        opacity = 0.9;
        strokeWidth = 0.3;
      }
      
      // Apply highlight filter
      if (dashboardState.highlightedCoauthor) {
        const isHighlightedCoauthor = point.name === dashboardState.highlightedCoauthor;
        opacity *= isHighlightedCoauthor ? 1 : 0.2;
      }
      
      return {
        ...point,
        displayColor,
        opacity,
        strokeWidth
      };
    });
  });

  // Apply styling and highlighting to paper data
  let styledPaperData = $derived.by(() => {
    if (!processedPaperData.length) return [];
    
    return processedPaperData.map(point => {
      let opacity = 1;
      
      // Apply author highlight filter if provided
      if (dashboardState.highlightedAuthor) {
        const isHighlightedAuthor = point.ego_aid === dashboardState.highlightedAuthor;
        opacity *= isHighlightedAuthor ? 1 : 0.2;
      }
      
      return {
        ...point,
        opacity,
        displayColor: point.color,
        strokeWidth: 0.8
      };
    });
  });

  let maxAge = $state(30);
  let isFacet = $state(false);
  let showMed = $state(false);
  let showArea = $state(false);
  
  let filteredAggData = $derived(
    trainingAggData?.filter(d=>dataState.availableColleges.slice(0,4).includes(d.college) && d.author_age < maxAge) || []
  );


</script>

<div class="dashboard">
  <div class="charts-container">
    <div class="charts-grid">
      <div class="chart-panel">
        <h2>Coauthor Collaborations</h2>
        <CoauthorChart 
          displayData={styledCoauthorData}
          rawData={filteredCoauthorData}
          timeScale={sharedTimeScale}
          colorScale={coauthorColorScale}
          width={chartWidth}
          height={chartHeight}
          colorMode={dashboardState.colorMode}
          {trainingData}
        />
      </div>
      <div class="chart-panel">
        <h2>Publications Timeline</h2>
        <PaperChart 
          displayData={styledPaperData}
          {productivityData}
          width={chartWidth}
          height={chartHeight}
          timeScale={sharedTimeScale}
        />
      </div>
      <div>
      </div>
    </div>
    <h3>Aggregated patterns</h3>
    <div class="toggle-controls">
          <RangeFilter 
            bind:value={maxAge}
            label="Max academic age: {maxAge} "
          />
    </div>
    <CollabChart data={filteredAggData} {maxAge}/>
  </div>
</div>



<style>
  .agg-plot-container {
    margin-top:3rem
  }

  .dashboard {
    max-width: 100%;
    margin: 0;
    padding: 20px;
    font-family: var(--sans);
  }

  .charts-container {
    margin-bottom: 30px;
  }

  .charts-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    width: 100%;
  }

  .chart-panel {
    margin-top: -40px;
    background: var(--color-bg);
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    overflow: hidden;
  }

  .chart-panel h2 {
    color: var(--color-text);
    font-size: var(--font-size-xsmall);
    text-align: center;
    width: 100%;
  }

  .toggle-controls {
    display: flex;
    max-width: 200px;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
  }

  .toggle-controls > span {
    margin-top: 1rem;
    margin-bottom: 1rem;
    font-size: 0.75rem;
    color: var(--color-fg);
    margin-right: 0.5rem;
  }

  /* Responsive design */
  @media (max-width: 1200px) {
    .charts-grid {
      grid-template-columns: 1fr;
    }
    
    .dashboard {
      padding: 15px;
    }
  }
</style>