<script>
  import { Plot, AreaY, LineY, HTMLTooltip } from 'svelteplot';

  import PaperChart from './PaperChart.svelte';
  import CoauthorChart from './CoauthorChart.svelte';
  import Toggle from './Toggle.svelte'
  import RangeFilter from './RangeFilter.svelte'
  import { dashboardState, uiState } from '../state.svelte.ts';
  import { innerWidth } from 'svelte/reactivity/window';
  
  let { 
    paperData, 
    coauthorData,
    aggData
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

  const chartHeight = $derived(coauthorData?.length > 600 ? coauthorData?.length < 1500 ? 1200 : 2200 : 800);

  let maxAge = $state(40);
  let isFacet = $state(false);
  let showMed = $state(false);
  let showArea = $state(false); // Add this new toggle state
  
  let filteredAggData = $derived(
    aggData?.filter(d => d.age_std <= maxAge) || []
  );

  $inspect(aggData)
  
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
      <div>
        <h3>Collaboration patterns</h3>
        <div class="toggle-controls">
          <span>Facet by Age Category</span>
          <Toggle bind:isTrue={isFacet}/>
          
          <span>Show median</span>
          <Toggle bind:isTrue={showMed}/>
          
          <span>Show Standard Deviation</span>
          <Toggle bind:isTrue={showArea}/>

          <RangeFilter 
            bind:value={maxAge}
            label="Max academic age: {maxAge} "
          />
        </div>
          <Plot grid frame 
              x={{label: "Academic age →"}}
              y={{label: "↑ Mean # of collaborations"}}
              color={{legend: true, scheme: ["#404788FF", "#20A387FF", "#FDE725FF"]}}
              >
              {#if showMed}
                <LineY data={filteredAggData}  
                  x="age_std" 
                  y="mean_collabs"
                  stroke="age_category" 
                  strokeOpacity=0.4
                  fx={isFacet ? "age_category" : null}/>
                  <LineY data={filteredAggData}  
                    x="age_std" 
                    y="median_collabs"
                    strokeDasharray=5
                    strokeWidth=3
                    stroke="age_category" 
                    fx={isFacet ? "age_category" : null}/>
              {:else}
                  <LineY data={filteredAggData}  
                    x="age_std" 
                    y="mean_collabs"
                    stroke="age_category" 
                    fx={isFacet ? "age_category" : null}/>
              {/if}
              {#if showArea}
                <AreaY 
                  data={filteredAggData} 
                  x="age_std" 
                  y1={(d) => d.mean_collabs - d.std_collabs}  
                  y2={(d) => d.mean_collabs + d.std_collabs} 
                  fillOpacity=0.2 
                  fill="age_category"
                  fx={isFacet ? "age_category" : null}
                />
              {/if}
          </Plot>
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

  .toggle-controls {
    display: flex;
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