<script>
  import * as d3 from 'd3';
  import DodgeChart2 from '$lib/components/helpers/DodgeChart2.svelte';
  import Legend from './CoauthorChart.Legend.svelte';
  import { dashboardState, data } from '$stories/open-academic-analytics/state.svelte';
  import { 
    ageColorScale, 
    acquaintanceColorScale, 
    createInstitutionColorScale,
    createSharedInstitutionColorScale 
  } from '../utils/colorScales.js';
  
  let { width, height, timeScale } = $props();
  
  let coauthorData = $derived(data.coauthor);
  
  let radiusScale = $derived.by(() => {
    if (!coauthorData?.length) return null;
    
    const collaborationCounts = coauthorData.map(d => +d.all_times_collabo || 1);
    const [minCollabs, maxCollabs] = d3.extent(collaborationCounts);
    
    if (minCollabs === maxCollabs) return () => 5;
    
    const scale = d3.scaleSqrt()
      .domain([minCollabs, maxCollabs])
      .range([2, 14])
      .clamp(true);
    
    return (d) => scale(+d.all_times_collabo || 1);
  });

  // Create color scale for legend generation
  let colorScale = $derived.by(() => {
    if (!coauthorData?.length) return null;
    
    const colorMode = dashboardState.coauthorNodeColor;
    
    if (colorMode === 'age_diff' || colorMode === 'age_category') {
      return ageColorScale;
    } else if (colorMode === 'acquaintance') {
      return acquaintanceColorScale;
    } else if (colorMode === 'institutions') {
      const institutionField = coauthorData.some(d => d.institution_normalized) 
        ? 'institution_normalized' 
        : 'institution';
      
      const uniqueInstitutions = [...new Set(coauthorData.map(d => d[institutionField]))]
        .filter(inst => inst != null && inst !== '' && inst !== 'Unknown');
      
      return createInstitutionColorScale(uniqueInstitutions);
    } else if (colorMode === 'shared_institutions') {
      const sharedField = coauthorData.some(d => d.shared_institutions_normalized) 
        ? 'shared_institutions_normalized' 
        : 'shared_institutions';
      
      const uniqueSharedInstitutions = [...new Set(coauthorData.map(d => d[sharedField]))]
        .filter(inst => inst != null && inst !== '' && inst !== 'Unknown');
      
      return createSharedInstitutionColorScale(uniqueSharedInstitutions);
    }
    
    return null;
  });

  // Create legend items based on current color mode and scale
  let legendItems = $derived.by(() => {
    if (!colorScale) return [{ color: '#888888', label: 'Coauthors' }];
    
    const colorMode = dashboardState.coauthorNodeColor;
    
    if (colorMode === 'age_diff' || colorMode === 'age_category') {
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
        .slice(0, 8); // Limit to 8 items for display
      
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
        .slice(0, 8); // Limit to 8 items for display
      
      return uniqueSharedInstitutions.map(inst => ({
        color: colorScale(inst),
        label: inst
      }));
    }
    
    return [{ color: '#dcdcdcff', label: 'Coauthors' }];
  });
  // Dynamic color function based on current color mode  
  const getCoauthorColor = $derived.by(() => {
    const colorMode = dashboardState.coauthorNodeColor;
    
    return (d) => {
      let colorValue;
      
      switch (colorMode) {
        case 'age_category':
        case 'age_diff':
          colorValue = d.age_category === 'unknown' ? null : d.age_category;
          break;
          
        case 'acquaintance':
          colorValue = +d.all_times_collabo || 0; // Use the actual collaboration count
          break;
          
        case 'institutions': // Note: plural like in your old code
          // Check which field exists and use it
          const institutionField = coauthorData.some(item => item.institution_normalized) 
            ? 'institution_normalized' 
            : 'institution';
          colorValue = d[institutionField];
          break;
          
        case 'shared_institutions':
          // Check which field exists and use it
          const sharedField = coauthorData.some(item => item.shared_institutions_normalized) 
            ? 'shared_institutions_normalized' 
            : 'shared_institutions';
          colorValue = d[sharedField];
          break;
          
        default:
          colorValue = d.age_category;
      }
      
      // Handle null/unknown values
      if (colorValue == null || colorValue === '' || colorValue === 'Unknown') {
        return "#dcdcdcff";
      }
      
      return colorScale ? colorScale(colorValue) : "#dcdcdcff";
    };
  });

  let hasData = $derived(coauthorData && coauthorData.length > 0);

  function formatTooltip(point) {
    const d = point.data;
    const institutionName = d.shared_institutions_normalized || d.shared_institutions || 'Unknown';
    return `Coauthor: ${d.coauthor_display_name || d.ego_display_name}\nYear: ${d.publication_year}\nAge difference: ${d.age_diff} years\nTotal collaborations: ${d.all_times_collabo}\nShared Institution: ${institutionName}`;
  }

  function handleCoauthorClick(event, point) {
    dashboardState.clickedCoauthor = point.data.coauthor_display_name;
  }

  function handleChartClick(event) {
    dashboardState.clickedCoauthor = null;
  }
</script>

<div class="coauthor-chart">
  <div class="chart-container">
    <!-- Main dodge chart -->
    <DodgeChart2 
      data={coauthorData} 
      yField={'pub_date'}
      colorFunction={getCoauthorColor}
      highlightedItem={dashboardState.clickedCoauthor} 
      highlightField={'coauthor_display_name'}                   
      onPointClick={handleCoauthorClick} 
      onChartClick={handleChartClick}
      {height} 
      {width} 
      {timeScale} 
      {radiusScale}
      {formatTooltip}
    />

    <!-- Right side overlay container for Legend -->
    <div class="right-overlay-container">
      <div class="legend-container">
        <Legend 
          {legendItems}
          visible={hasData}
        />
      </div>
    </div>
  </div>
</div>

<style>
  .coauthor-chart {
    width: 100%;
    overflow: visible;
    z-index: 10;
    position: relative;
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

  /* Legend positioning */
  .legend-container {
    pointer-events: none;
  }

  .legend-container :global(.legend) {
    pointer-events: auto;
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