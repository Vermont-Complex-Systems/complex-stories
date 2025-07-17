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

  let chartWidth = 250
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
   <h3>Embeddings (WIP)</h3>
  <p>Instead of using time to position paper, we can also use embeddings to position similar papers closer together in space. To do so, we use the <a href="https://allenai.org/blog/specter2-adapting-scientific-document-embeddings-to-multiple-fields-and-task-formats-c95686c06567">Specter2 model</a>, accesible via Semantic Scholar's API, which has the benefit of taking into account the similarity of paper titles and abstract, but also the relative proximity in citation space. That is, a paper can be similar in terms of content but pushed apart by virtue of being cited by different communities. We use <a href="https://umap-learn.readthedocs.io/en/latest/">UMAP</a> to project down the high dimensional embedding space onto a two-dimensional cartesian plane. We plot a subset of our UVM 2023 faculties (we are still annotating faculty with their database identifiers).</p>
    
  <p>Taking Peter again as our example, what is of interest to us is how his exploration of this embedding space might have been modified by his diverse coauthors, contextualized within UVM broader research ecosystem: </p>


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

  <p>Brushing the bottom chart over the years, it seems that Peter focused on a mixed bag of computational sciences early on (2015-2016), which makes sense. Starting in 2020-2021, he made incursions into health science. From ground truth, we know that this corresponds to different periods for his lab, with the Mass Mutual funding coming in later on.</p>

<p>There are a few issues with this plot, such as reducing the high-dimensionality of papers onto two dimensions. Another issue is that earlier papers have worse embedding coverage, which is too bad (we might fix that later on by running the embedding model ourselves).</p>

<p>All that being said, this plot remains highly informative for getting a glimpse of the UVM ecosystem, and exploring how different periods in collaboration are reflected in how faculty might explore topics.</p>
</section>

<style>
  /* Story-wide settings */
 :global(#embeddings) {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

  :global(#embeddings h1) {
    font-size: var(--font-size-xlarge);
    margin: 2rem 0 3rem 0;
    text-align: left;
    font-family: var(--serif);
  }


section p {
    font-size: 22px;
    max-width: 800px;
    line-height: 1.3;
    margin-top: 2rem; /* Add more space after paragraphs */
    margin-bottom: 2rem; /* Add more space after paragraphs */
  }
</style>

