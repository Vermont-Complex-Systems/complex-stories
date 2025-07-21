<script>
  let { paperData = [], coauthorData = [], availableCoauthors = [] } = $props();
  
  // import { dataState } from '../../state.svelte.ts';
  
  // let selected_authors_group_url = $derived(dataState.trainingData[0]['group_url'])
  // let selected_authors_depts = $derived(Array.from(new Set(dataState.trainingData.map(d => d.host_dept))).join(", "))
</script>

<div class="data-info-section">
  <div class="section-header">
    <span class="section-icon">📈</span>
    <span class="section-title">Author Info</span>
  </div>
  
  <div class="data-stats">
    <div class="stat-row">
      <span class="stat-label"># Papers:</span>
      <span class="stat-value">{paperData?.length || 0}</span>
    </div>
    <div class="stat-row">
      <span class="stat-label">Total collaborations:</span>
      <span class="stat-value">{coauthorData?.length || 0}</span>
    </div>
    <div class="stat-row">
      <span class="stat-label">Unique Coauthors:</span>
      <span class="stat-value">{availableCoauthors.length}</span>
    </div>
    <!-- <div class="stat-row">
      <span class="stat-label">Departments:</span>
      <span class="stat-value-text">{selected_authors_depts}</span>
    </div>
    {#if selected_authors_group_url}
      <div class="stat-row">
        <span class="stat-label">Group URL:</span>
        <span class="stat-value-href"><a href={selected_authors_group_url}>{selected_authors_group_url}</a></span>
      </div>
    {/if} -->
  </div>
</div>

<style>
  .data-info-section {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .section-icon {
    font-size: var(--font-size-small);
  }

  .section-title {
    font-size: var(--font-size-small);
    font-weight: var(--font-weight-medium);
    color: var(--color-fg);
  }

  .data-stats {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 0.75rem;
    background: var(--color-gray-50);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
  }

  :global(.dark) .data-stats {
    background: var(--color-gray-800);
  }

  .stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: var(--font-size-xsmall);
  }

  .stat-label {
    color: var(--color-secondary-gray);
    font-weight: var(--font-weight-small);
  }

  .stat-value {
    color: var(--color-fg);
    font-weight: var(--font-weight-bold);
  }
  
  .stat-value-text {
    color: var(--color-fg);
    font-size: 10px;
  }
  
  .stat-value-href {
    color: var(--color-fg);
    font-size: 12px;
  }
</style>