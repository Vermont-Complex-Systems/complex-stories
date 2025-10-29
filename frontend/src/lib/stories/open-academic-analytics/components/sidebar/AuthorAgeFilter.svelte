<script>
  import * as d3 from 'd3';
  import { dashboardState, unique } from '../../state.svelte.js';

  let availableAuthors = $derived(unique.authors);      // ✅ Clean
  
  // Extract age data from available authors and calculate range
  let authorAgeData = $derived.by(() => {
    if (!availableAuthors || availableAuthors.length === 0) return { ages: [], min: 0, max: 100 };
    
    const ages = availableAuthors
      .map(author => +author.current_age || 0)
      .filter(age => age > 0 && age < 120)
      .sort((a, b) => a - b);
    
    if (ages.length === 0) return { ages: [], min: 0, max: 100 };
    
    return {
      ages,
      min: Math.floor(Math.min(...ages) / 5) * 5,
      max: Math.ceil(Math.max(...ages) / 5) * 5
    };
  });

  // SVG dimensions
  const width = 240;
  const height = 100;
  const margin = { top: 10, right: 40, bottom: 35, left: 20 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  // Create histogram bins
  let histogram = $derived.by(() => {
    if (!authorAgeData.ages.length) return [];
    
    const binGenerator = d3.bin()
      .domain([authorAgeData.min, authorAgeData.max])
      .thresholds(12);
    
    return binGenerator(authorAgeData.ages);
  });

  // Scales
  let xScale = $derived(d3.scaleLinear()
    .domain([authorAgeData.min, authorAgeData.max])
    .range([0, chartWidth]));

  let yScale = $derived.by(() => {
    const maxCount = Math.max(...histogram.map(d => d.length), 1);
    return d3.scaleLinear()
      .domain([0, maxCount])
      .range([chartHeight, 0]);
  });

  // Selected bins state
  let selectedBins = $state(new Set());

  // Calculate age range from selected bins
  let selectedAgeRange = $derived.by(() => {
    if (selectedBins.size === 0) return null;
    
    const selectedBinArray = Array.from(selectedBins);
    const minBin = Math.min(...selectedBinArray);
    const maxBin = Math.max(...selectedBinArray);
    
    return [
      Math.round(histogram[minBin]?.x0 || authorAgeData.min),
      Math.round(histogram[maxBin]?.x1 || authorAgeData.max)
    ];
  });

  // Update dashboard state when selection changes
  $effect(() => {
    dashboardState.authorAgeFilter = selectedAgeRange;
  });

  // Handle bin click
  function handleBinClick(binIndex, event) {
    event.stopPropagation();
    
    if (event.shiftKey && selectedBins.size > 0) {
      // Shift+click: select range from first selected to clicked bin
      const existingBins = Array.from(selectedBins);
      const minExisting = Math.min(...existingBins);
      const maxExisting = Math.max(...existingBins);
      
      const rangeStart = Math.min(minExisting, binIndex);
      const rangeEnd = Math.max(maxExisting, binIndex);
      
      selectedBins = new Set();
      for (let i = rangeStart; i <= rangeEnd; i++) {
        selectedBins.add(i);
      }
    } else if (event.ctrlKey || event.metaKey) {
      // Ctrl/Cmd+click: toggle individual bin
      if (selectedBins.has(binIndex)) {
        selectedBins.delete(binIndex);
      } else {
        selectedBins.add(binIndex);
      }
      selectedBins = new Set(selectedBins); // Trigger reactivity
    } else {
      // Regular click: select only this bin
      selectedBins = new Set([binIndex]);
    }
  }

  // Handle keyboard events for bins
  function handleBinKeydown(event, binIndex) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleBinClick(binIndex, event);
    } else if (event.key === 'Escape') {
      event.preventDefault();
      clearFilter();
    }
  }

  // Clear selection
  function clearFilter() {
    selectedBins = new Set();
  }

  // Show filtered author count
  let filteredAuthorCount = $derived.by(() => {
    if (!selectedAgeRange) return availableAuthors.length;
    const [min, max] = selectedAgeRange;
    return availableAuthors.filter(author => {
      const age = author.current_age || 0;
      return age >= min && age <= max;
    }).length;
  });
</script>

