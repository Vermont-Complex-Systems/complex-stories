<script>
  import { dashboardState } from '../state.svelte.js';
  import { Palette } from "@lucide/svelte";
</script>

<div class="color-mode-section">
  <div class="section-header">
    <Palette size={16} />
    <span class="section-title">Coauthor Node Color</span>
  </div>
  
  <select bind:value={dashboardState.coauthorNodeColor} class="filter-select">
    <option value="age_diff">Age Difference</option>
    <option value="acquaintance">Collaboration History</option>
    <option value="institutions">Institutions</option>
    <option value="shared_institutions">Shared Institutions</option>
  </select>
  
  <div class="color-info">
    {#if dashboardState.coauthorNodeColor === 'age_category'}
      <p class="info-text">Colors based on age relative to main author</p>
    {:else if dashboardState.coauthorNodeColor === 'institutions'} 
      <p class="info-text">Colors based on coauthor's institution</p>
    {:else if dashboardState.coauthorNodeColor === 'shared_institutions'} 
      <p class="info-text">Colors based on shared institutions</p>
    {:else}
      <p class="info-text">Colors based on collaboration history</p>
    {/if}
  </div>
</div>

<style>
  .color-mode-section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
  }

  .section-title {
    font-size: var(--font-size-small);
    font-weight: var(--font-weight-medium);
    color: var(--color-fg);
  }

  .filter-select {
    padding: 0.5rem;
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    background: var(--color-bg);
    color: var(--color-fg);
    font-size: var(--font-size-smallish);
    width: 100%;
  }

  .filter-select:focus {
    outline: none;
    border-color: var(--color-good-blue);
  }

  .color-info {
    margin-top: 0.25rem;
  }

  .info-text {
    font-size: var(--font-size-xsmall);
    color: var(--color-secondary-gray);
    margin: 0;
    font-style: italic;
  }
</style>