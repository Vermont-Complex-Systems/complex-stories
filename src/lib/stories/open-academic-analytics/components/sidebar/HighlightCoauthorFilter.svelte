<script>
  import { Accordion } from "bits-ui";
  import { dashboardState } from '../../state.svelte.ts';

  let { coauthorData } = $props();

  // Available coauthors for highlighting
  let availableCoauthors = $derived.by(() => {
    if (!coauthorData || coauthorData.length === 0) return [];
    const coauthors = [...new Set(coauthorData.map(c => c.coauth_aid).filter(Boolean))];
    return coauthors.slice(0, 20); // Limit for UI
  });
</script>

<Accordion.Item value="highlight-coauthor">
  <Accordion.Header>
    <Accordion.Trigger class="accordion-trigger">
      👥 Highlight Coauthor
    </Accordion.Trigger>
  </Accordion.Header>
  <Accordion.Content class="accordion-content">
    <div class="control-section">
      <label class="filter-label">
        Select Coauthor to Highlight:
      </label>
      <select bind:value={dashboardState.highlightedCoauthor} class="filter-select">
        <option value={null}>None</option>
        {#each availableCoauthors as coauthor}
          <option value={coauthor}>{coauthor}</option>
        {/each}
      </select>
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
</style>