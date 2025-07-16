<script>
  import DodgeChart from '$lib/components/helpers/DodgeChart.svelte';

  let { displayData = [], width, height, timeScale } = $props();

  // Paper-specific tooltip formatter
  function formatPaperTooltip(point) {
    const citationInfo = point.citation_percentile !== undefined 
      ? `Citations: ${point.cited_by_count} (${Math.round(point.citation_percentile)}th percentile)`
      : `Citations: ${point.cited_by_count}`;
    
    const impactInfo = point.citation_category 
      ? `\nImpact: ${point.citation_category.replace('_', ' ')}`
      : '';
    
    return `Title: ${point.title}\nYear: ${point.year}\n${citationInfo}${impactInfo}\nCoauthors: ${point.authors}\nType: ${point.work_type}\nDOI: ${point.doi}`;
  }
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