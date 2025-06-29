<script>
  import { processPaperData } from '../utils/combinedChartUtils.js';
  import TimelineChart from './TimelineChart.svelte';

  let { paperData, coauthorData, width, height, highlightedAuthor = null } = $props();

  // Process and style data for display
  let displayData = $derived.by(() => {
    if (!paperData || paperData.length === 0) return [];
    
    return paperData.map(d => {
      let opacity = 1;
      
      // Apply author highlight filter if provided
      if (highlightedAuthor) {
        const isHighlightedAuthor = d.ego_aid === highlightedAuthor;
        opacity *= isHighlightedAuthor ? 1 : 0.2;
      }
      
      return {
        ...d,
        opacity,
        displayColor: "#888888" // Grey for all papers
      };
    });
  });

  function formatTooltip(point) {
    return `Title: ${point.title}\nYear: ${point.pub_year}\nCitations: ${point.cited_by_count}\nCoauthors: ${point.nb_coauthors}\nType: ${point.work_type}`;
  }
</script>

<TimelineChart
  {paperData}
  {coauthorData}
  {width}
  {height}
  processDataFn={processPaperData}
  dataToDisplay={displayData}
  tooltipFormatter={formatTooltip}
>
  {#snippet pointComponent(point, showTooltip, hideTooltip)}
    <circle
      cx={point.x}
      cy={point.y}
      r={point.r}
      fill={point.displayColor}
      stroke="black"
      stroke-width="0.8"
      fill-opacity={point.opacity}
      class="data-point"
      on:mouseenter={(e) => showTooltip(e, point)}
      on:mouseleave={hideTooltip}
    />
  {/snippet}
</TimelineChart>

<style>
  .chart-wrapper {
    --chart-grid-color: var(--color-border);
    --chart-text-color: var(--color-secondary-gray);
    width: 100%;
  }

  .plot-container {
    display: flex;
    justify-content: center;
    position: relative;
    width: 100%;
  }

  .chart-svg {
    display: block;
  }

  /* SVG element styling using design tokens */
  .chart-wrapper :global(.chart-label) {
    font-size: var(--font-size-xsmall);
    font-weight: var(--font-weight-bold);
    font-family: var(--sans);
    fill: var(--chart-text-color);
  }

  .chart-wrapper :global(.year-label) {
    font-size: var(--font-size-xsmall);
    font-family: var(--mono);
    fill: var(--chart-text-color);
  }

  .chart-wrapper :global(.grid-line) {
    stroke: var(--chart-grid-color);
    stroke-width: 1;
  }

  .chart-wrapper :global(.data-point) {
    cursor: pointer;
    transition: fill-opacity 0.3s ease;
  }

  .chart-wrapper :global(.data-point:hover) {
    stroke-width: 2;
  }
</style>