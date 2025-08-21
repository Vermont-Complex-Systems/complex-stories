<script>
  import { dashboardState } from '../../state.svelte.ts';
</script>

<div class="color-mode-section">
  <div class="section-header">
    <span class="section-title">Paper Node Size</span>
  </div>
  
<select bind:value={dashboardState.paperNodeSize} class="filter-select">
    <option value="cited_by_count"># Citation</option>
    <option value="nb_coauthors"># Coauthors</option>
  </select>
  
  <div class="color-info">
    {#if dashboardState.paperNodeSize === 'cited_by_count'}
      <p class="info-text">Node size based on citation count</p>
    {:else}
      <p class="info-text">Node size based on number of coauthors.</p>
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