<!-- BubbleChart.svelte -->
<script>
  import { processDataPoints } from '../utils/bubbleChartUtils.js';
  import { Tween } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';

  let { scrollyIndex, data, width, height } = $props();

  console.log("Bubble chart loaded with data:", data?.length);
  let basePoints = $state([]);

  // Animation parameters - consolidated into a single config object
  const animationConfig = {
    yearFilterMin: new Tween(1999, { duration: 800, easing: cubicOut }),
    yearFilterMax: new Tween(2023, { duration: 800, easing: cubicOut }),
    opacityMultiplier: new Tween(1, { duration: 600, easing: cubicOut }),
    radiusScale: new Tween(1, { duration: 600, easing: cubicOut }),
    highlightYounger: new Tween(1, { duration: 400, easing: cubicOut }),
    highlightSimilar: new Tween(1, { duration: 400, easing: cubicOut }),
    highlightOlder: new Tween(1, { duration: 400, easing: cubicOut }),
    authorHighlightOpacity: new Tween(1, { duration: 600, easing: cubicOut }),
    // Use CSS transform instead of viewBox
    scaleX: new Tween(1, { duration: 800, easing: cubicOut }),
    scaleY: new Tween(1, { duration: 800, easing: cubicOut }),
    translateY: new Tween(0, { duration: 800, easing: cubicOut })
  };

  // State variables
  let colorMode = $state('age_diff');
  let highlightedAuthor = $state(null);
  let hovered = $state(null);

  // Step configuration - much cleaner data structure
  const stepConfigs = {
    0: {
      yearRange: [1999, 2023],
      colorMode: 'age_diff',
      radiusScale: 1,
      highlightedAuthor: null,
      zoomLevel: 'zoomed' // Will zoom into this range
    },
    1: {
      yearRange: [2001, 2023],
      colorMode: 'shared_institutions',
      radiusScale: 1.2,
      highlightedAuthor: null,
      zoomLevel: 'normal' // Normal view
    },
    2: {
      yearRange: [2008, 2023],
      colorMode: 'age_diff',
      radiusScale: 1.2,
      highlightedAuthor: null,
      zoomLevel: 'normal' // Will zoom into this range
    },
    3: {
      yearRange: [2008, 2023],
      colorMode: 'shared_institutions',
      radiusScale: 0.9,
      highlightedAuthor: 'A5002034958',
      authorHighlightOpacity: 0.2,
      zoomLevel: 'overview' // Zoomed out view
    },
    4: {
      yearRange: [2008, 2023],
      colorMode: 'age_diff',
      radiusScale: 1,
      highlightedAuthor: null,
      zoomLevel: 'normal' // Back to normal
    }
  };

  // Default configuration
  const defaultConfig = {
    yearRange: [1999, 2023],
    colorMode: 'age_diff',
    radiusScale: 1,
    highlightedAuthor: null,
    authorHighlightOpacity: 1,
    zoomLevel: 'normal'
  };

  function processData() {
    if (!data || data.length === 0) {
      console.log("No data to process");
      basePoints = [];
      return;
    }

    console.log("Processing data...", data.length, "items");
    const processedPoints = processDataPoints(data, width, height); // Back to original
    console.log("Created", processedPoints.length, "points");
    basePoints = processedPoints;
  }
  
  function getPointColor(point) {
    if (colorMode === 'shared_institutions') {
      const sharedInst = point.shared_institutions || 'None';
      if (sharedInst === 'None' || sharedInst === '') return "#D3D3D3";
      if (sharedInst.includes('University of Vermont')) return "#2E8B57";
      if (sharedInst.includes('Massachusetts Institute of Technology')) return "#FF6B35";
      if (sharedInst.includes('Earth Island Institute')) return "#4682B4";
      if (sharedInst.includes('Columbia University')) return "#4682B4";
      if (sharedInst.includes('Santa Fe Institute')) return "#B59410";
      return "#4682B4";
    } else {
      return point.color;
    }
  }

  // Apply step configuration
  function applyStepConfig(config) {
    const { 
      yearRange, 
      radiusScale = 1, 
      authorHighlightOpacity = 1,
      colorMode: newColorMode = 'age_diff',
      highlightedAuthor: newHighlightedAuthor = null,
      zoomLevel = 'normal'
    } = config;

    // Calculate transform for zoom effect
    const margin = 80;
    const chartHeight = height - 2 * margin;
    const fullYearRange = 2023 - 1999;
    
    if (zoomLevel === 'overview') {
      // Zoom out - scale down and center
      animationConfig.scaleX.target = 0.8;
      animationConfig.scaleY.target = 0.8;
      animationConfig.translateY.target = 0;
    } else if (zoomLevel === 'zoomed') {
      // Zoom into the specific year range
      const yearStartProgress = (yearRange[0] - 1999) / fullYearRange;
      const yearEndProgress = (yearRange[1] - 1999) / fullYearRange;
      const rangeSize = yearEndProgress - yearStartProgress;
      
      // Scale to make the range fill more of the view
      const zoomFactor = Math.min(1.5, 1 / rangeSize);
      animationConfig.scaleX.target = 1;
      animationConfig.scaleY.target = zoomFactor;
      
      // Translate to center the range
      const rangeCenterProgress = (yearStartProgress + yearEndProgress) / 2;
      const rangeCenterY = margin + rangeCenterProgress * chartHeight;
      const viewCenterY = height / 2;
      animationConfig.translateY.target = (viewCenterY - rangeCenterY) * zoomFactor;
    } else {
      // Normal view
      animationConfig.scaleX.target = 1;
      animationConfig.scaleY.target = 1;
      animationConfig.translateY.target = 0;
    }

    animationConfig.yearFilterMin.target = yearRange[0];
    animationConfig.yearFilterMax.target = yearRange[1];
    animationConfig.radiusScale.target = radiusScale;
    animationConfig.authorHighlightOpacity.target = authorHighlightOpacity;
    
    // Reset age group highlights to 1
    animationConfig.highlightYounger.target = 1;
    animationConfig.highlightSimilar.target = 1;
    animationConfig.highlightOlder.target = 1;
    animationConfig.opacityMultiplier.target = 1;

    // Apply state changes
    colorMode = newColorMode;
    highlightedAuthor = newHighlightedAuthor;
  }

  // Transform the data based on current animation state
  let plotData = $derived(
    basePoints.map(point => {
      const pointYear = parseInt(point.year);
      const ageDiff = parseFloat(point.age_diff);
      
      // Calculate age group multiplier
      let ageGroupMultiplier = 1;
      if (ageDiff > 7) ageGroupMultiplier = animationConfig.highlightOlder.current;
      else if (ageDiff < -7) ageGroupMultiplier = animationConfig.highlightYounger.current;
      else ageGroupMultiplier = animationConfig.highlightSimilar.current;
      
      // Calculate year-based opacity
      const inYearRange = pointYear >= animationConfig.yearFilterMin.current && 
                         pointYear <= animationConfig.yearFilterMax.current;
      const yearOpacity = inYearRange ? 1 : 0.2;

      // Author highlighting logic
      const isHighlightedAuthor = highlightedAuthor && point.coauth_aid === highlightedAuthor;
      const authorOpacity = highlightedAuthor ? 
        (isHighlightedAuthor ? 1 : animationConfig.authorHighlightOpacity.current) : 1;
      
      return {
        ...point,
        r: point.r * animationConfig.radiusScale.current * (isHighlightedAuthor ? 1.3 : 1),
        opacity: yearOpacity * animationConfig.opacityMultiplier.current * ageGroupMultiplier * authorOpacity,
        displayColor: getPointColor(point),
        isHighlighted: isHighlightedAuthor
      };
    })
  );

  // Process data when component mounts or data changes
  $effect(() => {
    processData();
  });

  // Handle scroll index changes
  $effect(() => {
    const config = scrollyIndex !== undefined ? 
      (stepConfigs[scrollyIndex] || defaultConfig) : 
      defaultConfig;
    
    applyStepConfig(config);
  });
