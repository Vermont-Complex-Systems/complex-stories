<!-- CombinedBubbleChart.svelte -->
<script>
  import { processCombinedDataPoints, getCombinedDataDateRange } from '../utils/combinedChartUtils.js';
  import { Tween } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';

  let { scrollyIndex, coauthorData, paperData, width, height } = $props();

  console.log("Combined chart loaded with:", coauthorData?.length, "coauthors,", paperData?.length, "papers");
  let basePoints = $state([]);

  // Animation parameters
  const animationConfig = {
    yearFilterMin: new Tween(1999, { duration: 800, easing: cubicOut }),
    yearFilterMax: new Tween(2025, { duration: 800, easing: cubicOut }),
    opacityMultiplier: new Tween(1, { duration: 600, easing: cubicOut }),
    radiusScale: new Tween(1, { duration: 600, easing: cubicOut }),
    coauthorOpacity: new Tween(1, { duration: 400, easing: cubicOut }),
    paperOpacity: new Tween(1, { duration: 400, easing: cubicOut }),
    authorHighlightOpacity: new Tween(1, { duration: 600, easing: cubicOut }),
    // Transform controls
    scaleX: new Tween(1, { duration: 800, easing: cubicOut }),
    scaleY: new Tween(1, { duration: 800, easing: cubicOut }),
    translateY: new Tween(0, { duration: 800, easing: cubicOut })
  };

  // State variables
  let colorMode = $state('type'); // 'type', 'age_diff', 'citations'
  let highlightedAuthor = $state(null);
  let hovered = $state(null);

  // Step configuration
  const stepConfigs = {
    0: {
      yearRange: [1999, 2025],
      colorMode: 'age_diff', // Start with age diff
      radiusScale: 1.2,
      highlightedAuthor: null,
      viewMode: 'normal',
      focus: 'both'
    },
    1: {
      yearRange: [2001, 2025],
      colorMode: 'shared_institutions', // Switch to institutions
      radiusScale: 1.2,
      highlightedAuthor: null,
      viewMode: 'focus',
      focus: 'both'
    },
    2: {
      yearRange: [2008, 2025],
      colorMode: 'age_diff', // Back to age diff
      radiusScale: 1.2,
      highlightedAuthor: null,
      viewMode: 'focus',
      focus: 'both'
    },
    3: {
      yearRange: [2008, 2023],
      colorMode: 'shared_institutions', // Institutions again
      radiusScale: 0.9,
      highlightedAuthor: 'A5002034958',
      authorHighlightOpacity: 0.2,
      viewMode: 'overview',
      focus: 'papers'
    },
    4: {
      yearRange: [2008, 2025],
      colorMode: 'age_diff', // Back to age diff
      radiusScale: 1,
      highlightedAuthor: null,
      viewMode: 'normal',
      focus: 'both'
    }
  };

  // Default configuration
  const defaultConfig = {
    yearRange: [1999, 2025],
    colorMode: 'type',
    radiusScale: 1,
    highlightedAuthor: null,
    authorHighlightOpacity: 1,
    viewMode: 'normal',
    focus: 'both'
  };

  function processData() {
    if ((!coauthorData || coauthorData.length === 0) && (!paperData || paperData.length === 0)) {
      console.log("No data to process");
      basePoints = [];
      return;
    }

    console.log("Processing combined data...");
    const processedPoints = processCombinedDataPoints(coauthorData, paperData, width, height);
    console.log("Created", processedPoints.length, "combined points");
    basePoints = processedPoints;
  }
  
    function getPointColor(point) {
    if (point.type === 'paper') {
      return "#888888"; // Always grey for papers
    }
    
    if (colorMode === 'shared_institutions' && point.type === 'coauthor') {
      const sharedInst = point.shared_institutions || 'None';
      if (sharedInst === 'None' || sharedInst === '') return "#D3D3D3";
      if (sharedInst.includes('University of Vermont')) return "#2E8B57";
      if (sharedInst.includes('Massachusetts Institute of Technology')) return "#FF6B35";
      if (sharedInst.includes('Earth Island Institute')) return "#4682B4";
      if (sharedInst.includes('Columbia University')) return "#4682B4";
      if (sharedInst.includes('Santa Fe Institute')) return "#B59410";
      return "#4682B4";
    } else if (colorMode === 'age_diff' && point.type === 'coauthor') {
      return point.color; // Age diff coloring for coauthors
    } else if (colorMode === 'type') {
      return point.color; // Use original colors based on type
    } else {
      return "#D3D3D3"; // Gray out irrelevant points
    }
  }

  // Apply step configuration
  function applyStepConfig(config) {
    const { 
      yearRange, 
      radiusScale = 1, 
      authorHighlightOpacity = 1,
      colorMode: newColorMode = 'type',
      highlightedAuthor: newHighlightedAuthor = null,
      viewMode = 'normal',
      focus = 'both'
    } = config;

    // Calculate transforms based on view mode
    const margin = 80;
    const chartHeight = height - 2 * margin;
    const dataRange = getCombinedDataDateRange(coauthorData, paperData);
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

    // Set focus opacity
    if (focus === 'coauthors') {
      animationConfig.coauthorOpacity.target = 1;
      animationConfig.paperOpacity.target = 0.3;
    } else if (focus === 'papers') {
      animationConfig.coauthorOpacity.target = 1;
      animationConfig.paperOpacity.target = 1;
    } else {
      animationConfig.coauthorOpacity.target = 1;
      animationConfig.paperOpacity.target = 1;
    }

    animationConfig.yearFilterMin.target = yearRange[0];
    animationConfig.yearFilterMax.target = yearRange[1];
    animationConfig.radiusScale.target = radiusScale;
    animationConfig.authorHighlightOpacity.target = authorHighlightOpacity;
    animationConfig.opacityMultiplier.target = 1;

    // Apply state changes
    colorMode = newColorMode;
    highlightedAuthor = newHighlightedAuthor;
  }

  // Transform the data based on current animation state
  let plotData = $derived(
    basePoints.map(point => {
      const pointYear = parseInt(point.year);
      
      // Calculate year-based opacity
      const inYearRange = pointYear >= animationConfig.yearFilterMin.current && 
                         pointYear <= animationConfig.yearFilterMax.current;
      const yearOpacity = inYearRange ? 1 : 0.2;

      // Type-based opacity
      const typeOpacity = point.type === 'coauthor' ? 
        animationConfig.coauthorOpacity.current : 
        animationConfig.paperOpacity.current;

      // Author highlighting logic
      const isHighlightedAuthor = highlightedAuthor && point.coauth_aid === highlightedAuthor;
      const authorOpacity = highlightedAuthor ? 
        (isHighlightedAuthor ? 1 : animationConfig.authorHighlightOpacity.current) : 1;
      
      return {
        ...point,
        r: point.r * animationConfig.radiusScale.current * (isHighlightedAuthor ? 1.3 : 1),
        opacity: yearOpacity * animationConfig.opacityMultiplier.current * typeOpacity * authorOpacity,
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

<h2>Peter Sheridan Dodds's Academic Timeline: <span>{scrollyIndex !== undefined ? `Step ${scrollyIndex}` : "Overview"}</span></h2>
<div class="viz-content">
  <div class="plot-container">
    <svg {width} {height} 
     style="border: 1px solid #e2e8f0; background: white; border-radius: 8px; transform: scaleX({animationConfig.scaleX.current}) scaleY({animationConfig.scaleY.current}) translateY({animationConfig.translateY.current}px); transition: transform 0.8s cubic-bezier(0.23, 1, 0.32, 1);">
  
  <!-- Left center line (Coauthors) -->
  <line 
    x1={width * 0.25} 
    x2={width * 0.25} 
    y1="0" 
    y2={height} 
    stroke="#e0e0e0" 
    stroke-width="1"
    stroke-dasharray="5,5"
  />
  
  <!-- Right center line (Papers) - closer to divider -->
  <line 
    x1={width * 0.6} 
    x2={width * 0.6} 
    y1="0" 
    y2={height} 
    stroke="#e0e0e0" 
    stroke-width="1"
    stroke-dasharray="5,5"
  />
  
  <!-- Vertical divider -->
  <line 
    x1={width * 0.5} 
    x2={width * 0.5} 
    y1="0" 
    y2={height} 
    stroke="#d0d0d0" 
    stroke-width="2"
  />
  
  <!-- Grid lines for years - Dynamic generation -->
  {#each (() => {
    const dateRange = getCombinedDataDateRange(coauthorData, paperData);
    const startYear = dateRange[0].getFullYear();
    const endYear = dateRange[1].getFullYear();
    const years = [];
    
    // Generate ALL years from start to end with 2-year intervals
    for (let year = startYear; year <= endYear; year += 2) {
      years.push(year);
    }
    
    console.log("Grid years generated:", years);
    return years;
  })() as year}
    {@const dateRange = getCombinedDataDateRange(coauthorData, paperData)}
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
  
  <!-- Section labels -->
  <text x={width * 0.25} y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#666">
    Coauthors
  </text>
  <text x={width * 0.6} y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#666">
    Papers
  </text>
  
  <!-- Data points -->
  {#each plotData as point}
      <!-- Coauthor circles -->
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
  
 <!-- Updated Legend -->
<g transform="translate({width - 150}, 50)">
  <circle cx="10" cy="10" r="6" fill="#20A387FF" stroke="black" stroke-width="0.3"/>
  <text x="20" y="15" font-size="11" fill="#666">Coauthors</text>
  <rect x="4" y="24" width="12" height="12" fill="#888888" stroke="black" stroke-width="0.8"/>
  <text x="20" y="35" font-size="11" fill="#666">Papers</text>
</g>
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
      <span class="value">{colorMode === 'type' ? 'Type' : colorMode === 'age_diff' ? 'Age Diff' : 'Citations'}</span>
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
      <span class="label">Visible Points:</span> 
      <span class="value">{plotData.filter(p => p.opacity > 0.5).length}</span>
    </div>
  </div>

  {#if scrollyIndex === undefined}
    <p class="start-message">Scroll down to explore the combined timeline</p>
  {/if}
</div>

<!-- Tooltip -->
{#if hovered}
  <div class="tooltip" style="left: {hovered.x - 5}px; top: {hovered.y - 20}px;">
    {#if hovered.type === 'coauthor'}
      <strong>{hovered.name}</strong> ({hovered.year})<br>
      Age difference: {hovered.age_diff} years<br>
      Total collaborations: {hovered.collabs}
    {:else}
      <strong>{hovered.title.slice(0, 50)}...</strong><br>
      <span class="year">({hovered.year})</span><br>
      Citations: {hovered.cited_by_count}<br>
      Coauthors: {hovered.nb_coauthors}
    {/if}
  </div>
{/if}

<style>
  .viz-content {
    padding: 1rem;
    width: 100%;
    text-align: center;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    border: 1px solid #e2e8f0;
  }

  h2 {
    position: sticky;
    top: 0;
    z-index: 10;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    margin: 0 0 1rem 0;
    padding: 0.75rem 0;
    font-size: 1.2rem;
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
</style>