<div class="age-filter-section">
  <div class="filter-section">
    
    <!-- Range display -->
    {#if selectedAgeRange}
      <div class="range-display">
        <span class="range-label">Age Range:</span>
        <span class="range-values">
          {selectedAgeRange[0]} - {selectedAgeRange[1]} years
        </span>
        <span class="filter-badge">
          {filteredAuthorCount} of {availableAuthors.length}
        </span>
        <button class="clear-button" onclick={clearFilter}>Clear</button>
      </div>
    {/if}

    <!-- Histogram with clickable bins -->
    <div class="chart-container">
      <svg {width} {height} class="age-chart">
        <g transform="translate({margin.left}, {margin.top})">
          
          <!-- Histogram bars with accessibility -->
          {#each histogram as bin, i}
            {@const barHeight = chartHeight - yScale(bin.length)}
            {@const barWidth = Math.max(1, xScale(bin.x1) - xScale(bin.x0) - 1)}
            {@const isSelected = selectedBins.has(i)}
            {@const ageRangeText = `${Math.round(bin.x0)} to ${Math.round(bin.x1)} years`}
            {@const countText = `${bin.length} author${bin.length !== 1 ? 's' : ''}`}
            <rect
              x={xScale(bin.x0)}
              y={yScale(bin.length)}
              width={barWidth}
              height={barHeight}
              fill={isSelected ? "var(--color-good-blue)" : "var(--color-gray-300)"}
              stroke={isSelected ? "var(--color-good-blue)" : "var(--color-gray-400)"}
              stroke-width={isSelected ? "2" : "0.5"}
              style="cursor: pointer;"
              onclick={(e) => handleBinClick(i, e)}
              onkeydown={(e) => handleBinKeydown(e, i)}
              tabindex="0"
              role="button"
              aria-label={`Age range ${ageRangeText}, ${countText}. ${isSelected ? 'Selected' : 'Not selected'}`}
              aria-pressed={isSelected}
              class="histogram-bar"
            />
          {/each}

          <!-- X-axis -->
          <g transform="translate(0, {chartHeight})">
            <line x1={0} x2={chartWidth} stroke="var(--color-border)" />
            <text x={0} y={15} text-anchor="start" class="axis-label">{authorAgeData.min}</text>
            <text x={chartWidth} y={15} text-anchor="end" class="axis-label">{authorAgeData.max}</text>
            <text x={chartWidth / 2} y={30} text-anchor="middle" class="axis-title">Academic Age</text>
          </g>
        </g>
      </svg>
    </div>

    <div class="interaction-help">
      <p class="filter-info">
        <strong>Click</strong> a bar to select that age range • 
        <strong>Ctrl+Click</strong> to select multiple • 
        <strong>Shift+Click</strong> to select range •
        <strong>Escape</strong> to clear selection
      </p>
    </div>
    
  </div>
</div>

<style>
  .age-filter-section {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .filter-section {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .range-display {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    padding: 0.5rem;
    background: var(--color-gray-50);
    border-radius: var(--border-radius);
    border: 1px solid var(--color-border);
  }

  :global(.dark) .range-display {
    background: var(--color-gray-800);
  }

  .range-label {
    font-size: var(--font-size-small);
    font-weight: var(--font-weight-medium);
    color: var(--color-fg);
  }

  .range-values {
    font-size: var(--font-size-small);
    color: var(--color-good-blue);
    font-weight: var(--font-weight-bold);
  }

  .filter-badge {
    background: var(--color-good-blue);
    color: white;
    padding: 0.125rem 0.375rem;
    border-radius: 12px;
    font-size: var(--font-size-xxsmall);
    font-weight: var(--font-weight-bold);
    margin-left: auto;
  }

  .clear-button {
    padding: 0.25rem 0.5rem;
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    background: var(--color-bg);
    color: var(--color-secondary-gray);
    font-size: var(--font-size-xxsmall);
    cursor: pointer;
    transition: all var(--transition-fast) ease;
  }

  .clear-button:hover {
    background: var(--color-gray-100);
    color: var(--color-fg);
  }

  .chart-container {
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    background: var(--color-bg);
    overflow: hidden;
  }

  .age-chart {
    display: block;
    width: 100%;
  }

  .histogram-bar {
    transition: all 0.2s ease;
  }

  .histogram-bar:hover,
  .histogram-bar:focus {
    fill-opacity: 0.8;
    stroke-width: 2;
    outline: none;
  }

  .histogram-bar:focus {
    stroke: var(--color-focus, #3b82f6);
    stroke-width: 3;
  }

  :global(.age-chart .axis-label) {
    font-size: var(--font-size-xxsmall);
    font-family: var(--font-mono);
    fill: var(--color-secondary-gray);
  }

  :global(.age-chart .axis-title) {
    font-size: var(--font-size-xsmall);
    font-family: var(--font-body);
    font-weight: var(--font-weight-medium);
    fill: var(--color-fg);
  }

  .interaction-help {
    text-align: center;
  }

  .filter-info {
    font-size: var(--font-size-xsmall);
    color: var(--color-secondary-gray);
    margin: 0;
    line-height: 1.3;
  }

  /* Dark mode */
  :global(.dark) .clear-button:hover {
    background: var(--color-gray-700);
  }
</style>