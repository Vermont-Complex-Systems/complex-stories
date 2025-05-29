<script>
  import { descending } from "d3";
  import { getContext } from "svelte";
  import Stories from "$lib/components/Stories.svelte";
  import { ChevronDown } from "lucide-svelte";

  const initMax = 5;
  const { stories } = getContext("Home");

  let maxStories = $state(initMax);
  let activeFilter = $state(undefined);

  let filtered = $derived.by(() => {
    const f = stories.filter((d) => {
      const inFilter = activeFilter ? d.filters.includes(activeFilter) : true;
      return inFilter;
    });
    f.sort((a, b) => descending(a.id, b.id));
    return f;
  });

  let displayedStories = $derived(filtered.slice(0, maxStories));

  function onLoadMore(e) {
    e.preventDefault();
    e.stopPropagation();
    maxStories = filtered.length;
  }

  function handleFilterClick(filter) {
    // Toggle filter - if same filter clicked, clear it
    activeFilter = activeFilter === filter ? undefined : filter;
    maxStories = initMax; // Reset pagination when filter changes
  }

  $effect(() => {
    activeFilter;
    maxStories = initMax;
  });
</script>

<div class="content">
  <div class="stories">
    <Stories stories={displayedStories} {activeFilter} onFilterClick={handleFilterClick} />
  </div>

  {#if filtered.length > maxStories}
    <div class="more" class:visible={filtered.length > maxStories}>
      <button onclick={onLoadMore} class="load-more-btn">
        <ChevronDown class="chevron" />
        <span class="text">Load More Stories</span>
      </button>
    </div>
  {/if}
</div>

<!-- Keep your existing styles for .content, .more, .load-more-btn -->
<style>
  .content {
    position: relative;
  }

  .more {
    display: none;
    height: 40vh;
    max-height: 400px;
    background: var(--fade);
    position: absolute;
    width: 100%;
    bottom: 0;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    z-index: var(--z-overlay);
    pointer-events: none;
  }

  .more.visible {
    display: flex;
  }

  .load-more-btn {
    transition: transform var(--transition-medium) ease;
    margin-bottom: 15%;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 2rem;
    pointer-events: all;
    background: var(--color-button-bg);
    color: var(--color-button-fg);
    border: 1px solid var(--color-border);
    border-radius: 2rem;
    cursor: pointer;
    font-family: var(--font-form);
    font-size: var(--font-size-small);
    white-space: nowrap;
    min-width: fit-content;
    text-transform: uppercase;
    font-weight: var(--font-weight-bold);
    letter-spacing: 0.5px;
  }

  .load-more-btn:hover {
    transform: translateY(-2px);
    background: var(--color-button-hover);
  }

  .chevron {
    width: 1.125rem;
    height: 1.125rem;
    stroke-width: 2;
    flex-shrink: 0;
  }

  .text {
    flex-shrink: 0;
  }

  @media (max-width: 768px) {
    .load-more-btn {
      padding: 0.875rem 1.75rem;
      margin-bottom: 12%;
      font-size: var(--font-size-xsmall);
    }
    
    .chevron {
      width: 1rem;
      height: 1rem;
    }
  }
</style>