<script lang="ts">
  // Example tooltip data (replace with your actual data)
  const tooltipData = [
    "Point 0: Origin",
    "Point 1: Diagonal",
    "Point 2: Offset",
    "Point 3: Negative",
    "Point 4: Up",
    "Point 5: Right",
    "Point 6: Top",
    "Point 7: Left"
  ];

  let hoveredIndex: number | null = null;
  import { Plot, Dot } from 'svelteplot';
  import { Tween } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';

  const { value } = $props();

  // New: baseData as array of 2D arrays [[x, y], ...]
  const baseData: [number, number][] = [
    [0, 0],
    [1, 1],
    [2, 0.5],
    [-1, -1],
    [-0.5, 1.5],
    [1.5, -0.5],
    [0.5, 2],
    [-1.5, 0.5]
  ];

  // Tweened transform parameters
  const offsetX = new Tween(0, { duration: 800, easing: cubicOut });
  const offsetY = new Tween(0, { duration: 800, easing: cubicOut });
  const scaleX = new Tween(1, { duration: 600, easing: cubicOut });
  const scaleY = new Tween(1, { duration: 600, easing: cubicOut });

  // Transform the data based on tweened values
  let plotData = $derived(
    baseData.map(([x0, y0], i) => ({
      id: i + 1,
      x: x0 * scaleX.current + offsetX.current,
      y: y0 * scaleY.current + offsetY.current
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

// update plot when new 
</script>

<div class="viz-content">
  <div class="plot-container">
    <Plot grid maxWidth="500" height="400" 
          x={{ domain: [-4, 4] }} 
          y={{ domain: [-2, 4] }}>
      {#each plotData as d, i}
        <circle
          cx={d.x}
          cy={d.y}
          r="6"
          fill="#667eea"
          opacity="0.8"
          on:mouseenter={() => hoveredIndex = i}
          on:mouseleave={() => hoveredIndex = null}
        />
      {/each}
    </Plot>
    {#if hoveredIndex !== null}
      <div class="tooltip" style="position: absolute; left: 20px; top: 20px; pointer-events: none; background: #fff; border: 1px solid #ccc; padding: 0.5em; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        {tooltipData[hoveredIndex]}
      </div>
    {/if}
  </div>

</div>
