<script>
  import * as d3 from 'd3';

  import CoauthorChart from './CoauthorChart.svelte';
  import PaperChart from './PaperChart.svelte';
  import { data } from './state.svelte';
  import { innerWidth } from 'svelte/reactivity/window';
  import { calculateChartWidth, calculateChartHeight, spacing } from '../utils/layout.js';

  import {  getCombinedDateRange } from '../utils/combinedChartUtils.js';
  
  // Calculate available width for charts considering sidebar and layout
  let width = $derived(
    calculateChartWidth(innerWidth.current, true)
  )

  const height = $derived(
    calculateChartHeight(data.coauthor?.length)
  );

  // Create shared time scale for both charts
  let timeScale = $derived.by(() => {
        
        if (!data.paper && !data.coauthor) return d3.scaleTime();
        
        const dateRange = getCombinedDateRange(data.paper, data.coauthor, 'pub_date');
        return d3.scaleTime()
            .domain(dateRange)
            .range([50, height - 50]);
      });

</script>

<div class="dashboard">
  <div class="charts-container">
    <div class="charts-grid">
      <div class="chart-panel">
        <h2>Coauthor Collaborations</h2>
        <CoauthorChart  {timeScale} {width} {height}/>
      </div>
      <div class="chart-panel">
        <h2>Publications Timeline</h2>
          <PaperChart {timeScale} {width} {height} />
      </div>
    </div>
  </div>
</div>



<style>

  .dashboard {
    max-width: 100%;
    margin: 0;
    padding: 20px;
    font-family: var(--sans);
  }

  .charts-container {
    margin-bottom: 30px;
    overflow: visible;
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
    overflow: visible;
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