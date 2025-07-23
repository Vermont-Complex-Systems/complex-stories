<script>
  import * as d3 from 'd3';
  import DodgeChart from '$lib/components/helpers/DodgeChart.svelte';
  // import ChangePointChart from './ChangePointChart.svelte';
  // import Legend from './Legend.svelte';
  import { data } from './state.svelte.ts';
  import { processCoauthorData } from './utils/coauthorUtils.js';
  
  // ✅ Import centralized color scales
  import { 
    ageColorScale, 
    acquaintanceColorScale, 
    createInstitutionColorScale,
    createSharedInstitutionColorScale 
  } from './utils/colorScales.js';

  let { width, height, timeScale } = $props();
  
  let coauthorData = $derived(data.coauthor);
  // let trainingData = $derived(data.trainingData);

  let radiusScale = $derived.by(() => {
    if (!coauthorData || coauthorData.length === 0) return null;
    
    const collaborationCounts = coauthorData.map(d => +d.all_times_collabo || 1);
    const [minCollabs, maxCollabs] = d3.extent(collaborationCounts);
    
    if (minCollabs === maxCollabs) {
      return () => 5;
    }
    
    const scale = d3.scaleSqrt()
      .domain([minCollabs, maxCollabs])
      .range([2, 12])
      .clamp(true);
    
    return (d) => scale(+d.all_times_collabo || 1);
  });

  // Process coauthor data into positioned points
  let processedCoauthorData = $derived.by(() => {
    if (!coauthorData || coauthorData.length === 0) return [];
    return processCoauthorData(coauthorData, width, height, timeScale, radiusScale);
  });

  const coauthorNodeColor = 'age_diff';

  
  // Coauthor-specific tooltip formatter
  
  function formatCoauthorTooltip(point) {
    const institutionName = point.shared_institutions_normalized || point.shared_institutions || 'Unknown';
    return `Coauthor: ${point.name}\nYear: ${point.publication_year}\nAge difference: ${point.age_diff} years\nTotal collaborations: ${point.all_times_collabo}\nShared Institution: ${institutionName}`;
  }
  
  let displayData = $derived.by(() => {
    if (!processedCoauthorData.length) return [];
    
    return processedCoauthorData.map(point => {
      // Get the value for coloring
      let colorValue;
      
      colorValue = point.age_category;
      

      // Styling logic
      const isNull = colorValue == null || colorValue === '' || colorValue === 'Unknown';
      let displayColor, opacity, strokeWidth;

      if (isNull) {
        displayColor = "#888888";
        opacity = 0.3;
        strokeWidth = 0.1;
      } else {
        displayColor = ageColorScale(colorValue);
        opacity = 0.9;
        strokeWidth = 0.3;
      }
      
      // ✅ Fixed: Use correct property name
      // if (dashboardState.clickedCoauthor) {
      //   const isHighlightedCoauthor = point.name === dashboardState.clickedCoauthor;
      //   opacity *= isHighlightedCoauthor ? 1 : 0.2;
      // }
      
      return {
        ...point,
        displayColor,
        opacity,
        strokeWidth
      };
    });
  });

  // Check if we have training data and display data
  let hasTrainingData = $derived(trainingData && trainingData.length > 0);
  let hasData = $derived(displayData && displayData.length > 0);

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
    />

    <!-- Right side overlay container for Legend and ChangePoint Chart -->
    <!-- <div class="right-overlay-container">
      <div class="legend-container">
        <Legend 
          {legendItems}
          visible={hasData}
        />
      </div>
      
      {#if hasTrainingData && coauthorNodeColor === 'age_diff'}
        <div class="changepoint-container">
          <ChangePointChart 
            data={trainingData} 
            visible={hasTrainingData && coauthorNodeColor === 'age_diff'} 
          />
        </div>
      {/if}
    </div> -->
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