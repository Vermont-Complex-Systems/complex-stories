<script>
  import * as d3 from 'd3';
  import DodgeChart from '$lib/components/helpers/DodgeChart.svelte';
  import { processPaperData } from './paperUtils.js';
  import { data } from './state.svelte.ts';
  
  let { width, height, timeScale } = $props();
  
  $inspect(data.paper)
  // Create the radius scale based on the selected field
  let radiusScale = $derived.by(() => {
    if (!data.paper || data.paper.length === 0) return null;
    
    const values = data.paper.map(d => +d['cited_by_count'] || 0);
    const [minValue, maxValue] = d3.extent(values);
    
    if (minValue === maxValue) {
      // Return a function that always returns 5
      return () => 5;
    }
    
    const scale = d3.scaleSqrt()
      .domain([minValue, maxValue])
      .range([2, 12])
      .clamp(true);
    
    // Return a function that takes a data object and extracts the field
    return (d) => scale(+d['cited_by_count'] || 0);
  });
  // Process paper data into positioned points
  let processedPaperData = $derived.by(() => {
    if (!data.paper || data.paper.length === 0) return [];
    return processPaperData(data.paper, width, height, timeScale, radiusScale);
  });
  
  // Paper-specific tooltip formatter
  function formatPaperTooltip(point) {
    return `Title: ${point.title}\nYear: ${point.publication_year}\n# coauthors: ${point.nb_coauthors}\nType: ${point.work_type}\nDOI: ${point.doi}`;
  }
  
  // Apply styling and highlighting to paper data
  let displayData = $derived.by(() => {
    if (!processedPaperData.length) return [];
    
    return processedPaperData.map(point => {
      let opacity = 1;
      
      return {
        ...point,
        opacity,
        displayColor: point.color,
        strokeWidth: 0.8
      };
    });
  });

</script>

<div class="paper-chart">
  <DodgeChart 
    {displayData}
    {width}
    {height}
    {timeScale}
    gridStyle="margins"
    formatTooltip={formatPaperTooltip}
  />
</div>

<style>
  .paper-chart {
    width: 100%;
    overflow: hidden;
  }
</style>