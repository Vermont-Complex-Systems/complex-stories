<script>
  let { 
    activeFilter = $bindable(undefined), 
    filters = [] 
  } = $props();

  function toggleFilter(filter) {
    const slug = filter?.toLowerCase()?.replace(/[^a-z]/g, "_");
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
          {@const slug = filter?.toLowerCase()?.replace(/[^a-z]/g, "_")}
          {@const active = slug === activeFilter}
          <button
            class:active
            onclick={() => toggleFilter(filter)}
          >
            {filter}
          </button>
        {/each}
      </div>

      <!-- Mobile filters -->
      <div class="filters--mobile">
        <select bind:value={activeFilter}>
          <option value={undefined}>All</option>
          {#each filters as filter}
            {@const slug = filter?.toLowerCase()?.replace(/[^a-z]/g, "_")}
            <option value={slug}>{filter}</option>
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
    /* Removed: border-bottom: 1px solid var(--color-border); */
    transition: all var(--transition-medium);
  }
  
  .filter-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 2rem;
    max-width: 100%;
    position: relative;
  }
  
  .spacer {
    width: 250px;
  }
  
  .filters-wrapper {
    display: flex;
    align-items: center;
    margin-right: 1.5rem;
  }

  /* Desktop filters */
  .filters--desktop {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .filters--desktop button {
    display: flex;
    align-items: center;
    background: none;
    padding: 0.5rem 1rem;
    border: 1px solid transparent;
    border-radius: var(--border-radius);
    text-transform: uppercase;
    font-size: var(--font-size-small);
    font-weight: var(--font-weight-bold);
    font-family: var(--mono);
    color: var(--color-secondary-gray);
    opacity: 0.6;
    transition: all var(--transition-medium);
    cursor: pointer;
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
    /* Your reset.css already handles select styling */
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
      padding: 0.5rem 1rem;
      justify-content: center;
    }
    
    .spacer {
      display: none;
    }
    
    .filters-wrapper {
      margin-right: 0;
    }
  }
</style>