<script>
  import { Accordion } from "bits-ui";
  import { dashboardState } from '../../state.svelte.ts';
  import { UserCheck } from "@lucide/svelte";

  let { availableAuthors } = $props();
    
  // Extract author names from availableAuthors array
  let authorNames = $derived.by(() => {
    if (!availableAuthors || availableAuthors.length === 0) return [];
    // Handle both object format { name: "..." } and string format
    return availableAuthors.map(author => 
      typeof author === 'string' ? author : author.name || author["Faculty Name"] || author
    );
  });

  // Convert single selection to array for multiple select, and back
  let selectedAuthors = $derived.by(() => {
    return dashboardState.selectedAuthor ? [dashboardState.selectedAuthor] : [];
  });

  function handleSelectionChange(event) {
    const selected = Array.from(event.target.selectedOptions).map(option => option.value);
    // Only allow one selection - take the last one selected
    dashboardState.selectedAuthor = selected.length > 0 ? selected[selected.length - 1] : '';
  }
</script>

<!-- Author Selection Filter -->
<Accordion.Item value="author-select">
  <Accordion.Header>
    <Accordion.Trigger class="accordion-trigger">
      <UserCheck size={16} />
      Select Author
    </Accordion.Trigger>
  </Accordion.Header>
  <Accordion.Content class="accordion-content">
    <div class="control-section">
      <select 
        multiple 
        class="filter-select-multiple"
        onchange={handleSelectionChange}
        value={selectedAuthors}
      >
        {#each authorNames as authorName}
          <option value={authorName} selected={dashboardState.selectedAuthor === authorName}>
            {authorName}
          </option>
        {/each}
      </select>
      <p class="filter-info">Select an author to filter all data. Only one can be selected at a time.</p>
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

  .filter-select-multiple {
    padding: 0.5rem;
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    background: var(--color-bg);
    color: var(--color-fg);
    font-size: var(--font-size-smallish);
    width: 100%;
    height: 250px; /* Fixed height to show multiple options */
    font-family: var(--font-body);
  }

  .filter-select-multiple:focus {
    outline: none;
    border-color: var(--color-good-blue);
  }

  .filter-select-multiple option {
    padding: 0.2rem 0.5rem;
  }

  .filter-select-multiple option:checked {
    background: var(--color-good-blue);
    color: white;
  }

  .filter-info {
    font-size: var(--font-size-xsmall);
    color: var(--color-secondary-gray);
    margin: 0;
    font-style: italic;
    line-height: 1.3;
  }
</style>