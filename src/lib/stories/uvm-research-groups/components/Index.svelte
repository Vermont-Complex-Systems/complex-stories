<!-- src/routes/+page.svelte -->
<script>
  import Scrolly from '$lib/components/helpers/Scrolly.svelte';
  import CoauthorBubbleChart from './BubbleChart.svelte';
  import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
  import dodds from "../data/dodds_coauthors.csv";
  import { innerWidth } from 'svelte/reactivity/window';
  
  let { story, data } = $props();
  
  const doddsSection = data.zoomingIn;
  
  let width = $state(700);
  let height = 2000;
  let scrollyIndex = $state();
</script>

<svelte:head>
  <title>Coauthor Collaboration Timeline</title>
</svelte:head>

<section>
  <h1>Coauthor Collaboration Analysis</h1>
  
  <div class="scrolly-container">
    <!-- Fixed chart on the right -->
    <div class="chart-container">
      <CoauthorBubbleChart {scrollyIndex} data={dodds} {width} {height} />
    </div>

    <!-- Scrolling text on the left -->
    <div class="text-container">
      <Scrolly bind:value={scrollyIndex}>
        {#each doddsSection as text, i}
          {@const active = scrollyIndex === i}
          <div class="step" class:active>
            {#if text.type === 'markdown'}
              <p> 
                <Md text={text.value}/>
              </p>
            {:else }
              <p>{@html text.value}</p>
            {/if}
          </div>
        {/each}
      </Scrolly>
    </div>
  </div>
</section>

<style>
  section {
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
  }

  h1 {
    text-align: center;
    color: #333;
    margin-bottom: 2rem;
  }

  .scrolly-container {
    display: flex;
    gap: 2rem;
    min-height: 100vh;
  }

  .text-container {
    flex: 1;
    max-width: 400px;
  }

  .chart-container {
    flex: 1;
    position: sticky;
    top: 2rem;
    height: fit-content;
  }

  .step {
    min-height: 60vh;
    display: flex;
    align-items: center;
    opacity: 0.3;
    transition: opacity 0.5s ease;
    margin-bottom: 2rem;
  }

  .step.active {
    opacity: 1;
  }

  .step p {
    font-size: 1.1rem;
    line-height: 1.6;
    color: #333;
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }

  /* Mobile adjustments */
  @media (max-width: 768px) {
    .scrolly-container {
      flex-direction: column;
    }
    
    .chart-container {
      position: relative;
      order: -1;
    }
    
    .text-container {
      max-width: none;
    }
    
    .step {
      min-height: 40vh;
    }
  }
</style>