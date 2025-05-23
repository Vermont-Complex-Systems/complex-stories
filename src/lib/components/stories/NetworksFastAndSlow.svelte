<script lang="ts">
  import Scrolly from "$lib/components/helpers/Scrolly.svelte";
  import { Plot, Dot } from 'svelteplot';
  import { Tween } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';

  let { story } = $props();
  let value = $state();
  let currentStep = $derived(story.steps[value]);

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
        // Original positions
        offsetX.target = 0;
        offsetY.target = 0;
        scaleX.target = 1;
        scaleY.target = 1;
        break;

      case 1:
        // Shift right
        offsetX.target = 1.8;
        offsetY.target = 0;
        scaleX.target = 1;
        scaleY.target = 1;
        break;

      case 2:
        // Stretch horizontally
        offsetX.target = 0;
        offsetY.target = 0;
        scaleX.target = 1.8;
        scaleY.target = 1;
        break;

      case 3:
        // Flip and compress
        offsetX.target = 0;
        offsetY.target = 1;
        scaleX.target = -1;
        scaleY.target = 0.5;
        break;

      case 4:
        // Back to center, enlarged
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
  <div class="timeline-viz">
    <h2>Data Transform: <span>{currentStep?.data.year || "Start"}</span></h2>
    
    {#if currentStep}
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
      
      <div class="timeline-content">
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
        
        <div class="year-display">{currentStep.data.year}</div>
        <div class="event-display">{currentStep.data.event}</div>
        <p class="event-description">{currentStep.text}</p>
      </div>
    {:else}
      <div class="timeline-content">
        <p class="start-message">Scroll down to see the transformation</p>
      </div>
    {/if}
  </div>
  
  <div class="spacer"></div>
  
  <Scrolly bind:value>
    {#each story.steps as step, i}
      <div class="step"></div>
    {/each}
  </Scrolly>
  
  <div class="spacer"></div>
</section>

<style>
  .timeline-viz {
    position: sticky;
    top: 2rem;
    height: 80vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    border: 1px solid #e2e8f0;
    margin: 0 2rem;
    padding: 2rem;
  }

  .plot-container {
    margin-bottom: 1rem;
  }

  .stats {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
    font-family: monospace;
    font-size: 0.8rem;
  }

  .stat {
    background: #f7fafc;
    padding: 0.5rem;
    border-radius: 4px;
  }

  .label {
    color: #4a5568;
  }

  .value {
    color: #667eea;
    font-weight: bold;
  }

  .timeline-viz h2 {
    margin: 0 0 1rem 0;
    font-size: 1.8rem;
    color: #2d3748;
  }

  .timeline-viz h2 span {
    color: #667eea;
    font-weight: bold;
  }

  .timeline-content {
    text-align: center;
    max-width: 400px;
  }

  .year-display {
    font-size: 2rem;
    font-weight: bold;
    color: #667eea;
    margin-bottom: 0.5rem;
  }

  .event-display {
    font-size: 1rem;
    font-weight: 600;
    color: #4a5568;
    margin-bottom: 1rem;
    text-transform: capitalize;
  }

  .event-description {
    font-size: 1rem;
    line-height: 1.5;
    color: #2d3748;
    margin: 0;
  }

  .start-message {
    color: #718096;
    font-size: 1.1rem;
    margin: 0;
  }

  .step {
    height: 80vh;
  }

  .spacer {
    height: 75vh;
  }
</style>