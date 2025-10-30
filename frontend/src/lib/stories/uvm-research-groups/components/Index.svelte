<script>
  import { base } from '$app/paths';
  
  import { innerWidth } from 'svelte/reactivity/window';
  
  import PersonIcon from './PersonIcon.svelte';

  import Scrolly from '$lib/components/helpers/Scrolly.svelte';
  import MorphingChart from './MorphingChart.svelte';
  import WaffleChart from './Waffle.svelte';
  import Nav from './Nav.svelte';
  import Intro from './Intro.svelte'
  import EmbeddingSection from './EmbeddingSection.svelte'
  import Spinner from '$lib/components/helpers/Spinner.svelte'
  import Md from '$lib/components/helpers/MarkdownRenderer.svelte';

  import { loadDoddsPaperData, loadDoddsCoauthorData, loadUvmProfsData, loadEmbeddingsData } from '../data.remote.js';

  let { story, data } = $props();

  const doddsSection = data.zoomingIn;

  let isDark = $state(false);
  let width = $state(innerWidth.current);
  let height = 1800;
  let scrollyIndex = $state();

  // Process UVM profs data similar to the old trainingAggData function
  async function processTrainingAggData() {
    const uvmProfs = await loadUvmProfsData();

    // Explode departments (split host_dept by ';')
    const exploded = [];
    uvmProfs.forEach(prof => {
        if (prof.host_dept) {
            const departments = prof.host_dept.split(';').map(dept => dept.trim());
            departments.forEach(department => {
                exploded.push({
                    ...prof,
                    name: prof.payroll_name,
                    department: department
                });
            });
        } else {
            exploded.push({
                ...prof,
                name: prof.payroll_name,
                department: null
            });
        }
    });

    // Sort by has_research_group, perceived_as_male, oa_uid
    exploded.sort((a, b) => {
        if (a.has_research_group !== b.has_research_group) {
            return (b.has_research_group || 0) - (a.has_research_group || 0);
        }
        if (a.perceived_as_male !== b.perceived_as_male) {
            return (a.perceived_as_male || 0) - (b.perceived_as_male || 0);
        }
        return (a.oa_uid || '').localeCompare(b.oa_uid || '');
    });

    return exploded;
  }

  // Create promise for initial data loading
  const initialDataPromise = Promise.all([
    processTrainingAggData(),
    loadDoddsPaperData(),
    loadDoddsCoauthorData()
  ]);

</script>

<Nav bind:isDark />

