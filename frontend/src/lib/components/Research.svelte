<!-- src/lib/components/Blog.svelte -->
<script>
  import { descending } from "d3";
  import ResearchPosts from "$lib/components/Research.Posts.svelte";
  import FilterBar from "$lib/components/FilterBar.svelte";
  import { ChevronDown } from "@lucide/svelte";

  let { posts } = $props();

  const initMax = 27;
  let maxPosts = $state(initMax);
  let activeFilter = $state(undefined);

  // Extract unique tags from all posts for filtering
  let allTags = $derived.by(() => {
    const tagSet = new Set();
    posts.forEach(post => {
      if (post.tags && Array.isArray(post.tags)) {
        post.tags.forEach(tag => tagSet.add(tag));
      }
    });
    return Array.from(tagSet).sort();
  });

  let filtered = $derived.by(() => {
    const f = posts.filter((post) => {
      if (!activeFilter) return true;
      
      // Convert post tags to slugs and check if any match the active filter
      return post.tags?.some(tag => {
        const tagSlug = tag?.toLowerCase()?.replace(/[^a-z]/g, "_");
        return tagSlug === activeFilter;
      }) || false;
    });
    f.sort((a, b) => descending(a.date, b.date)); // Most recent first
    return f;
  });

  let displayedPosts = $derived(filtered.slice(0, maxPosts));

  function onLoadMore(e) {
    e.preventDefault();
    e.stopPropagation();
    maxPosts = filtered.length;
  }

  // Reset pagination when filter changes
  $effect(() => {
    activeFilter;
    maxPosts = initMax;
  });
</script>

<div class="blog-container">
  <!-- Header section -->
  <section class="research-header">
    <h1>Research groups at UVM</h1>
    <p class="research-description">
      What groups are there at the University of Vermont?
    </p>
  </section>

  <!-- Filter bar -->
  <FilterBar bind:activeFilter filters={allTags} />

  <!-- Blog posts -->
  <div class="blog-content">
    <ResearchPosts posts={displayedPosts} />
  </div>

  <!-- Load more button -->
  {#if filtered.length > maxPosts}
    <div class="more" class:visible={filtered.length > maxPosts}>
      <button onclick={onLoadMore} class="load-more-btn">
        <ChevronDown class="chevron" size={20} />
        <span class="text">Load More Posts</span>
      </button>
    </div>
  {/if}
</div>

<style>
  /* Override main element constraints for full-width layout */
  :global(main#content:has(.blog-container)) {
    max-width: none;
    padding: 0 !important; /* Remove default padding to let column-screen handle spacing */
  }

  .blog-container {
    position: relative;
    min-height: 100vh;
  }

  .research-header {
    padding: 7rem var(--margin-left) 0.5rem var(--margin-left);
    text-align: left;
  }

  .research-header h1 {
    font-family: var(--mono);
    font-size: clamp(1.5rem, 3vw, 2rem);
    font-weight: var(--font-weight-bold);
    color: var(--color-fg);
    margin: 0 0 1rem 0;
  }

  .research-description {
    font-family: var(--mono);
    font-size: var(--font-size-medium);
    color: var(--color-secondary-gray);
    margin-bottom: 1.5rem;
    line-height: 1.6;
  }


  .blog-content {
    margin-top: 0;
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
    /* Reset button defaults first */
    border: none;
    background: none;
    padding: 0;
    cursor: pointer;
    font-family: inherit;
    
    /* Apply our styling */
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

  .text {
    flex-shrink: 0;
  }

  @media (max-width: 768px) {
    .research-header {
      padding: 1.5rem var(--margin-left-mobile);
      text-align: left;
    }

    .load-more-btn {
      padding: 0.875rem 1.75rem;
      margin-bottom: 12%;
      font-size: var(--font-size-xsmall);
    }
  }
</style>