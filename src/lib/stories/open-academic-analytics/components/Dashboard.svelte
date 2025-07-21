<script>
  import * as d3 from 'd3';

  import CoauthorChart from './CoauthorChart.svelte';
  import PaperChart from './PaperChart.svelte';
  import Toggle from './helpers/Toggle.svelte'
  import RangeFilter from './helpers/RangeFilter.svelte'
  import CollabChart from './Collaboration.Agg.svelte'
  import { dashboardState, dataState, uiState, unique } from '../state.svelte.ts';
  import { innerWidth } from 'svelte/reactivity/window';
  import { calculateChartWidth, calculateChartHeight, spacing } from '../utils/layout.js';

  import {  getCombinedDateRange } from '../utils/combinedChartUtils.js';
  
  // Calculate available width for charts considering sidebar and layout
  let chartWidth = $derived(
    calculateChartWidth(innerWidth.current, uiState.sidebarCollapsed)
  )

  const chartHeight = $derived(
    calculateChartHeight(dataState.coauthorData?.length)
  );


  // Create shared time scale for both charts
  let sharedTimeScale = $derived.by(() => {
    const paperData = dataState.paperData;
    const coauthorData = dataState.coauthorData;
    
    if (!paperData && !coauthorData) return d3.scaleTime();
    
    const dateRange = getCombinedDateRange(paperData, coauthorData);
    return d3.scaleTime()
      .domain(dateRange)
      .range([50, chartHeight - 50]);
  });

  
  let maxAge = $state(30);
  
  let filteredAggData = $derived(
    dataState.trainingAggData?.filter(d => 
      unique.colleges.slice(0,4).includes(d.college) &&  
      d.author_age < maxAge
    ) || []
  );


</script>

<div class="dashboard">
  <div class="charts-container">
    <div class="charts-grid">
      <div class="chart-panel">
        <h2>Coauthor Collaborations</h2>
        <CoauthorChart 
          timeScale={sharedTimeScale}
          width={chartWidth}
          height={chartHeight}
        />
    </div>
  <div class="chart-panel">
  <h2>Publications Timeline</h2>
        <PaperChart 
          timeScale={sharedTimeScale}
          width={chartWidth}
          height={chartHeight}
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