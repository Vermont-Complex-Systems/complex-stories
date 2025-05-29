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
    <div class="spacer"></div> <!-- Left spacer for balance -->
    <div class="filters-wrapper">
      <!-- Desktop filters -->
      <div class="filters--desktop">
        {#each filters as filter, i}
          {@const slug = filter?.toLowerCase()?.replace(/[^a-z]/g, "_")}
          {@const active = slug === activeFilter} <!-- Fixed this line -->
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
    z-index: 45;
    width: 100%;
    background: #fefefe;
    border-bottom: 1px solid rgba(226, 232, 240, 0.3);
    transition: all 0.2s;
  }
  
  :global(.dark) .filter-bar {
    background: #1a202c;
    border-bottom-color: rgba(74, 85, 104, 0.3);
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
    border-radius: 0.375rem;
    text-transform: uppercase;
    font-size: 0.875rem;
    font-weight: 600;
    font-family: monospace;
    color: #718096;
    opacity: 0.6;
    transition: all 0.2s;
    cursor: pointer;
  }

  .filters--desktop button:hover {
    opacity: 1;
    background: rgba(226, 232, 240, 0.5);
  }

  .filters--desktop button.active {
    opacity: 1;
    color: #2d3748;
    background: rgba(226, 232, 240, 0.8);
    border-color: #cbd5e0;
  }

  :global(.dark) .filters--desktop button {
    color: #a0aec0;
  }

  :global(.dark) .filters--desktop button:hover {
    background: rgba(74, 85, 104, 0.5);
  }

  :global(.dark) .filters--desktop button.active {
    color: #e2e8f0;
    background: rgba(74, 85, 104, 0.8);
    border-color: #718096;
  }

  /* Mobile filters */
  .filters--mobile {
    display: none;
  }

  .filters--mobile select {
    border: 1px solid #e2e8f0;
    background-color: white;
    color: #4a5568;
    border-radius: 6px;
    font-size: 0.875rem;
    padding: 8px 12px;
    cursor: pointer;
  }

  :global(.dark) .filters--mobile select {
    border-color: #4a5568;
    background-color: #2d3748;
    color: #e2e8f0;
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