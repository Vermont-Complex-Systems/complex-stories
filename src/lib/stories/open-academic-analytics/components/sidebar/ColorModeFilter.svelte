<script>
  import { Accordion } from "bits-ui";
  import { dashboardState } from '../../state.svelte.ts';
</script>

<Accordion.Item value="color-mode">
  <Accordion.Header>
    <Accordion.Trigger class="accordion-trigger">
      🎨 Color Mode
    </Accordion.Trigger>
  </Accordion.Header>
  <Accordion.Content class="accordion-content">
    <div class="control-section">
      <label class="filter-label">
        Coauthor Coloring:
      </label>
      <select bind:value={dashboardState.colorMode} class="filter-select">
        <option value="age_diff">Age Difference</option>
        <option value="acquaintance">Acquaintance Type</option>
        <option value="institutions">Institutions</option>
        <option value="shared_institutions">Shared Institutions</option>
      </select>
      
      <div class="color-info">
        {#if dashboardState.colorMode === 'age_diff'}
          <p class="info-text">Colors based on age relative to main author</p>
        {:else if dashboardState.colorMode === 'institutions'} 
          <p class="info-text">Colors based on institutions.</p>
        {:else if dashboardState.colorMode === 'shared_institutions'} 
          <p class="info-text">Colors based on shared institutions.</p>
        {:else}
          <p class="info-text">Colors based on collaboration history</p>
        {/if}
      </div>
    </div>
  </Accordion.Content>
</Accordion.Item>

<style>
  :global(.accordion-trigger) {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    width: 100%;
    padding: 0.75rem;
    font-size: var(--font-size-small);
    font-weight: var(--font-weight-medium);
    color: var(--color-fg);
    background: transparent;
    border: none;
    border-radius: var(--border-radius);
    transition: background-color var(--transition-medium) ease;
    cursor: pointer;
  }

  :global(.accordion-trigger:hover) {
    background-color: var(--color-gray-100);
  }

  :global(.dark .accordion-trigger:hover) {
    background-color: var(--color-gray-800);
  }

  :global(.accordion-content) {
    padding: 0 0.75rem 1rem 0.75rem;
  }

  .control-section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .filter-label {
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
    font-size: var(--font-size-small);
    width: 100%;
  }

  .filter-select:focus {
    outline: none;
    border-color: var(--color-good-blue);
  }

  .color-info {
    margin-top: 0.5rem;
  }

  .info-text {
    font-size: var(--font-size-xsmall);
    color: var(--color-secondary-gray);
    margin: 0;
    font-style: italic;
  }
</style>