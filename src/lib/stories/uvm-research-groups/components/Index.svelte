<!-- src/routes/+page.svelte -->
<script>
  import Scrolly from '$lib/components/helpers/Scrolly.svelte';
  import MorphingChart from './MorphingChart.svelte';
  import Hero from './Hero.svelte';
  import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
  import coauthorData from "../data/uvm_2023_or_dodds.csv";
  import paperData from "../data/papers_uvm_2023_or_dodds.csv"
  
  let { story, data } = $props();
  
  const doddsSection = data.zoomingIn;
  
  let width = $state(900);
  let height = 1800;
  let scrollyIndex = $state();
</script>

<svelte:head>
  <title>Academic Career Analysis</title>
</svelte:head>

<Hero {coauthorData} {paperData} />

<section>
  <h1>Academic Career Timeline: Collaborators & Publications</h1>
  
  <div class="scrolly-container">
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

    <!-- Combined chart on the right -->
    <div class="chart-container">
      <MorphingChart 
        {scrollyIndex} 
        {coauthorData}
        {paperData} 
        {width} 
        {height} 
      />
    </div>
  </div>
</section>

<style>
  section {
    padding: 2rem;
    max-width: 1600px;
    margin: 0 auto;
  }

  h1 {
    text-align: center;
    color: #333;
    margin-bottom: 2rem;
    font-size: 1.8rem;
  }

  .scrolly-container {
    display: flex;
    gap: 2rem;
    min-height: 100vh;
  }

  .text-container {
    flex: 1;
    max-width: 500px;
    min-width: 400px;
  }

  .chart-container {
    flex: 2;
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

  /* Medium screens */
  @media (max-width: 1200px) {
    .scrolly-container {
      gap: 1.5rem;
    }
    
    .text-container {
      min-width: 350px;
      max-width: 450px;
    }
  }

  /* Small screens - stack vertically */
  @media (max-width: 900px) {
    .scrolly-container {
      flex-direction: column;
    }
    
    .chart-container {
      position: relative;
      order: -1; /* Chart first on mobile */
    }
    
    .text-container {
      max-width: none;
      min-width: auto;
    }
    
    .step {
      min-height: 40vh;
    }

    h1 {
      font-size: 1.4rem;
    }
  }

  /* Very small screens */
  @media (max-width: 600px) {
    section {
      padding: 1rem;
    }
    
    .step p {
      padding: 1rem;
      font-size: 1rem;
    }
  }
</style>