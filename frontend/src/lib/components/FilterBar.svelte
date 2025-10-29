<script>
  let { 
    activeFilter = $bindable(undefined), 
    filters = [] 
  } = $props();

  // Helper function to convert filter to slug (DRY principle)
  function createSlug(filter) {
    return filter?.toLowerCase()?.replace(/[^a-z]/g, "_");
  }

  // Helper function to convert filter to display name
  function createDisplayName(filter) {
    return filter?.replace(/_/g, ' ');
  }

  function toggleFilter(filter) {
    const slug = createSlug(filter);
    activeFilter = slug === activeFilter ? undefined : slug;
  }
</script>

<div class="filter-bar">
  <div class="filter-content">
    <div class="spacer"></div>
    <div class="filters-wrapper">
      <!-- Desktop filters -->
      <div class="filters--desktop">
        {#each filters as filter, i}
          {@const slug = createSlug(filter)}
          {@const displayName = createDisplayName(filter)}
          {@const active = slug === activeFilter}
          <button
            class:active
            onclick={() => toggleFilter(filter)}
          >
            {displayName}
          </button>
        {/each}
      </div>

      <!-- Mobile filters -->
      <div class="filters--mobile">
        <select bind:value={activeFilter}>
          <option value={undefined}>All</option>
          {#each filters as filter}
            {@const slug = createSlug(filter)}
            {@const displayName = createDisplayName(filter)}
            <option value={slug}>{displayName}</option>
          {/each}
        </select>
      </div>
    </div>
  </div>
</div>

<style>
  .filter-bar {
    position: sticky;
    top: 0;
    z-index: calc(var(--z-overlay) - 100);
    width: 100%;
    background: var(--color-bg);
    transition: all var(--transition-medium);
  }
  
  .filter-content {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    padding: 0.5rem var(--margin-left);
    max-width: 100%;
    position: relative;
    box-sizing: border-box;
  }
  
  .spacer {
    display: none; /* No longer needed since we're using margin-left padding */
  }
  
  .filters-wrapper {
    display: flex;
    align-items: center;
  }

  /* Desktop filters */
  .filters--desktop {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .filters--desktop button {
    /* Reset button defaults first */
    border: none;
    background: none;
    padding: 0;
    cursor: pointer;
    font-family: inherit;
    
    /* Our button styling */
    display: flex;
    align-items: center;
    padding: 0.5rem 1rem;
    border: 1px solid transparent;
    border-radius: var(--border-radius);
    text-transform: uppercase;
    font-size: var(--font-size-xsmall);
    font-weight: var(--font-weight-bold);
    font-family: var(--mono);
    color: var(--color-secondary-gray);
    opacity: 0.6;
    transition: all var(--transition-medium);
  }

  .filters--desktop button:hover {
    opacity: 1;
    background: var(--color-input-bg);
  }

  .filters--desktop button.active {
    opacity: 1;
    color: var(--color-fg);
    background: var(--color-input-bg);
    border-color: var(--color-border);
  }

  /* Mobile filters */
  .filters--mobile {
    display: none;
  }

  .filters--mobile select {
    /* Ensure consistent styling with base.css */
    min-width: 8rem;
    font-family: var(--mono);
    font-size: var(--font-size-small);
    text-transform: uppercase;
    margin-top: 2.5rem;
  }

  /* Responsive */
  @media (max-width: 960px) {
    .filters--desktop {
      display: none;
    }

    .filters--mobile {
      display: block;
    }
  }
  
  @media (max-width: 768px) {
    .filter-content {
      justify-content: center;
      padding: 0.5rem var(--margin-left-mobile);
    }
    
    .spacer {
      display: none;
    }
    
    .filters-wrapper {
      margin-right: 0;
    }
  }
</style>