{#await initialDataPromise}
  <div class="loading-container">
    <Spinner />
  </div>
{:then [trainingAggData, DoddsPaperData, DoddsCoauthorData]}
  <article id="uvm-groups-story">

    <header class="story-header">
      <div class="header-content">
        <div class="header-text">
          <h1>Mapping the Research Ecosystem of the University of Vermont</h1>
          <div class="article-meta">
            <p class="author">By <a href="{base}/author/jonathan-st-onge">Jonathan St-Onge</a></p>
            <p class="date">May 16, 2025</p>
          </div>
        </div>
        <div class="logo-container">
          <img src="{base}/UVM_Seal_Gr.png" alt="University of Vermont Seal" class="logo light-seal" />
          <img src="{base}/UVM_Seal_Gold.png" alt="University of Vermont Seal" class="logo dark-seal" />
        </div>
      </div>
    </header>

    <section id="introduction">
      <Intro data={trainingAggData}/>
    </section>

    <section id="story" class="story">

      <h2>Zooming in</h2>
      <p>To better understand faculty career trajectories, we build a simple timeline plot showing how scientific productivity coevolves withsocial collaborations. As a faculty member advances in his career—call him Peter—it is expected that his patterns of collaborations willchange. We are interested in a few relevant features to determine from the data when Peter started his research group.</p>

      <div class="scrolly-container">
          <div class="scrolly-chart">
            <MorphingChart
              {scrollyIndex}
              {DoddsCoauthorData}
              {DoddsPaperData}
              {width} {height} />
          </div>

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
        </div>
    </section>

    <!-- Embedding section -->
    <section class="embeddings" id="embeddings">
      <h2>Embeddings</h2>
      <p>Instead of using time to position papers, we can also use embeddings to position similar papers closer together in space. To do so, we use the <a href="https://allenai.org/blog/specter2-adapting-scientific-document-embeddings-to-multiple-fields-and-task-formats-c95686c06567">Specter2 model</a>, accessible via Semantic Scholar's API, which has the benefit of taking into account the similarity of paper titles and abstracts, but also the relative proximity in citation space. That is, a paper can be similar in terms of content but pushed apart by virtue of being cited by different communities. We use <a href="https://umap-learn.readthedocs.io/en/latest/">UMAP</a> to project down the high-dimensional embedding space onto a two-dimensional cartesian plane.</p>

      <p>Taking Peter again as our example, what is of interest to us is how his exploration of this embedding space might have been modified by his diverse coauthors. We situate Peter's papers within the backdrop of papers written by the UVM 2023 faculty (the papers themselves can be older than that):</p>

      <div class="embeddings-container">
        {#await Promise.all([loadEmbeddingsData(), Promise.resolve(DoddsCoauthorData)])}
          <div class="loading-container">
            <Spinner />
          </div>
        {:then [embeddingData, coauthorData]}
          <EmbeddingSection {embeddingData} {coauthorData}/>
        {:catch error}
          <div class="error-container">
            <p>Error loading embeddings: {error.message}</p>
          </div>
        {/await}
      </div>
      <p>On desktop, we show that by brushing over the years we can see that Peter focused on a mixed bag of computational sciences early on (2015-2016), which makes sense. Starting in 2020-2021, he made incursions into health science. From ground truth, we know that this corresponds to different periods for his lab, with the Mass Mutual funding coming in later on.</p>

      <p>There are a few issues with this plot, such as reducing the high-dimensionality of papers onto two dimensions. Another issue is that earlier papers have worse embedding coverage, which is too bad (we might fix that later on by running the embedding model ourselves).</p>

      <p>All that being said, this plot remains highly informative for getting a glimpse of the UVM ecosystem, and exploring how different periods in collaboration are reflected in how faculty might explore topics.</p>
    </section>

    <section id="conclusion">
      <h2>Conclusion</h2>
      <p>We started out by looking at the broader picture of how many groups there were at UVM. Then, we zoomed in on a particular faculty, trying to better understand the coevolution of collaborations and productivity. Our analysis remains limited, as we didn't analyze how the patterns we noticed in the timeline plot generalized to other researchers. This is for a future post.</p>
      <p>In the meantime, you want to carry the same analysis to other faculties at UVM? Visit <a href="{base}/open-academic-analytics">our dashboard</a> for more.</p>
    </section>
  </article>
{:catch error}
  <div class="error-container">
    <p>Error loading data: {error.message}</p>
  </div>
{/await}

<style>
    
  /* Header styling - no layout overrides */
  .story-header {
    margin: 4rem 0 3rem 0;
  }

  .header-content {
    display: flex;
    align-items: flex-start;
    gap: 20px;
  }

  .header-text {
    flex: 1;
    max-width: 600px;
  }

  .logo-container {
    flex-shrink: 0;
  }

  .logo {
    height: 300px;
    width: auto;
    object-fit: contain;
    max-width: 400px;
    transform: translateY(-30px);
  }
  
  /* Dark mode seal switching */
  .light-seal {
    display: block;
  }
  
  .dark-seal {
    display: none;
  }
  
  :global(.dark) .light-seal {
    display: none;
  }
  
  :global(.dark) .dark-seal {
    display: block;
  }

  /* Typography and basic styling */
  
  .story-header h1 {
    margin: 0 0 1rem 0;
    font-size: var(--font-size-xlarge);
    font-family: var(--serif);
    line-height: 1.2;
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

  .article-meta .author a {
    color: inherit;
    text-decoration: none;
  }

  .article-meta .author a:hover {
    text-decoration: underline;
  }

  .article-meta .date {
    font-size: var(--font-size-small);
    color: var(--color-tertiary-gray);
    margin: 0;
    font-weight: 400;
  }

  /* Sections - no layout constraints */
  /* section {
    margin: 3rem 0;
  } */

  
  /* Allow story section (with scrolly) to use full wide width - desktop only */
  @media (min-width: 1200px) {
    section#story .scrolly-container {
      width: var(--width-column-wide) !important;
      max-width: none !important;
      margin-left: 50% !important;
      transform: translateX(-45%) !important;
    }

    section#embeddings .embeddings-container{
      width: var(--width-column-wide) !important;
      max-width: none !important;
      margin-left: 50% !important;
      transform: translateX(-50%) !important;
    }
  }
  
  section#embeddings > p {
      font-size: 22px;
      max-width: 800px !important;
      line-height: 1.3 !important;
      margin-top: 2rem; /* Add more space after paragraphs */
      margin-bottom: 2rem; /* Add more space after paragraphs */
  }

  section h2 {
    font-size: 1.8rem;
    margin: 2rem 0 1rem 0;
    font-family: var(--serif);
    color: var(--color-fg);
  }
  
  section p {
    color: var(--color-fg);
  }

  section p a {
    color: var(--color-primary);
    text-decoration: none;
  }

  section p a:hover {
    text-decoration: underline;
  }

  /* -----------------------------

  Scrolly 

  ----------------------------- */

  /* enforce the left-right layout for text and plot */
  .scrolly-container {
    display: grid;
    grid-template-columns: 4fr 6fr;
    min-height: 100vh;
    gap: 6rem;
    margin-top: 3rem;
  }
  
  /* make the plot sticky */
  .scrolly-chart {
    position: sticky;
    top: calc(50vh - 350px);
    height: fit-content;
    grid-column: 2;
    grid-row: 1;
  }

  /* Fix size of sticky text */
  .scrolly-content {
    grid-column: 1;
    grid-row: 1;
    width: 100%;
  }

  .spacer {
    height: 35vh;
  }

  .step {
    height: 80vh;
    display: flex;
    align-items: center;
  }

  /* esthetics of sticky text */
  .step p {
    padding: 1rem;
    background: #f5f5f5;
    color: #ccc;
    border-radius: 5px;
    box-shadow: 1px 1px 10px rgba(0, 0, 0, 0.2);
    transition: all 500ms ease;
  }

  /* esthetics of sticky text _when active_ */
  .step.active p {
    background: white;
    color: black;
  }

  /* Loading states */
  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 50vh;
    gap: 1rem;
  }

  /* Dark mode support */
  :global(.dark) article {
    color: var(--color-fg);
  }

  :global(.dark) .step p {
    background: #2a2a2a;
    color: #888;
  }

  :global(.dark) .step.active p {
    background: #383838;
    color: #fff;
  }

  :global(.dark) .story-header h1 {
    color: var(--color-fg);
  }

  /* Mobile responsive */
  @media (max-width: 1200px) {
    article {
      padding: 0 1rem;
    }

    .header-content {
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

    section p {
      font-size: 18px;
      max-width: none;
    }

    .scrolly-container {
      display: block;
      margin-top: 2rem;
    }

    .scrolly-chart {
      position: sticky;
      top: calc(50vh - 200px);
      width: 100%;
      max-width: 90vw;
      margin: 1rem auto;
      z-index: -1;
    }

    .scrolly-content {
      max-width: none;
      position: relative;
      z-index: 10;
    }

    .step {
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .step p {
      width: 90vw;
      max-width: 90vw;
      margin: 0 auto;
      text-align: center;
      transform: none;
      background: rgba(255, 255, 255, 0.95) !important;
      border: 1px solid rgba(0, 0, 0, 0.1);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
      position: relative;
      z-index: 100;
    }

    .step.active p {
      background: rgba(255, 255, 255, 0.98) !important;
    }

    /* Hide legend on mobile */
    .scrolly-chart :global(.legend) {
      display: none;
    }
  }

  @media (max-width: 768px) {
    article {
      padding: 0 0.5rem;
    }

    .story-header {
      margin: 2rem 0;
    }

    .story-header h1 {
      font-size: var(--font-size-large);
    }

    section p {
      font-size: 16px;
    }

    .logo {
      height: 150px;
    }

    .step p {
      font-size: 16px;
      padding: 0.75rem;
    }
  }
</style>