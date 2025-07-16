<script>
    import { Plot, Dot } from 'svelteplot';
    import DodgeChart from '$lib/components/helpers/DodgeChart.svelte';
    import EmbeddingDotPlot from './EmbeddingDotPlot.svelte';
    import BrushableCoauthorChart from './BrushableCoauthorChart.svelte';
    import * as d3 from 'd3';
    
    import { dashboardState } from '../state.svelte.ts';
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

  let chartWidth = 250
  const chartHeight = 1105

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
    console.log('Selected coauthors:', brushedPoints);
    console.log('Time range:', timeRange);
  }

</script>

<section id="embeddings" class="story">
  <h3>Embeddings</h3>
  <p>Instead of using time to position paper, we can also use embeddings to position similar papers closer together. To do so, we use Semantic Scholar API which take into account the similarity of paper titles and abstract, but also the relative proximity in citation space. That is, a paper can be similar in terms of content but pushed apart by virtue of being cited by different communities. We use UMAP to project down Semantic scholar high dimensional  embeddings on a two-dimensional cartesian plane, so you should take that visualization with a big grain of salt. We will plot here 30% of all papers by our UVM 2023 faculties (according to the payroll), as well as all the papers of Peter. Hence, we have a map of how Peter and coauthors are situated within UVM topic space. What is of interest to us is how Peter's exploration of content space might have been modified by his diverse coauthors. </p>


  <div class="charts-container">
    <EmbeddingDotPlot 
      {embeddingData}
      width={1200} 
      height={650}
      highlightedIds={highlightedIds}
      timeRange={timeRange}
    />

    <BrushableCoauthorChart 
        displayData={styledCoauthorData}
        width={chartWidth}
        height={chartHeight}
        {timeScale}
        onBrushSelection={handleBrushSelection}
    />    
  </div>

  <p>It is hard to draw any strong conclusion. One issue is that earlier papers have worst embeddings coverage, which is sad. </p>

  {#if selectedCoauthors.length > 0}
    <div class="selected-info">
        <h4>Selected Coauthors:</h4>
        <ul>
        {#each selectedCoauthors as coauthor}
            <li>{coauthor.name} ({coauthor.year})</li>
        {/each}
        </ul>
    </div>
    {/if}
</section>

<style>
    section p {
      font-size: 22px;
      max-width: 800px;
      line-height: 1.3;
  }
</style>

