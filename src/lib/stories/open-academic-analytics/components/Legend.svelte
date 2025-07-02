<script>
  import * as d3 from 'd3';
  import { ageColorScale, collaborationColorScale } from '../utils/combinedChartUtils.js';

  let { 
    colorMode = 'age_diff',
    coauthorData = [],
    visible = true
  } = $props();

  // Create institution color scale when needed
  let institutionColorScale = $derived.by(() => {
    if (colorMode !== 'institutions' || !coauthorData.length) return null;
    const uniqueInstitutions = [...new Set(coauthorData.map(d => d.institution))]
      .filter(inst => inst != null && inst !== '');
    return d3.scaleOrdinal(d3.schemeTableau10).domain(uniqueInstitutions);
  });

  // Create shared institution color scale when needed
  let sharedInstitutionColorScale = $derived.by(() => {
    if (colorMode !== 'shared_institutions' || !coauthorData.length) return null;
    const uniqueSharedInstitutions = [...new Set(coauthorData.map(d => d.shared_institutions))]
      .filter(inst => inst != null && inst !== '');
    return d3.scaleOrdinal(d3.schemeTableau10).domain(uniqueSharedInstitutions);
  });

  // Generate legend items based on color mode - Observable Plot style
  let legendItems = $derived.by(() => {
    if (!visible) return [];
    
    if (colorMode === 'age_diff') {
      return [
        { label: 'Older (>7 years)', color: ageColorScale('older') },
        { label: 'Same age (±7 years)', color: ageColorScale('same') },
        { label: 'Younger (<-7 years)', color: ageColorScale('younger') }
      ];
    } 
    
    if (colorMode === 'acquaintance') {
      // Use collaboration-based legend that matches the threshold scale
      return [
        { label: 'New (1 collaboration)', color: collaborationColorScale(1) },
        { label: 'Repeat (2-3 collaborations)', color: collaborationColorScale(2) },
        { label: 'Regular (4-8 collaborations)', color: collaborationColorScale(4) },
        { label: 'Long-term (9+ collaborations)', color: collaborationColorScale(9) }
      ];
    } 
    
    if (colorMode === 'institutions' && coauthorData.length > 0) {
      const uniqueInstitutions = [...new Set(coauthorData.map(d => d.institution))]
        .filter(inst => inst != null && inst !== '');
      const hasUnknown = coauthorData.some(d => d.institution == null || d.institution === '');
      
      const items = uniqueInstitutions.map(institution => ({
        label: institution,
        color: institutionColorScale(institution)
      }));
      
      return items;
    }

    if (colorMode === 'shared_institutions' && coauthorData.length > 0) {
      const uniqueSharedInstitutions = [...new Set(coauthorData.map(d => d.shared_institutions))]
        .filter(inst => inst != null && inst !== '');
      const hasUnknown = coauthorData.some(d => d.shared_institutions == null || d.shared_institutions === '');
      
      const items = uniqueSharedInstitutions.map(institution => ({
        label: institution,
        color: sharedInstitutionColorScale(institution)
      }));
      
      
      return items;
    }
    
    return [];
  });

  // Legend title based on mode
  let legendTitle = $derived.by(() => {
    switch (colorMode) {
      case 'age_diff': return 'Age Difference';
      case 'acquaintance': return 'Collaboration Type';
      case 'institutions': return 'Institutions';
      case 'shared_institutions': return 'Shared Institutions';
      default: return 'Legend';
    }
  });
</script>

{#if legendItems.length > 0}
  <div class="legend">
    <h4>{legendTitle}</h4>
    {#each legendItems as item}
      <div class="legend-item">
        <div class="legend-color" style="background-color: {item.color}"></div>
        <span class="legend-label">{item.label}</span>
      </div>
    {/each}
  </div>
{/if}

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
    max-width: 200px;
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
    flex-shrink: 0;
  }

  .legend-label {
    color: var(--chart-text-color, var(--color-fg));
    line-height: 1.2;
    font-size: var(--font-size-xsmall);
  }

  /* Dark mode support */
  :global(.dark) .legend {
    background: var(--color-bg);
    border-color: var(--color-border);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }
</style>