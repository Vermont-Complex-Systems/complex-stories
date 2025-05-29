<script>
  import { descending } from "d3";
  import { getContext } from "svelte";
  import Stories from "$lib/components/Stories.svelte";
  import FilterBar from "$lib/components/FilterBar.svelte";
  import { ChevronDown } from "lucide-svelte";

  const initMax = 5;
  const { stories } = getContext("Home");
  const filters = ["Popular", "In Theory", "Dashboard"];

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

  // Slice the filtered results based on maxStories
  let displayedStories = $derived(filtered.slice(0, maxStories));

  function onLoadMore(e) {
    e.preventDefault();
    e.stopPropagation();
    maxStories = filtered.length; // Show all filtered stories
  }

  // Reset maxStories when filter changes
  $effect(() => {
    activeFilter; // Track activeFilter changes
    maxStories = initMax; // Reset to initial max when filter changes
  });
</script>

<FilterBar bind:activeFilter {filters} />

<div class="content">
  <div class="stories">
    <Stories stories={displayedStories} />
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

<style>
  .content {
    position: relative;
  }

  .more {
    display: none;
    height: 40vh;
    max-height: 400px;
    background: linear-gradient(transparent, rgba(254, 254, 254, 0.85));
    position: absolute;
    width: 100%;
    bottom: 0;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    z-index: 1000;
    pointer-events: none;
  }

  :global(.dark) .more {
    background: linear-gradient(transparent, rgba(26, 32, 44, 0.85));
  }

  .more.visible {
    display: flex;
  }

  .load-more-btn {
    transition: all 0.2s ease;
    margin-bottom: 15%;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 2rem;
    pointer-events: all;
    background: #2d3748; /* Dark in light mode */
    color: white;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 2rem;
    cursor: pointer;
    font-family: inherit;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    backdrop-filter: blur(12px);
    font-size: 0.95rem;
    white-space: nowrap; /* Keep text on single line */
    min-width: fit-content;
  }

  :global(.dark) .load-more-btn {
    background: rgba(255, 255, 255, 0.9); /* Light in dark mode */
    color: #2d3748;
    border-color: rgba(255, 255, 255, 0.2);
  }

  .load-more-btn:hover {
    transform: translateY(-2px);
    background: #1a202c;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  :global(.dark) .load-more-btn:hover {
    background: rgba(255, 255, 255, 0.95);
  }


  .text {
    font-weight: 600;
    letter-spacing: 0.25px;
    -webkit-font-smoothing: antialiased;
    flex-shrink: 0; /* Prevent text from wrapping */
  }

  @media (max-width: 768px) {
    .load-more-btn {
      padding: 0.875rem 1.75rem;
      margin-bottom: 12%;
      font-size: 0.875rem;
    }
    
  }
</style>