<script>
  import * as d3 from 'd3';
  import DodgeChart from '$lib/components/helpers/DodgeChart.svelte';
  import ChangePointChart from './ChangePointChart.svelte';
  import Legend from './Legend.svelte';
  import { dashboardState, dataState } from '../state.svelte';
  import { processCoauthorData } from '../utils/coauthorUtils.js';
  
  // ✅ Import centralized color scales
  import { 
    ageColorScale, 
    acquaintanceColorScale, 
    createInstitutionColorScale,
    createSharedInstitutionColorScale 
  } from '../utils/colorScales.js';

  let { width, height, timeScale } = $props();
  
  let coauthorData = $derived(dataState.coauthorData);
  let trainingData = $derived(dataState.trainingData);

  // Create radius scale based on collaboration counts
  let radiusScale = $derived.by(() => {
    if (!coauthorData || coauthorData.length === 0) return null;
    
    const collaborationCounts = coauthorData.map(d => +d.all_times_collabo || 1);
    const [minCollabs, maxCollabs] = d3.extent(collaborationCounts);
    
    if (minCollabs === maxCollabs) {
      return () => 5;
    }
    
    const scale = d3.scaleSqrt()
      .domain([minCollabs, maxCollabs])
      .range([2.5, 12])
      .clamp(true);
    
    return (d) => scale(+d.all_times_collabo || 1);
  });

  // ✅ Fixed: Use correct property name
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
    return processCoauthorData(filteredCoauthorData, width, height, timeScale, radiusScale);
  });

  let colorScale = $derived.by(() => {
    if (!coauthorData || coauthorData.length === 0) return null;
    
    if (dashboardState.coauthorNodeColor === 'age_diff') {
      return ageColorScale;
    } else if (dashboardState.coauthorNodeColor === 'acquaintance') {
      return acquaintanceColorScale;
    } else if (dashboardState.coauthorNodeColor === 'institutions') {
      const institutionField = coauthorData.some(d => d.institution_normalized) 
        ? 'institution_normalized' 
        : 'institution';
      
      const uniqueInstitutions = [...new Set(coauthorData.map(d => d[institutionField]))]
        .filter(inst => inst != null && inst !== '' && inst !== 'Unknown');
      
      return createInstitutionColorScale(uniqueInstitutions);
    } else if (dashboardState.coauthorNodeColor === 'shared_institutions') {
      const sharedField = coauthorData.some(d => d.shared_institutions_normalized) 
        ? 'shared_institutions_normalized' 
        : 'shared_institutions';
      
      const uniqueSharedInstitutions = [...new Set(coauthorData.map(d => d[sharedField]))]
        .filter(inst => inst != null && inst !== '' && inst !== 'Unknown');
      
      return createSharedInstitutionColorScale(uniqueSharedInstitutions);
    }
    
    return null;
  });

  // Coauthor-specific tooltip formatter
  function formatCoauthorTooltip(point) {
    const institutionName = point.shared_institutions_normalized || point.shared_institutions || 'Unknown';
    return `Coauthor: ${point.name}\nYear: ${point.year}\nAge difference: ${point.age_diff} years\nTotal collaborations: ${point.all_times_collabo}\nShared Institution: ${institutionName}`;
  }

  // Coauthor-specific click handlers
  function handleCoauthorClick(event, point) {
    dashboardState.clickedCoauthor = point.name;
  }

  function handleChartClick(event) {
    dashboardState.clickedCoauthor = null;
  }

  // Create legend items based on current color mode and scale
  let legendItems = $derived.by(() => {
    if (!colorScale) return [{ color: '#888888', label: 'Coauthors' }];
    
    const colorMode = dashboardState.coauthorNodeColor;
    
    if (colorMode === 'age_diff') {
      return [
        { color: colorScale('older'), label: 'Older coauthor (+7 years)' },
        { color: colorScale('same'), label: 'Similar age (±7 years)' },
        { color: colorScale('younger'), label: 'Younger coauthor (-7 years)' }
      ];
    } else if (colorMode === 'acquaintance') {
      return [
        { color: colorScale(1), label: 'Few collaborations (1)' },
        { color: colorScale(3), label: 'Some collaborations (2-4)' },
        { color: colorScale(5), label: 'Many collaborations (5+)' }
      ];
    } else if (colorMode === 'institutions') {
      const institutionField = coauthorData.some(d => d.institution_normalized) 
        ? 'institution_normalized' 
        : 'institution';
      
      const uniqueInstitutions = [...new Set(coauthorData.map(d => d[institutionField]))]
        .filter(inst => inst != null && inst !== '' && inst !== 'Unknown')
        .slice(0, 8);
      
      return uniqueInstitutions.map(inst => ({
        color: colorScale(inst),
        label: inst
      }));
    } else if (colorMode === 'shared_institutions') {
      const sharedField = coauthorData.some(d => d.shared_institutions_normalized) 
        ? 'shared_institutions_normalized' 
        : 'shared_institutions';
      
      const uniqueSharedInstitutions = [...new Set(coauthorData.map(d => d[sharedField]))]
        .filter(inst => inst != null && inst !== '' && inst !== 'Unknown')
        .slice(0, 8);
      
      return uniqueSharedInstitutions.map(inst => ({
        color: colorScale(inst),
        label: inst
      }));
    }
    
    return [{ color: '#888888', label: 'Coauthors' }];
  });

  // Apply styling and highlighting to coauthor data
  let displayData = $derived.by(() => {
    if (!processedCoauthorData.length) return [];
    
    return processedCoauthorData.map(point => {
      // Get the value for coloring
      let colorValue;
      const colorMode = dashboardState.coauthorNodeColor;
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
        if (colorScale) {
          if (colorMode === 'acquaintance') {
            const collabCount = +point.all_times_collabo || 0;
            displayColor = colorScale(collabCount);
          } else {
            displayColor = colorScale(colorValue);
          }
        } else {
          displayColor = "#888888";
        }
        opacity = 0.9;
        strokeWidth = 0.3;
      }
      
      // ✅ Fixed: Use correct property name
      if (dashboardState.clickedCoauthor) {
        const isHighlightedCoauthor = point.name === dashboardState.clickedCoauthor;
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
      onPointClick={handleCoauthorClick}
      onChartClick={handleChartClick}
    />

    <!-- Right side overlay container for Legend and ChangePoint Chart -->
    <div class="right-overlay-container">
      <!-- Legend positioned on the right -->
      <div class="legend-container">
        <Legend 
          {legendItems}
          visible={hasData}
        />
      </div>
      
      <!-- ChangePoint Chart positioned underneath legend -->
      {#if hasTrainingData && dashboardState.coauthorNodeColor === 'age_diff'}
        <div class="changepoint-container">
          <ChangePointChart 
            data={trainingData} 
            visible={hasTrainingData && dashboardState.coauthorNodeColor === 'age_diff'} 
          />
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