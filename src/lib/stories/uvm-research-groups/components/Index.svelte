<script>
  import Scrolly from '$lib/components/helpers/Scrolly.svelte';
  import MorphingChart from './MorphingChart.svelte';
  import WaffleChart from './Waffle.svelte';
  import Nav from './Nav.svelte';
  import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
  import coauthorData from "../data/uvm_2023_or_dodds.csv";
  import paperData from "../data/papers_uvm_2023_or_dodds.csv"
  import embeddings from '../data/umap_results.csv'
  import { group } from 'd3-array'
	
  import { Plot, Dot } from 'svelteplot';

  import { dataState, initializeApp } from '../state.svelte.ts';


  let { story, data } = $props();

    
  // Initialize on component mount
  initializeApp();
  
  const doddsSection = data.zoomingIn;
  
  let isDark = $state(false);
  let width = $state(900);
  let height = 1800;
  let scrollyIndex = $state();

  let groupedData = $derived(() => {
    if (!dataState.trainingAggData?.length) return new Map();
    
    // Flatten the data - create multiple entries for people with multiple departments
    const flattenedData = dataState.trainingAggData.flatMap(person => {
      const depts = (person.college || 'Unknown').split(';').map(d => d.trim());
      return depts.map(dept => ({
        ...person,
        college: dept
      }));
    });
    
    return group(flattenedData, d => d.college);
  });

  $inspect(dataState.trainingAggData)

</script>

<Nav bind:isDark />


{#if dataState.isInitializing}
  <div class="loading-container">
    <p>Loading authors...</p>
  </div>
{:else}
<section id="story" class="story">
  <h1>How does scientific productivity coevolve with coauthorships?</h1>
   
  <p>Here's the {dataState.trainingAggData.length} UVM faculty annotated with research group:</p>
    
        <WaffleChart data={ dataState.trainingAggData } groupBy="college"/>

  <p>We can also look by college</p>

  <div class="waffle-grid">
      {#each groupedData() as [collegeName, collegeData]}
         <WaffleChart 
          data={collegeData} 
          title="{collegeName} ({collegeData.length})"
          cellSize={30}
          rows={4}
        />
      {/each}
  </div>

  <p>Interesting. But now, we zoom in on a particular faculty to try to understand better what it feels like to have a research group.</p>
  <h2>Zooming in</h2>
  <p>We explore a simple timeline plot showing how scientific productivity and social collaborations changes over time. As a given researcher advance in his career, call him Peter, it is expected that his patterns of collaborations will change. In particular, we are interested in using a few relevant features to determine from the data when Peter started his lab.</p>
    
  <div class="scrolly-container">
      <div class="scrolly-content">
        <div class="spacer"></div>
        <Scrolly bind:value={scrollyIndex}>
          {#each doddsSection as text, i}
            {@const active = scrollyIndex === i}
            <div class="step" class:active>
              {#if text.type === 'markdown'}
                <p><Md text={text.value}/></p>
              {:else}
                <p>{@html text.value}</p>
              {/if}
            </div>
          {/each}
        </Scrolly>
        <div class="spacer"></div>
      </div>
      
      <div class="scrolly-chart">
        <MorphingChart {scrollyIndex} {coauthorData} {paperData} {width} {height} />
      </div>
    </div>
  </section>

<section id="embeddings" class="story">
  <h3>Embeddings</h3>
  <p>Instead of using time to position paper, we can also use embeddings. (WIP)</p>

  <Plot width={1200} height={800} 
    x={{ domain: [-6, 18], grid: true }}
    y={{ domain: [-5, 13], grid: true }}
    caption="UMAP embeddings of Peter's papers and a sample of UVM faculties."> 
      <Dot
          data={embeddings}
          x="umap_1"
          y="umap_2"
          stroke="black"
          fill="white" />
  </Plot>
  <p>(show same plot than before, but just the coauthor side that is rotated on the side. It would be nice to make it brushable, so that we highlight the paper positions for chosen coauthors. Doing so could help visualize changes in coauthors correlate with changes in how ego explore the embedding space. Or not.)</p>
</section>
{/if}

<style>

  .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        gap: 1rem;
    }

  .waffle-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin: 2rem 0;
  }


  /* Story-wide settings */
  :global(#story) {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
  }

  :global(#story h1) {
    font-size: var(--font-size-xlarge);
    margin: 2rem 0 3rem 0;
    text-align: left;
    font-family: var(--serif);
  }

  section p {
      font-size: 22px;
      max-width: 800px;
      line-height: 1.3;
  }

  section p {
      font-size: 22px;
      max-width: 800px;
      line-height: 1.3;
  }

  /* Scrolly layout */
  
  .scrolly-container {
    display: grid;
    margin-top: 3rem; 
    grid-template-columns: 3fr 7fr; /* Text gets 3/10, chart gets 7/10 */
    gap: 2rem;
    min-height: 100vh;
  }

  .scrolly-chart {
    position: sticky;
    top: calc(50vh - 350px);
    height: fit-content;
    overflow: visible; 
  }

  .scrolly-content {
    width: 400px; /* Control the text width */
  }
  

  .spacer {
    height: 75vh;
  }

  .step {
    height: 80vh;
    display: flex;
    align-items: center;
  }

  .step p {
    padding: 1rem;
    background: #f5f5f5;
    color: #ccc;
    border-radius: 5px;
    transform: translateX(-4rem);  /* Magic number to push text on the left */
    box-shadow: 1px 1px 10px rgba(0, 0, 0, 0.2);
    transition: all 500ms ease;
  }

  .step.active p {
    background: white;
    color: black;
  }

  /* Dark mode */
  :global(.dark) .step p {
    background: #2a2a2a;
    color: #888;
  }

  :global(.dark) .step.active p {
    background: #383838;
    color: #fff;
  }

  /* Mobile */
  @media (max-width: 1200px) {
    :global(#story) {
      padding: 0 1rem;
    }

    :global(#story p) {
      font-size: 18px;
      max-width: none;
    }

    .scrolly-container {
      grid-template-columns: 1fr;
      gap: 1rem;
    }

    .scrolly-chart {
      position: sticky;
      top: calc(50vh - 200px);
      width: 100%;
      max-width: 600px;
      margin: 0 auto;
    }

    .step p {
      width: 100%;
      max-width: 600px;
      margin: 0 auto;
      text-align: center;
    }
  }
</style>