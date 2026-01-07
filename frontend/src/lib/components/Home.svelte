<script>
  import { descending } from "d3";
  import { getContext } from "svelte";
  import Stories from "$lib/components/Stories.svelte";
  import FilterBar from "$lib/components/FilterBar.svelte";
  import { ChevronDown } from "@lucide/svelte";

  const { stories } = getContext("Home");

  const initMax = 6;

  let maxStories = $state(initMax);
  let activeFilter = $state(undefined);

  // Extract unique filters from all stories
  let allFilters = $derived.by(() => {
    const filterSet = new Set();
    stories.forEach(story => {
      if (story.filters && Array.isArray(story.filters)) {
        story.filters.forEach(filter => filterSet.add(filter));
      }
    });
    return Array.from(filterSet).sort();
  });

  
  let filtered = $derived.by(() => {
    const f = stories.filter((d) => {
      
      // Simplified: if no active filter, show all; otherwise check if story has the filter
      return !activeFilter || d.filters.includes(activeFilter);
    });
    f.sort((a, b) => descending(a.id, b.id));
    // hide stories like that for now
    return f.filter(d => d.slug !== 'interdisciplinarity' && d.slug !== 'dark-data-survey') ;
  });

  
  let displayedStories = $derived(filtered.slice(0, maxStories));

  function onLoadMore(e) {
    e.preventDefault();
    e.stopPropagation();
    maxStories = filtered.length;
  }

  // Reset pagination when filter changes
  $effect(() => {
    activeFilter; // Track the dependency
    maxStories = initMax;
  });
</script>

<div class="content">
  <FilterBar bind:activeFilter filters={allFilters} />
  
  <div class="stories">
    <Stories stories={displayedStories} />
  </div>

  {#if filtered.length > maxStories}
    <div class="more">
      <button onclick={onLoadMore} class="load-more-btn">
        <ChevronDown class="chevron" size={20} />
        <span class="text">Load More Stories</span>
      </button>
    </div>
  {/if}
</div>

<style>
  
  :global(main:has(.content)) {
    max-width: none;
    padding: 0 !important;
  }

  .content {
    position: relative;
    padding-bottom: 8rem; 
  }

  .stories {
    margin-top: 0;
  }

  .more {
    height: 30vh;
    max-height: 300px;
    background: var(--fade);
    position: absolute;
    width: 100%;
    bottom: 0;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    z-index: var(--z-overlay);
    pointer-events: none;
  }

  .load-more-btn {
    /* Reset button defaults first */
    border: none;
    background: none;
    padding: 0;
    cursor: pointer;
    font-family: inherit;
    
    /* Our button styling */
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 2rem;
    margin-bottom: 2rem; /* Fixed spacing instead of percentage */
    background: var(--color-button-bg);
    color: var(--color-button-fg);
    border: 1px solid var(--color-border);
    border-radius: 2rem;
    font-family: var(--font-form);
    font-size: var(--font-size-small);
    font-weight: var(--font-weight-bold);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
    min-width: fit-content;
    transition: transform var(--transition-medium) ease;
    pointer-events: all;
    
    /* Ensure good touch target size */
    min-height: 44px; /* iOS recommended minimum */
  }

  .load-more-btn:hover {
    transform: translateY(-2px);
    background: var(--color-button-hover);
  }

  .text {
    flex-shrink: 0;
  }

  /* Mobile improvements */
  @media (max-width: 768px) {
    .more {
      height: 25vh; /* Shorter on mobile */
      max-height: 200px; /* Less intrusive */
    }
    
    .load-more-btn {
      padding: 1.125rem 2.25rem; /* LARGER on mobile, not smaller */
      margin-bottom: 1.5rem; /* Safer distance from bottom */
      font-size: var(--font-size-small); /* Keep readable size */
      min-height: 48px; /* Even better touch target */
    }
  }

  /* Very small screens */
  @media (max-width: 480px) {
    .more {
      height: 20vh;
      max-height: 150px;
    }
    
    .load-more-btn {
      padding: 1rem 1.75rem; /* Slightly smaller to fit */
      font-size: var(--font-size-xsmall);
      gap: 0.375rem; /* Tighter gap */
    }
  }
</style>