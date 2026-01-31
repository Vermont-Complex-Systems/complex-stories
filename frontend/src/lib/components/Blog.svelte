<!-- src/lib/components/Blog.svelte -->
<script>
  import BlogPosts from "$lib/components/Blog.Posts.svelte";
  import FilterBar from "$lib/components/FilterBar.svelte";
  import HeroText from "$lib/components/HeroText.svelte";
  import { ChevronDown } from "@lucide/svelte";

  let { posts } = $props();

  const initMax = 6;
  let maxPosts = $state(initMax);
  let activeFilter = $state(undefined);

  function toSlug(tag) {
    return tag?.toLowerCase()?.replace(/[^a-z]/g, '_');
  }

  let allTags = $derived([...new Set(posts.flatMap((p) => p.tags))].sort());

  let filtered = $derived(
    activeFilter
      ? posts.filter((post) => post.tags.some((tag) => toSlug(tag) === activeFilter))
      : posts
  );

  let displayedPosts = $derived(filtered.slice(0, maxPosts));

  function onLoadMore() {
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
  <section class="blog-hero">
    <HeroText>
      <h1>Behind the Scenes</h1>
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

  .blog-hero {
    padding: 2rem var(--margin-left);
    text-align: center;
  }

  .blog-hero :global(h1) {
    font-family: var(--mono);
  }

  .blog-hero :global(h1)::after {
    content: '|';
    animation: blink 1s infinite;
    margin-left: 0.1em;
  }

  @keyframes blink {
    0%, 50% {
      opacity: 1;
    }
    51%, 100% {
      opacity: 0;
    }
  }

  .blog-hero :global(p) {
    font-family: var(--mono);
    max-width: var(--width-column-regular);
    margin-left: auto;
    margin-right: auto;
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
    .blog-hero {
      padding: 1rem var(--margin-left-mobile);
      text-align: center;
    }

    .load-more-btn {
      padding: 0.875rem 1.75rem;
      margin-bottom: 12%;
      font-size: var(--font-size-xsmall);
    }
  }
</style>