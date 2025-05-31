<!-- PaperBubbleChart.svelte -->
<script>
  import { processPaperDataPoints, getPaperDataDateRange } from '../utils/paperChartUtils.js';
  import { Tween } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';

  let { scrollyIndex, data, width, height } = $props();

  console.log("Paper chart loaded with data:", data?.length);
  let basePoints = $state([]);

  // Animation parameters
  const animationConfig = {
    yearFilterMin: new Tween(1999, { duration: 800, easing: cubicOut }),
    yearFilterMax: new Tween(2025, { duration: 800, easing: cubicOut }),
    opacityMultiplier: new Tween(1, { duration: 600, easing: cubicOut }),
    radiusScale: new Tween(1, { duration: 600, easing: cubicOut }),
    highlightHighCited: new Tween(1, { duration: 400, easing: cubicOut }),
    highlightMediumCited: new Tween(1, { duration: 400, easing: cubicOut }),
    highlightLowCited: new Tween(1, { duration: 400, easing: cubicOut }),
    // Transform controls
    scaleX: new Tween(1, { duration: 800, easing: cubicOut }),
    scaleY: new Tween(1, { duration: 800, easing: cubicOut }),
    translateY: new Tween(0, { duration: 800, easing: cubicOut })
  };

  // State variables
  let colorMode = $state('coauthors');
  let hovered = $state(null);

  // Step configuration for papers
  const stepConfigs = {
    0: {
      yearRange: [1999, 2025],
      colorMode: 'coauthors',
      radiusScale: 1,
      viewMode: 'normal'
    },
    1: {
      yearRange: [2010, 2025],
      colorMode: 'citations',
      radiusScale: 1.2,
      viewMode: 'focus'
    },
    2: {
      yearRange: [2020, 2025],
      colorMode: 'coauthors',
      radiusScale: 1.5,
      viewMode: 'focus'
    },
    3: {
      yearRange: [1999, 2025],
      colorMode: 'citations',
      radiusScale: 0.8,
      viewMode: 'overview'
    }
  };

  // Default configuration
  const defaultConfig = {
    yearRange: [1999, 2025],
    colorMode: 'coauthors',
    radiusScale: 1,
    viewMode: 'normal'
  };

  function processData() {
    if (!data || data.length === 0) {
      console.log("No paper data to process");
      basePoints = [];
      return;
    }

    console.log("Processing paper data...", data.length, "items");
    const processedPoints = processPaperDataPoints(data, width, height);
    console.log("Created", processedPoints.length, "paper points");
    basePoints = processedPoints;
  }
  
  function getPointColor(point) {
    if (colorMode === 'citations') {
      const citations = point.cited_by_count;
      if (citations === 0) return "#D3D3D3";
      if (citations >= 100) return "#440154FF"; // High citations (purple)
      if (citations >= 20) return "#2A788EFF"; // Medium citations (teal)
      if (citations >= 5) return "#20A387FF"; // Some citations (green)
      return "#FDE725FF"; // Few citations (yellow)
    } else {
      return point.color; // Coauthor-based coloring
    }
  }

  // Apply step configuration
  function applyStepConfig(config) {
    const { 
      yearRange, 
      radiusScale = 1, 
      colorMode: newColorMode = 'coauthors',
      viewMode = 'normal'
    } = config;

    // Calculate transforms based on view mode
    const margin = 80;
    const chartHeight = height - 2 * margin;
    const dataRange = data ? getPaperDataDateRange(data) : [new Date('1999-01-01'), new Date('2027-12-31')];
    const fullYearRange = dataRange[1].getFullYear() - dataRange[0].getFullYear();
    
    if (viewMode === 'overview') {
      animationConfig.scaleX.target = 0.8;
      animationConfig.scaleY.target = 0.8;
      animationConfig.translateY.target = 0;
    } else if (viewMode === 'focus') {
      const yearRangeStart = yearRange[0];
      const yearRangeEnd = yearRange[1];
      const yearRangeCenter = (yearRangeStart + yearRangeEnd) / 2;
      
      const centerProgress = (yearRangeCenter - dataRange[0].getFullYear()) / fullYearRange;
      const centerY = margin + centerProgress * chartHeight;
      
      const viewCenterY = height / 2;
      const translation = (viewCenterY - centerY) * 0.6;
      
      animationConfig.scaleX.target = 1;
      animationConfig.scaleY.target = 1.1;
      animationConfig.translateY.target = translation;
    } else {
      animationConfig.scaleX.target = 1;
      animationConfig.scaleY.target = 1;
      animationConfig.translateY.target = 0;
    }

    animationConfig.yearFilterMin.target = yearRange[0];
    animationConfig.yearFilterMax.target = yearRange[1];
    animationConfig.radiusScale.target = radiusScale;
    
    // Reset citation group highlights to 1
    animationConfig.highlightHighCited.target = 1;
    animationConfig.highlightMediumCited.target = 1;
    animationConfig.highlightLowCited.target = 1;
    animationConfig.opacityMultiplier.target = 1;

    // Apply state changes
    colorMode = newColorMode;
  }

  // Transform the data based on current animation state
  let plotData = $derived(
    basePoints.map(point => {
      const pointYear = parseInt(point.year);
      const citations = point.cited_by_count;
      
      // Calculate citation group multiplier
      let citationGroupMultiplier = 1;
      if (citations >= 20) citationGroupMultiplier = animationConfig.highlightHighCited.current;
      else if (citations >= 5) citationGroupMultiplier = animationConfig.highlightMediumCited.current;
      else citationGroupMultiplier = animationConfig.highlightLowCited.current;
      
      // Calculate year-based opacity
      const inYearRange = pointYear >= animationConfig.yearFilterMin.current && 
                         pointYear <= animationConfig.yearFilterMax.current;
      const yearOpacity = inYearRange ? 1 : 0.2;
      
      return {
        ...point,
        r: point.r * animationConfig.radiusScale.current,
        opacity: yearOpacity * animationConfig.opacityMultiplier.current * citationGroupMultiplier,
        displayColor: getPointColor(point)
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

<h2>Peter Sheridan Dodds's Papers: <span>{scrollyIndex !== undefined ? `Step ${scrollyIndex}` : "Overview"}</span></h2>
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
        {#each Array.from({length: 13}, (_, i) => {
          const dateRange = data ? getPaperDataDateRange(data) : [new Date('1999-01-01'), new Date('2027-12-31')];
          const startYear = dateRange[0].getFullYear();
          const endYear = dateRange[1].getFullYear();
          return startYear + i * 2;
        }).filter(year => {
          const dateRange = data ? getPaperDataDateRange(data) : [new Date('1999-01-01'), new Date('2027-12-31')];
          return year <= dateRange[1].getFullYear();
        }) as year}
          {@const dateRange = data ? getPaperDataDateRange(data) : [new Date('1999-01-01'), new Date('2027-12-31')]}
          {@const yearDate = new Date(year, 0, 1)}
          {@const dateProgress = (yearDate - dateRange[0]) / (dateRange[1] - dateRange[0])}
          {@const margin = 80}
          {@const chartHeight = height - 2 * margin}
          {@const y = margin + dateProgress * chartHeight}
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
            <title>{point.title} ({point.year}) - {point.cited_by_count} citations</title>
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
        <span class="value">{colorMode === 'coauthors' ? 'Coauthors' : 'Citations'}</span>
      </div>
      <div class="stat">
        <span class="label">View:</span> 
        <span class="value">{
          animationConfig.scaleX.current < 0.9 ? 'Overview' : 
          animationConfig.scaleY.current > 1.05 ? 'Focus' : 
          'Normal'
        }</span>
      </div>
      <div class="stat">
        <span class="label">Visible Papers:</span> 
        <span class="value">{plotData.filter(p => p.opacity > 0.5).length}</span>
      </div>
    </div>

    {#if scrollyIndex === undefined}
      <p class="start-message">Scroll down to explore the publication timeline</p>
    {/if}
  </div>

  <!-- Tooltip -->
  {#if hovered}
    <div class="tooltip" style="left: {hovered.x - 5}px; top: {hovered.y - 20}px;">
      <strong>{hovered.title.slice(0, 50)}...</strong><br>
      <span class="year">({hovered.year})</span><br>
      Citations: {hovered.cited_by_count}<br>
      Coauthors: {hovered.nb_coauthors}
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
    max-width: 300px;
  }

  .year {
    color: #cbd5e0;
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