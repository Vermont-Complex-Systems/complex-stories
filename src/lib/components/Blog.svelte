<!-- src/lib/components/Blog.svelte -->
<script>
  import { descending } from "d3";
  import BlogPosts from "$lib/components/Blog.Posts.svelte";
  import FilterBar from "$lib/components/FilterBar.svelte";
  import HeroText from "$lib/components/HeroText.svelte";
  import { ChevronDown } from "lucide-svelte";

  let { posts } = $props();

  const initMax = 6; // Show 6 blog posts initially
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
      const inFilter = activeFilter ? 
        post.tags?.includes(activeFilter.replace(/_/g, ' ')) : true;
      return inFilter;
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
  <!-- Hero section -->
  <section class="blog-hero column-wide">
    <HeroText>
      <h1>Blog</h1>
      <p>
        Insights, tutorials, and thoughts on complex systems, data visualization, 
        and the stories that emerge from data.
      </p>
    </HeroText>
  </section>

  <!-- Filter bar -->
  <FilterBar bind:activeFilter filters={allTags} />

  <!-- Blog posts -->
  <div class="blog-content">
    <BlogPosts posts={displayedPosts} />
  </div>

  <!-- Load more button -->
  {#if filtered.length > maxPosts}
    <div class="more" class:visible={filtered.length > maxPosts}>
      <button onclick={onLoadMore} class="load-more-btn">
        <ChevronDown class="chevron" />
        <span class="text">Load More Posts</span>
      </button>
    </div>
  {/if}
</div>

<style>
  .blog-container {
    position: relative;
    min-height: 100vh;
  }

  .blog-hero {
    padding: 2rem 0;
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

  .text {
    flex-shrink: 0;
  }

  @media (max-width: 768px) {
    .blog-hero {
      padding: 1rem 0;
    }

    .load-more-btn {
      padding: 0.875rem 1.75rem;
      margin-bottom: 12%;
      font-size: var(--font-size-xsmall);
    }
  }
</style>