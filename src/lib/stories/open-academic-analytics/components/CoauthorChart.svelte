<script>
  import DodgeChart from './DodgeChart.svelte';
  import ChangePointChart from './ChangePointChart.svelte';
  import Legend from './Legend.svelte';
  import { dashboardState } from '../state.svelte.ts';

  let { 
    displayData = [], 
    rawData = [],
     width, height, timeScale, 
     colorMode = 'age_diff', 
     colorScale = null, 
     trainingData = null
  } = $props();

  // Check if we have training data
  let hasTrainingData = $derived(trainingData && trainingData.length > 0);
  let hasData = $derived(displayData && displayData.length > 0);

  // Coauthor-specific tooltip formatter
  function formatCoauthorTooltip(point) {
    const institutionName = point.shared_institutions_normalized || point.shared_institutions || 'Unknown';
    return `Coauthor: ${point.name}\nYear: ${point.year}\nAge difference: ${point.age_diff} years\nTotal collaborations: ${point.all_times_collabo}\nShared Institution: ${institutionName}`;
  }

  // Coauthor-specific click handlers
  function handleCoauthorClick(event, point) {
    dashboardState.highlightedCoauthor = point.name;
  }

  function handleChartClick(event) {
    dashboardState.highlightedCoauthor = null;
  }
</script>

<div class="coauthor-chart">
  <div class="chart-container">
    <!-- Main dodge chart -->
    <DodgeChart 
      {displayData}
      {width}
      {height}
      {timeScale}
      gridStyle="full"
      formatTooltip={formatCoauthorTooltip}
      onPointClick={handleCoauthorClick}
      onChartClick={handleChartClick}
    />

    <!-- Right side overlay container for Legend and ChangePoint Chart -->
    <div class="right-overlay-container">
      <!-- Legend positioned on the right -->
      <div class="legend-container">
        <Legend 
          {colorMode}
          coauthorData={rawData}
          {colorScale}
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
  </div>
</div>

<style>
  .coauthor-chart {
    width: 100%;
    overflow: hidden;
  }

  .chart-container {
    position: relative;
    width: 100%;
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
    .chart-container {
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