<script lang="ts">
  import Scrolly from "$lib/components/helpers/Scrolly.svelte";
  import { Plot, Dot } from 'svelteplot';
  import { Tween } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';

  // story = metadata from CSV (title, author, etc.)
  // data = content from copy.json (steps, text content, etc.)
  let { story, data } = $props();
  let value = $state();
  let currentStep = $derived(data.steps[value]);

  // Create simple, fixed data points
  const baseData = [
    { id: 1, baseX: 0, baseY: 0 },
    { id: 2, baseX: 1, baseY: 1 },
    { id: 3, baseX: 2, baseY: 0.5 },
    { id: 4, baseX: -1, baseY: -1 },
    { id: 5, baseX: -0.5, baseY: 1.5 },
    { id: 6, baseX: 1.5, baseY: -0.5 },
    { id: 7, baseX: 0.5, baseY: 2 },
    { id: 8, baseX: -1.5, baseY: 0.5 }
  ];

  // Tweened transform parameters
  const offsetX = new Tween(0, { duration: 800, easing: cubicOut });
  const offsetY = new Tween(0, { duration: 800, easing: cubicOut });
  const scaleX = new Tween(1, { duration: 600, easing: cubicOut });
  const scaleY = new Tween(1, { duration: 600, easing: cubicOut });

// Transform the data based on tweened values
  let plotData = $derived(
    baseData.map(point => ({
      id: point.id,
      x: point.baseX * scaleX.current + offsetX.current,
      y: point.baseY * scaleY.current + offsetY.current
    }))
  );

  // Watch for scroll changes
  $effect(() => {
    if (value === undefined) {
      offsetX.target = 0;
      offsetY.target = 0;
      scaleX.target = 1;
      scaleY.target = 1;
      return;
    }

    switch (value) {
      case 0:
        offsetX.target = 0;
        offsetY.target = 0;
        scaleX.target = 1;
        scaleY.target = 1;
        break;
      case 1:
        offsetX.target = 1.8;
        offsetY.target = 0;
        scaleX.target = 1;
        scaleY.target = 1;
        break;
      case 2:
        offsetX.target = 0;
        offsetY.target = 0;
        scaleX.target = 1.8;
        scaleY.target = 1;
        break;
      case 3:
        offsetX.target = 0;
        offsetY.target = 1;
        scaleX.target = -1;
        scaleY.target = 0.5;
        break;
      case 4:
        offsetX.target = 0;
        offsetY.target = 0;
        scaleX.target = 1.5;
        scaleY.target = 1.5;
        break;
      default:
        offsetX.target = 0;
        offsetY.target = 0;
        scaleX.target = 1;
        scaleY.target = 1;
    }
  });
</script>

<section id="scrolly">
  <div class="scrolly-container">
    <!-- Scrolling text on the left -->
    <div class="text-container">
      <Scrolly bind:value>
        {#each data.steps as step, i}
          {@const active = value === i}
          <div class="step" class:active>
            <div class="step-content">
              <div class="step-number">Step {i + 1}</div>
              <h3>{step.data.event || `Step ${i + 1}`}</h3>
              <p class="step-text">{step.text}</p>
              <div class="step-meta">
                <span class="year">{step.data.year}</span>
              </div>
            </div>
          </div>
        {/each}
      </Scrolly>
    </div>

    <!-- Fixed visualization on the right -->
    <div class="viz-container">
      <div class="viz-content">
        <h2>Data Transform: <span>{currentStep?.data.year || "Start"}</span></h2>
        
        <div class="plot-container">
          <Plot grid maxWidth={500} height={400} 
                x={{ domain: [-4, 4] }} 
                y={{ domain: [-2, 4] }}>
            <Dot data={plotData} 
                 x="x" 
                 y="y" 
                 fill="#667eea" 
                 opacity={0.8} 
                 r={6} />
          </Plot>
        </div>
        
        <div class="stats">
          <div class="stat">
            <span class="label">Offset X:</span> 
            <span class="value">{offsetX.current.toFixed(1)}</span>
          </div>
          <div class="stat">
            <span class="label">Offset Y:</span> 
            <span class="value">{offsetY.current.toFixed(1)}</span>
          </div>
          <div class="stat">
            <span class="label">Scale X:</span> 
            <span class="value">{scaleX.current.toFixed(1)}</span>
          </div>
          <div class="stat">
            <span class="label">Scale Y:</span> 
            <span class="value">{scaleY.current.toFixed(1)}</span>
          </div>
        </div>

        {#if !currentStep}
          <p class="start-message">Scroll down to see the transformation</p>
        {/if}
      </div>
    </div>
  </div>
</section>

<style>
  #scrolly {
    min-height: 100vh;
  }

  .scrolly-container {
    display: flex;
    min-height: 100vh;
    max-width: 1200px;
    margin: 0 auto;
    gap: 2rem;
  }

  .text-container {
    flex: 1;
    min-width: 0; /* Allow flex shrinking */
  }

  .viz-container {
    flex: 1;
    position: sticky;
    top: 2rem;
    height: 90vh;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .viz-content {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    border: 1px solid #e2e8f0;
    padding: 2rem;
    width: 100%;
    max-width: 600px;
    text-align: center;
  }

  .viz-content h2 {
    margin: 0 0 1.5rem 0;
    font-size: 1.5rem;
    color: #2d3748;
  }

  .viz-content h2 span {
    color: #667eea;
    font-weight: bold;
  }

  .plot-container {
    margin-bottom: 1.5rem;
  }

  .stats {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    flex-wrap: wrap;
    font-family: monospace;
    font-size: 0.8rem;
  }

  .stat {
    background: #f7fafc;
    padding: 0.5rem;
    border-radius: 4px;
    min-width: 80px;
  }

  .label {
    color: #4a5568;
  }

  .value {
    color: #667eea;
    font-weight: bold;
  }

  .start-message {
    color: #718096;
    font-size: 1.1rem;
    margin-top: 1rem;
  }

  /* Text container styles */
  .step {
    min-height: 100vh;
    display: flex;
    align-items: center;
    padding: 2rem;
    opacity: 0.3;
    transition: opacity 0.3s ease;
  }

  .step.active {
    opacity: 1;
  }

  .step-content {
    max-width: 500px;
  }

  .step-number {
    font-family: monospace;
    font-size: 0.9rem;
    color: #667eea;
    font-weight: bold;
    margin-bottom: 0.5rem;
  }

  .step h3 {
    font-size: 1.8rem;
    margin: 0 0 1rem 0;
    color: #2d3748;
    line-height: 1.2;
  }

  .step-text {
    font-size: 1.1rem;
    line-height: 1.6;
    color: #4a5568;
    margin: 0 0 1rem 0;
  }

  .step-meta {
    font-family: monospace;
    font-size: 0.9rem;
    color: #718096;
  }

  .year {
    background: #edf2f7;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-weight: bold;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .scrolly-container {
      flex-direction: column;
    }

    .viz-container {
      position: relative;
      height: auto;
      order: -1; /* Put viz on top on mobile */
    }

    .viz-content {
      margin-bottom: 2rem;
    }

    .step {
      min-height: 60vh;
      padding: 1rem;
    }
  }
</style>