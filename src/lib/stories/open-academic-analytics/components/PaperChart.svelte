<script>
  import * as d3 from 'd3';
  import DodgeChart from '$lib/components/helpers/DodgeChart.svelte';
  import { processPaperData } from './paperUtils.js';
  import { data } from './state.svelte.ts';
  
  let { width, height, timeScale } = $props();
  let paperData = $derived(data.paper);
  
  // Create the radius scale based on the selected field
  let radiusScale = $derived.by(() => {
    if (!paperData || paperData.length === 0) return null;
    
    const values = paperData.map(d => +d['cited_by_count'] || 0);
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
    if (!paperData || paperData.length === 0) return [];
    return processPaperData(paperData, width, height, timeScale, radiusScale);
  });
  
  // Paper-specific tooltip formatter
  function formatPaperTooltip(point) {
    return `${point.ego_aid}\nTitle: ${point.title}\nYear: ${point.year}\nCoauthors: ${point.authors} (${point.nb_coauthors} coauthors)\nType: ${point.work_type}\nDOI: ${point.doi}`;
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