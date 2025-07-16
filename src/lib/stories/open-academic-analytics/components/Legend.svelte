<!-- Legend.svelte -->
<script>
  import * as d3 from 'd3';
  import { collaborationColorScale, acquaintanceColorScale, ageColorScale } from '../utils/combinedChartUtils.js';
  
  let { 
    colorMode, 
    coauthorData = [],
    visible = true 
  } = $props();

  // Generate dynamic legend items based on actual data
  let legendItems = $derived.by(() => {
    if (colorMode === 'age_diff') {
      return [
        { color: ageColorScale('older'), label: 'Older coauthor (+7 years)' },
        { color: ageColorScale('same'), label: 'Similar age (±7 years)' },
        { color: ageColorScale('younger'), label: 'Younger coauthor (-7 years)' }
      ];
    } else if (colorMode === 'acquaintance') {
      // Use acquaintanceColorScale for collaboration counts
      return [
        { color: acquaintanceColorScale(1), label: 'Few collaborations (1)' },
        { color: acquaintanceColorScale(3), label: 'Some collaborations (2-4)' },
        { color: acquaintanceColorScale(5), label: 'Many collaborations (5+)' }
      ];
    } else if (colorMode === 'institutions' && coauthorData.length > 0) {
      // Get unique institutions from data
      const institutionField = coauthorData.some(d => d.institution_normalized) 
        ? 'institution_normalized' 
        : 'institution';
      
      const uniqueInstitutions = [...new Set(coauthorData.map(d => d[institutionField]))]
        .filter(inst => inst != null && inst !== '' && inst !== 'Unknown')
        .slice(0, 8); // Limit to prevent overflow
      
      const colorScale = d3.scaleOrdinal(d3.schemeTableau10).domain(uniqueInstitutions);
      
      return uniqueInstitutions.map(inst => ({
        color: colorScale(inst),
        label: inst
      }));
    } else if (colorMode === 'shared_institutions' && coauthorData.length > 0) {
      // Get unique shared institutions from data
      const sharedField = coauthorData.some(d => d.shared_institutions_normalized) 
        ? 'shared_institutions_normalized' 
        : 'shared_institutions';
      
      const uniqueSharedInstitutions = [...new Set(coauthorData.map(d => d[sharedField]))]
        .filter(inst => inst != null && inst !== '' && inst !== 'Unknown')
        .slice(0, 8); // Limit to prevent overflow
      
      const colorScale = d3.scaleOrdinal(d3.schemeTableau10).domain(uniqueSharedInstitutions);
      
      return uniqueSharedInstitutions.map(inst => ({
        color: colorScale(inst),
        label: inst
      }));
    } else {
      return [
        { color: 'black', label: 'Coauthors' }
      ];
    }
  });
</script>

<div class="legend" class:visible>
  <div class="legend-content">
    <div class="legend-title">Legend</div>
    
    {#key colorMode}
      <div class="legend-items">
        {#each legendItems as item, i}
          <div 
            class="legend-item" 
            style="animation-delay: {i * 0.1}s"
          >
            <div 
              class="legend-dot" 
              style="background: {item.color};"
            ></div>
            <span>{item.label}</span>
          </div>
        {/each}
        

      </div>
    {/key}
  </div>
</div>

<style>
  .legend {
    background: var(--step-bg);
    border: 1px solid var(--color-border, #ddd);
    border-radius: 8px;
    padding: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    font-size: 11px;
    backdrop-filter: blur(10px);
    min-width: 180px;
    max-width: 220px;
    
    /* Transition properties */
    opacity: 0;
    transform: translateY(-10px);
    transition: opacity 0.6s ease, transform 0.6s ease;
  }

  .legend.visible {
    opacity: 1;
    transform: translateY(0);
  }

  .legend-content {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .legend-title {
    font-weight: bold;
    font-size: 12px;
    color: var(--color-text, var(--step-bg));
    margin-bottom: 4px;
    text-align: center;
    border-bottom: 1px solid var(--color-border, #eee);
    padding-bottom: 4px;
  }

  .legend-items {
    display: flex;
    flex-direction: column;
    gap: 6px;
    max-height: 300px;
    overflow-y: auto;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
    opacity: 0;
    transform: translateX(10px);
    animation: slideIn 0.4s ease forwards;
  }

  .legend-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    border: 1px solid rgba(0, 0, 0, 0.3);
    flex-shrink: 0;
    transition: background-color 0.4s ease;
  }

  .legend-item span {
    font-size: 10px;
    color: var(--color-text, var(--step-bg));
    line-height: 1.2;
    word-break: break-word;
  }

  @keyframes slideIn {
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
</style>