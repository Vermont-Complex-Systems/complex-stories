<script>
  import { base } from '$app/paths';
  import Scrolly from '$lib/components/helpers/Scrolly.svelte';
  import MorphingChart from './MorphingChart.svelte';
  import WaffleChart from './Waffle.svelte';
  import Nav from './Nav.svelte';
  import Intro from './Intro.svelte'
  import Embeddings from './Embeddings.svelte'
  import Spinner from '$lib/components/helpers/Spinner.svelte'
  import Md from '$lib/components/helpers/MarkdownRenderer.svelte';

  import { dataState, initializeApp } from '../state.svelte.ts';

  let { story, data } = $props();
    
  // Initialize on component mount
  initializeApp();
  
  const doddsSection = data.zoomingIn;
  
  let isDark = $state(false);
  let width = $state(900);
  let height = 1800;
  let scrollyIndex = $state();
  
</script>

<Nav bind:isDark />

{#if dataState.isInitializing}
  <div class="loading-container">
    <Spinner />
  </div>
{:else}


  <div class="header-container">
  <div class="header-text">
    <h1>Mapping the Research Ecosystem of the University of Vermont</h1>
    <div class="article-meta">
      <p class="author">By <a href="{base}/author/jonathan-st-onge">Jonathan St-Onge</a></p>
      <p class="date">May 16, 2025</p>
    </div>
  </div>
  <div class="logo-container">
    <img src="{base}/UVM_Seal_Gr.png" alt="Home" class="logo" />
  </div>
</div>

  <Intro data={dataState.trainingAggData}/>
  
  <section id="story" class="story">  

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

  <Embeddings embeddingData={dataState.EmbeddingsData} coauthorData={dataState.DoddsCoauthorData}/>

  <section id="conclusion" class="story">
    <h2>Conclusion</h2>

    <p>Poetic conclusion about what we accomplished. Also what about other faculties at UVM? Visit <a href="{base}/open-academic-analytics">our dashboard</a> for more.</p>
  </section>
{/if}

<style>
    /* Header Layout */
  .header-container {
    display: flex;
    align-items: flex-start;
    gap: 20px;
    max-width: 1200px;
    margin: 4rem auto 0 auto;
    padding: 0 2rem;
  }

  .header-text {
    flex: 1;
    max-width: 600px;
  }

  .header-container h1 {
    margin: 0 0 1rem 0 !important;
    font-size: var(--font-size-xlarge);
    font-family: var(--serif);
  }

  .logo {
    height: 300px;
    width: auto;
    object-fit: contain;
    max-width: 400px;
    transform: translateY(-30px);
  }

  .article-meta {
    margin: 0;
    font-family: var(--sans);
  }

  .article-meta .author {
    font-size: var(--font-size-medium);
    color: var(--color-secondary-gray);
    margin: 0 0 0.25rem 0;
    font-weight: 500;
  }

  .article-meta .date {
    font-size: var(--font-size-small);
    color: var(--color-tertiary-gray);
    margin: 0;
    font-weight: 400;
  }

  /* Loading */
  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    gap: 1rem;
  }

  /* Story sections */
  :global(#story) {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
  }

  :global(#story h2) {
    font-size: 1.8rem;
    margin: 2rem 0 1rem 0;
    font-family: var(--serif);
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
    grid-template-columns: 3fr 7fr;
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
    width: 400px;
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
    transform: translateX(-4rem);
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

  /* Mobile responsive */
  @media (max-width: 1200px) {
    .header-container {
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 1rem;
    }

    .header-text {
      max-width: none;
    }

    .logo {
      transform: none;
      height: 200px;
    }

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