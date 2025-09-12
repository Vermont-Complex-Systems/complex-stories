<script>
  import DodgeChart from '$lib/components/helpers/DodgeChart.svelte';
  import EmbeddingDotPlot from './EmbeddingDotPlot.svelte';
  import BrushableCoauthorChart from './BrushableCoauthorChart.svelte';
  import * as d3 from 'd3';
    
  import { dashboardState } from '../state.svelte';
  import { ageColorScale, processCoauthorData, getCombinedDateRange, parseDate } from '../utils/combinedChartUtils2'

  let { embeddingData, coauthorData } = $props();

  // Process coauthor data into positioned points
  let processedCoauthorData = $derived.by(() => {
    if (!filteredCoauthorData || filteredCoauthorData.length === 0) return [];
    return processCoauthorData(filteredCoauthorData, chartWidth, chartHeight, timeScale);
  });

  let timeScale = $derived.by(() => {
    if (!coauthorData) return d3.scaleTime();
    
    const allDates = coauthorData.map(d => parseDate(d.pub_date));
    const [minDate, maxDate] = d3.extent(allDates);
    
    const paddedMinDate = new Date(minDate.getFullYear() - 1, 0, 1);
    const paddedMaxDate = new Date(maxDate.getFullYear() + 1, 11, 31);
    return d3.scaleTime()
      .domain([paddedMinDate,paddedMaxDate ])
      .range([50, chartHeight - 50]); // MARGIN_TOP to height - MARGIN_BOTTOM
  });

  let chartWidth = 280
  const chartHeight = 1045

  let styledCoauthorData = $derived.by(() => {
    if (!processedCoauthorData.length) return [];
    
    return processedCoauthorData.map(point => {
      // Get the value for coloring
      let colorValue;
      const colorMode = dashboardState.colorMode;
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
        if (ageColorScale) {
          if (colorMode === 'acquaintance') {
            const collabCount = +point.all_times_collabo || 0;
            displayColor = ageColorScale(collabCount);
          } else {
            displayColor = ageColorScale(colorValue);
          }
        } else {
          displayColor = "#888888";
        }
        opacity = 0.9;
        strokeWidth = 0.3;
      }
      
      // Apply highlight filter
      if (dashboardState.highlightedCoauthor) {
        const isHighlightedCoauthor = point.name === dashboardState.highlightedCoauthor;
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

  let filteredCoauthorData = coauthorData;

  let selectedCoauthors = $state([]);
  
  // Extract both coauthor IDs and time range
  let highlightedIds = $derived(
    selectedCoauthors.map(coauthor => coauthor.coauth_aid).filter(Boolean)
  );


  let timeRange = $derived.by(() => {
    if (selectedCoauthors.length === 0) return null;
    
    const years = selectedCoauthors.map(c => parseInt(c.year)).filter(Boolean);
    if (years.length === 0) return null;
    
    return [Math.min(...years), Math.max(...years)];
  });
  
  function handleBrushSelection(brushedPoints) {
    selectedCoauthors = brushedPoints;
  }

</script>

<section id="embeddings" class="story">

  <div class="charts-container">
    <EmbeddingDotPlot 
      {embeddingData}
      width={1200} 
      height={650}
      {selectedCoauthors}
      timeRange={timeRange}
    />

    <BrushableCoauthorChart 
        displayData={styledCoauthorData}
        width={chartWidth}
        height={chartHeight}
        {timeScale}
        onBrushSelection={handleBrushSelection}
    />    
    <small>brush to filter</small>
  </div>

</section>

<style>
  section#embeddings .charts-container {
    transform: translate(10%) !important;
  }
</style>

