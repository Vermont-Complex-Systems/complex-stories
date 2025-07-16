<script>
  import DodgeChart from '$lib/components/helpers/DodgeChart.svelte';
  
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

<div class="coauthor-chart" style="--chart-width: {width}px; --chart-height: {height}px;">
  <div class="rotation-wrapper">
    <div class="chart-container rotated">
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
    </div>
  </div>
</div>

<style>
  .coauthor-chart {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    height: var(--chart-width);
  }

  .rotation-wrapper {
    position: relative;
    overflow: visible;
    width: var(--chart-height);
    height: var(--chart-width);
  }

  .chart-container.rotated {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: rotate(270deg) translate(-40%, -50.7%);
    transform-origin: 0 0;
    border: 2px solid rgb(237, 237, 237);
    width: var(--chart-width);
    height: var(--chart-height);
  }
</style>