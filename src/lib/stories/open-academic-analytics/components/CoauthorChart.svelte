<script>
  import { processCoauthorData, getCoauthorColor, ageColorScale, acquaintanceColorScale } from '../utils/combinedChartUtils.js';
  import TimelineChart from './TimelineChart.svelte';

  let { 
    coauthorData, 
    paperData,
    width, 
    height, 
    colorMode = 'age_diff',
    highlightedCoauthor = null
  } = $props();

  // Process and style data for display
  let displayData = $derived.by(() => {
    if (!coauthorData || coauthorData.length === 0) return [];
    
    return coauthorData.map(d => {
      let opacity = 1;
      
      // Apply coauthor highlight filter if provided
      if (highlightedCoauthor) {
        const isHighlightedCoauthor = d.coauth_aid === highlightedCoauthor;
        opacity *= isHighlightedCoauthor ? 1 : 0.2;
      }

      // Create a point object with color information
      const point = {
        ...d,
        // Add age_category for color calculation
        age_category: d.age_diff > 7 ? 'older' : d.age_diff < -7 ? 'younger' : 'same',
        opacity,
        displayColor: getCoauthorColor({
          age_category: d.age_diff > 7 ? 'older' : d.age_diff < -7 ? 'younger' : 'same',
          all_times_collabo: d.all_times_collabo
        }, colorMode)
      };
      
      return point;
    });
  });

  // Legend data
  let legendData = $derived.by(() => {
    if (colorMode === 'age_diff') {
      return [
        { label: 'Older (>7 years)', color: ageColorScale('older') },
        { label: 'Same age (±7 years)', color: ageColorScale('same') },
        { label: 'Younger (<-7 years)', color: ageColorScale('younger') }
      ];
    } else if (colorMode === 'acquaintance') {
      return [
        { label: 'New collaboration', color: ageColorScale('new_collab') },
        { label: 'Repeat collaboration', color: ageColorScale('repeat_collab') },
        { label: 'Long-term collaboration', color: ageColorScale('long_term_collab') }
      ];
    }
    return [];
  });

  function formatTooltip(point) {
    return `Coauthor: ${point.coauth_name}\nYear: ${point.pub_year}\nAge difference: ${point.age_diff} years\nTotal collaborations: ${point.all_times_collabo}\nYearly collaborations: ${point.yearly_collabo}\nAcquaintance: ${point.acquaintance}`;
  }
</script>

<TimelineChart
  {paperData}
  {coauthorData}
  {width}
  {height}
  processDataFn={processCoauthorData}
  dataToDisplay={displayData}
  tooltipFormatter={formatTooltip}
>
  {#snippet pointComponent(point, showTooltip, hideTooltip)}
    <circle
      cx={point.x}
      cy={point.y}
      r={point.r}
      fill={point.displayColor}
      stroke="black"
      stroke-width="0.3"
      fill-opacity={point.opacity}
      class="data-point"
      on:mouseenter={(e) => showTooltip(e, point)}
      on:mouseleave={hideTooltip}
    />
  {/snippet}

  {#snippet legendComponent()}
    {#if legendData.length > 0}
      <div class="legend">
        <h4>Legend</h4>
        {#each legendData as item}
          <div class="legend-item">
            <div class="legend-color" style="background-color: {item.color}"></div>
            <span class="legend-label">{item.label}</span>
          </div>
        {/each}
      </div>
    {/if}
  {/snippet}
</TimelineChart>

<!-- Same styles as before -->
<style>
  .legend {
    position: absolute;
    top: 10px;
    right: 20px;
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    padding: 12px;
    font-size: var(--font-size-xsmall);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .legend h4 {
    margin: 0 0 8px 0;
    font-size: var(--font-size-small);
    font-weight: var(--font-weight-bold);
  }

  .legend-item {
    display: flex;
    align-items: center;
    margin: 4px 0;
  }

  .legend-color {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
    border: 1px solid black;
  }

  .legend-label {
    color: var(--color-secondary-gray);
  }

  :global(.dark) .legend {
    background: var(--color-bg);
    border-color: var(--color-border);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }
</style>