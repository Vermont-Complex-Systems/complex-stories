<script>
  import Scrolly from '$lib/components/helpers/Scrolly.svelte';
  import MorphingChart from './MorphingChart.svelte';
  import WaffleChart from './Waffle.svelte';
  import Nav from './Nav.svelte';
  import Intro from './Intro.svelte'
  import Spinner from '$lib/components/helpers/Spinner.svelte'
  import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
  import embeddings from '../data/umap_results.csv'
  
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
  
  $inspect(dataState.trainingAggData)
</script>

<Nav bind:isDark />

{#if dataState.isInitializing}
  <div class="loading-container">
    <Spinner />
  </div>
{:else}

<section id="story" class="story">  
  <Intro data={dataState.trainingAggData}/>

  <h2>Zooming in</h2>
  <p>To better understand faculty career trajectory, we explore a simple timeline plot showing how scientific productivity coevolve social collaborations. As a faculty advance in his career, call him Peter, it is expected that his patterns of collaborations will change. We are interested in a few relevant features to determine from the data when Peter started his research groups.</p>
    
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
        <MorphingChart 
          {scrollyIndex} 
          DoddsCoauthorData={dataState.DoddsCoauthorData} 
          DoddsPaperData={dataState.DoddsPaperData} 
          {width} {height} />
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
    margin: 0;
    padding: 0;
    gap: 1rem;
    box-sizing: border-box;
  }
  .waffle-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin: 0 0;
  }

  .college-section {
  grid-column: 1 / -1; /* Span full width */
  margin-bottom: 2rem;
}

.college-header {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #ddd;
  color: #333;
}

.department-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
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