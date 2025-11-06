<script>
  import { dashboardState, unique } from '$stories/open-academic-analytics/state.svelte.js';
  import { UserCheck } from "@lucide/svelte";

  // Use centralized filtered authors from state
  let filteredAuthors = $derived(unique.filteredAuthors);
    
  // Extract author names from filtered authors
  let authorNames = $derived.by(() => {
    if (!filteredAuthors || filteredAuthors.length === 0) return [];
    return filteredAuthors.map(author => author.ego_display_name);
  });

  function handleSelectionChange(event) {
    const selected = Array.from(event.target.selectedOptions).map(option => option.value);
    // Only allow one selection - take the last one selected
    dashboardState.selectedAuthor = selected.length > 0 ? selected[selected.length - 1] : '';
  }

  // Show filter status
  let filterStatus = $derived.by(() => {
    if (!dashboardState.authorAgeFilter) return '';
    const total = unique.authors.length;
    const filtered = filteredAuthors.length;
    return `(${filtered} of ${total} authors)`;
  });
</script>

<!-- Author Selection Filter -->
<div class="widget-container">
  <div class="widget-header">
    <UserCheck size={16} />
    <span class="widget-title">Select Author {filterStatus}</span>
  </div>
    <div class="control-section">
      <select 
        multiple 
        class="filter-select-multiple"
        onchange={handleSelectionChange}
        value={dashboardState.selectedAuthor}
      >
        {#each authorNames as authorName}
          <option value={authorName} selected={dashboardState.selectedAuthor === authorName}>
            {authorName}
          </option>
        {/each}
      </select>
    </div>
</div>

<style>
  .widget-container {
    margin-bottom: 1.5rem;
  }

  .widget-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
    padding-bottom: 0.25rem;
    border-bottom: 1px solid var(--color-border);
  }

  .widget-title {
    font-size: var(--font-size-xsmall);
    font-weight: var(--font-weight-medium);
    color: var(--color-fg);
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