</script>

<h2>Peter Sheridan Dodds's Coauthors: <span>{scrollyIndex !== undefined ? `Step ${scrollyIndex}` : "Overview"}</span></h2>
<div class="viz-container">
  <div class="viz-content">
    <div class="plot-container">
      <svg {width} {height} 
           style="border: 1px solid #e2e8f0; background: white; border-radius: 8px; transform: scaleX({animationConfig.scaleX.current}) scaleY({animationConfig.scaleY.current}) translateY({animationConfig.translateY.current}px); transition: transform 0.8s cubic-bezier(0.23, 1, 0.32, 1);">
        <!-- Center line -->
        <line 
          x1={width/2} 
          x2={width/2} 
          y1="0" 
          y2={height} 
          stroke="#e0e0e0" 
          stroke-width="1"
          stroke-dasharray="5,5"
        />
        
        <!-- Grid lines for years -->
        {#each Array.from({length: 13}, (_, i) => 1999 + i * 2) as year}
          {@const yearProgress = (year - 1999) / (2023 - 1999)}
          {@const margin = 80}
          {@const chartHeight = height - 2 * margin}
          {@const y = margin + yearProgress * chartHeight}
          <line 
            x1="0" 
            x2={width} 
            y1={y} 
            y2={y} 
            stroke="#f0f0f0" 
            stroke-width="1"
          />
          <text x="10" y={y + 4} text-anchor="start" font-size="11" fill="#666">
            {year}
          </text>
        {/each}
        
        <!-- Data points -->
        {#each plotData as point}
          <circle
            cx={point.x}
            cy={point.y}
            r={point.r}
            fill={point.displayColor}
            stroke="black"
            stroke-width="0.3"
            fill-opacity={hovered && hovered !== point ? 0.3 : point.opacity}
            style="cursor: pointer; transition: fill-opacity 0.2s, fill 0.5s;"
            onmouseover={() => hovered = point}
            onmouseleave={() => hovered = null}
          >
            <title>{point.name} ({point.year}) - {point.faculty}</title>
          </circle>
        {/each}
      </svg>
    </div>

    <!-- Stats display -->
    <div class="stats">
      <div class="stat">
        <span class="label">Year Range:</span> 
        <span class="value">{Math.round(animationConfig.yearFilterMin.current)}-{Math.round(animationConfig.yearFilterMax.current)}</span>
      </div>
      <div class="stat">
        <span class="label">Size Scale:</span> 
        <span class="value">{animationConfig.radiusScale.current.toFixed(1)}x</span>
      </div>
      <div class="stat">
        <span class="label">Color Mode:</span> 
        <span class="value">{colorMode === 'age_diff' ? 'Age Diff' : 'Institutions'}</span>
      </div>
      <div class="stat">
        <span class="label">View:</span> 
        <span class="value">{
          animationConfig.scaleX.current < 1 ? 'Overview' : 
          animationConfig.scaleY.current > 1.2 ? 'Zoomed' : 
          'Normal'
        }</span>
      </div>
      <div class="stat">
        <span class="label">Visible Points:</span> 
        <span class="value">{plotData.filter(p => p.opacity > 0.5).length}</span>
      </div>
    </div>

    {#if scrollyIndex === undefined}
      <p class="start-message">Scroll down to explore the collaboration timeline</p>
    {/if}
  </div>

  <!-- Tooltip -->
  {#if hovered}
    <div class="tooltip" style="left: {hovered.x - 5}px; top: {hovered.y - 20}px;">
      <strong>{hovered.name}</strong> ({hovered.year})<br>
      Age difference: {hovered.age_diff} years<br>
      Total collaborations: {hovered.collabs}
    </div>
  {/if}
</div>

<style>
  .viz-container {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    border: 1px solid #e2e8f0;
    padding: 2rem;
    width: 100%;
    max-width: 700px;
    text-align: center;
  }

  h2 {
    position: sticky;
    top: 0;
    z-index: 10;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    margin: 0 0 1.5rem 0;
    padding: 1rem 0;
    font-size: 1.3rem;
    color: #2d3748;
    font-family: system-ui, sans-serif;
    font-weight: 400;
    border-bottom: 1px solid #e2e8f0;
  }

  h2 span {
    color: #667eea;
    font-weight: bold;
  }

  .plot-container {
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: center;
  }

  .stats {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    flex-wrap: wrap;
    font-family: monospace;
    font-size: 0.8rem;
    margin-bottom: 1.5rem;
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
    font-size: 1rem;
    margin-top: 1rem;
    font-style: italic;
  }

  .tooltip {
    position: absolute;
    background: rgba(0,0,0,0.9);
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 12px;
    pointer-events: none;
    z-index: 1000;
    font-family: system-ui, sans-serif;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    white-space: nowrap;
  }

  @media (max-width: 768px) {
    .viz-container {
      padding: 1rem;
    }
    
    h2 {
      font-size: 1.1rem;
    }
    
    .stats {
      gap: 0.25rem;
    }
    
    .stat {
      min-width: 70px;
      padding: 0.4rem;
    }
  }
</style>