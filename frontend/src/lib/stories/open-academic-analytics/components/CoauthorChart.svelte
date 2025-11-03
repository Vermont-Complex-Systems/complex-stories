<script>
  import * as d3 from 'd3';
  import DodgeChart2 from '$lib/components/helpers/DodgeChart2.svelte';
  import Legend from './CoauthorChart.Legend.svelte';
  import { Info, X } from '@lucide/svelte';
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

  // Create consistent institution lists for both color scale and legend
  let institutionData = $derived.by(() => {
    if (!coauthorData?.length) return null;

    const colorMode = dashboardState.coauthorNodeColor;

    if (colorMode === 'institutions') {
      // Count occurrences of each institution
      const institutionCounts = {};
      coauthorData.forEach(d => {
        const inst = d.coauthor_institution;
        if (inst != null && inst !== '' && inst !== 'Unknown') {
          institutionCounts[inst] = (institutionCounts[inst] || 0) + 1;
        }
      });

      // Sort institutions by count (descending) for better color distribution
      const institutionsByCount = Object.entries(institutionCounts)
        .sort(([,a], [,b]) => b - a) // Sort by count descending
        .map(([inst]) => inst);

      // Use frequency-based ordering for both color scale and display
      const allInstitutions = institutionsByCount;
      const topInstitutions = institutionsByCount.slice(0, 10); // Use all 10 colors from Tableau10

      return {
        all: allInstitutions,
        display: topInstitutions
      };
    } else if (colorMode === 'shared_institutions') {
      const sharedField = coauthorData.some(d => d.shared_institutions_normalized)
        ? 'shared_institutions_normalized'
        : 'shared_institutions';

      // Count occurrences of each shared institution
      const institutionCounts = {};
      coauthorData.forEach(d => {
        const inst = d[sharedField];
        if (inst != null && inst !== '' && inst !== 'Unknown') {
          institutionCounts[inst] = (institutionCounts[inst] || 0) + 1;
        }
      });

      // Sort institutions by count (descending) for better color distribution
      const institutionsByCount = Object.entries(institutionCounts)
        .sort(([,a], [,b]) => b - a) // Sort by count descending
        .map(([inst]) => inst);

      // Use frequency-based ordering for both color scale and display
      const allInstitutions = institutionsByCount;
      const topInstitutions = institutionsByCount.slice(0, 10); // Use all 10 colors from Tableau10

      return {
        all: allInstitutions,
        display: topInstitutions
      };
    }

    return null;
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
      return institutionData ? createInstitutionColorScale(institutionData.all) : null;
    } else if (colorMode === 'shared_institutions') {
      return institutionData ? createSharedInstitutionColorScale(institutionData.all) : null;
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
      if (!institutionData) return [];

      // Calculate counts for display
      const institutionCounts = {};
      coauthorData.forEach(d => {
        const inst = d.coauthor_institution;
        if (inst != null && inst !== '' && inst !== 'Unknown') {
          institutionCounts[inst] = (institutionCounts[inst] || 0) + 1;
        }
      });

      return institutionData.display.map(inst => ({
        color: colorScale(inst),
        label: `${inst} (${institutionCounts[inst]})`
      }));
    } else if (colorMode === 'shared_institutions') {
      if (!institutionData) return [];

      const sharedField = coauthorData.some(d => d.shared_institutions_normalized)
        ? 'shared_institutions_normalized'
        : 'shared_institutions';

      // Calculate counts for display
      const institutionCounts = {};
      coauthorData.forEach(d => {
        const inst = d[sharedField];
        if (inst != null && inst !== '' && inst !== 'Unknown') {
          institutionCounts[inst] = (institutionCounts[inst] || 0) + 1;
        }
      });

      return institutionData.display.map(inst => ({
        color: colorScale(inst),
        label: `${inst} (${institutionCounts[inst]})`
      }));
    }
    
    return [{ color: '#dcdcdcff', label: 'Coauthors' }];
  });
  // Determine shared institutions field once
  let sharedField = $derived.by(() => {
    if (!coauthorData?.length) return 'shared_institutions';
    return coauthorData.some(item => item.shared_institutions_normalized)
      ? 'shared_institutions_normalized'
      : 'shared_institutions';
  });

  // Dynamic color function based on current color mode
  const getCoauthorColor = $derived.by(() => {
    const colorMode = dashboardState.coauthorNodeColor;
    const field = sharedField;

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
          // Use the actual field name from the backend
          colorValue = d.coauthor_institution;
          break;

        case 'shared_institutions':
          colorValue = d[field];
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
  let showMobileLegend = $state(false);

  function formatTooltip(point) {
    const d = point.data;
    const institutionName = d.coauthor_institution || 'Unknown';
    const sharedInstitutionName = d.shared_institutions || 'None';
    return `Coauthor: ${d.coauthor_display_name || d.ego_display_name}\nYear: ${d.publication_year}\nAge difference: ${d.age_diff} years\nTotal collaborations: ${d.all_times_collabo}\nInstitution: ${institutionName}`;
  }

  function handleCoauthorClick(event, point) {
    dashboardState.clickedCoauthor = point.data.coauthor_display_name;
  }

  function handleChartClick(event) {
    dashboardState.clickedCoauthor = null;
  }

  function toggleMobileLegend() {
    showMobileLegend = !showMobileLegend;
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

    <!-- Mobile legend button and overlay -->
    <div class="mobile-legend-container">
      <button class="mobile-legend-button" onclick={toggleMobileLegend}>
        {#if showMobileLegend}
          <X size={16} />
        {:else}
          <Info size={16} />
        {/if}
        <span>Legend</span>
      </button>
      {#if showMobileLegend}
        <div class="mobile-legend-overlay">
          <Legend
            {legendItems}
            visible={hasData}
          />
        </div>
      {/if}
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
    max-width: 150px;
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
      min-width: 120px;
      max-width: 150px;
    }
  }

  /* Mobile legend components - hidden by default */
  .mobile-legend-container {
    display: none;
  }

  @media (max-width: 480px) {

    .coauthor-chart {
      overflow: hidden;
    }
    .right-overlay-container {
      display: none;
    }

    .mobile-legend-container {
      display: block;
      position: absolute;
      top: 0.5rem;
      right: 1rem;
      z-index: 20;
    }

    .mobile-legend-button {
      background: var(--step-bg);
      border: 1px solid var(--color-border);
      border-radius: 6px;
      padding: 8px 12px;
      font-size: 12px;
      cursor: pointer;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      color: var(--color-text);
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .mobile-legend-button:hover {
      background: var(--color-border);
    }

    .mobile-legend-overlay {
      position: absolute;
      top: 100%;
      right: 0;
      margin-top: 8px;
      z-index: 30;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      border-radius: 8px;
      overflow: hidden;
    }
  }
</style>