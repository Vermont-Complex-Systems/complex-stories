<script>
  import PaperChart from './PaperChart.svelte';
  import CoauthorChart from './CoauthorChart.svelte';
  import { dashboardState, uiState } from '../state.svelte.ts';
  import { innerWidth } from 'svelte/reactivity/window';

  let { 
    paperData, 
    coauthorData
  } = $props();

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

  const chartHeight = $derived(coauthorData?.length < 600 ? 800 : 1200);
</script>

<div class="dashboard">
  <div class="charts-container">
    <div class="charts-grid">
      <div class="chart-panel">
        <h2>Coauthor Collaborations</h2>
        <CoauthorChart 
          {coauthorData}
          {paperData}
          width={chartWidth}
          height={chartHeight}
          colorMode={dashboardState.colorMode}
          highlightedCoauthor={dashboardState.highlightedCoauthor}
        />
      </div>
      <div class="chart-panel">
        <h2>Publications Timeline</h2>
        <PaperChart 
          {paperData}
          {coauthorData}
          width={chartWidth}
          height={chartHeight}
          highlightedAuthor={dashboardState.highlightedAuthor}
        />
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