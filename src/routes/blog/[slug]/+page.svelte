<!-- src/routes/blog/[slug]/+page.svelte -->
<script>
  import Meta from '$lib/components/Meta.svelte';
  import MarkdownRenderer from '$lib/components/helpers/MarkdownRenderer.svelte';
  import { base } from '$app/paths';
  import { ModeWatcher, setMode } from "mode-watcher";
  import { Sun, Moon } from "lucide-svelte";
  
  let { data } = $props();
  const { blog, content } = data;
  
  let isDark = $state(false);
  
  $effect(() => {
    isDark = document.documentElement.classList.contains('dark');
  });
  
  function toggleTheme() {
    isDark = !isDark;
    setMode(isDark ? 'dark' : 'light');
  }
</script>

<Meta 
  title={`${blog.title} - Complex Stories`}
  description={blog.excerpt || blog.tease || `Read ${blog.title} on Complex Stories blog`}
  keywords={blog.tags?.join(', ') || ''}
  author={blog.author?.join(', ') || 'Vermont Complex Systems Institute'}
/>

<ModeWatcher />

<!-- Floating theme toggle -->
<div class="floating-nav">
  <button onclick={toggleTheme} class="floating-theme-toggle">
    {#if isDark}
      <Sun class="icon" />
    {:else}
      <Moon class="icon" />
    {/if}
    <span class="sr-only">Toggle theme</span>
  </button>
</div>

<article class="blog-post">
    <header class="post-header column-regular">
    <!-- Back to Blog breadcrumb -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <a href="{base}/blog" class="back-link">← Back to Blog</a>
    </nav>
    
    <!-- Title -->
    <h1>{blog.title}</h1>
    
    <!-- Tease -->
    {#if blog.tease && blog.tease.trim()}
      <p class="post-tease">
        {blog.tease}
      </p>
    {/if}
    
    <!-- Meta -->
    <div class="post-meta">
      <time datetime={blog.date?.toISOString()}>
        {blog.month}
      </time>
      
      {#if blog.author?.length}
        <span class="authors">
          by {blog.author.join(', ')}
        </span>
      {/if}
      
      {#if blog.tags?.length}
        <div class="tags">
          {#each blog.tags as tag}
            <span class="tag">{tag}</span>
          {/each}
        </div>
      {/if}
    </div>
  </header>

  <div class="post-content column-regular">
    {#if blog.hasMarkdown}
      <MarkdownRenderer text={content} />
    {:else}
      <div class="html-content">
        {@html content}
      </div>
    {/if}
  </div>
</article>

<style>
  /* Floating navigation container */
  .floating-nav {
    position: fixed;
    top: 2.5rem;
    right: 2.5rem;
    z-index: var(--z-overlay);
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  /* Theme toggle */
  .floating-theme-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent !important;
    border: none !important;
    color: var(--color-fg) !important;
    text-transform: none !important;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 0.5rem;
    transition: all var(--transition-medium);
    width: 2.5rem;
    height: 2.5rem;
    box-shadow: none !important;
    flex-shrink: 0;
  }
  
  .floating-theme-toggle:hover {
    background: transparent !important;
    border: none !important;
    transform: rotate(var(--right-tilt)) scale(1.05);
    box-shadow: none !important;
    opacity: 0.7;
  }
  
  /* Breadcrumb */
  .breadcrumb {
    margin-bottom: 0.5rem;
  }

  .back-link {
    font-family: var(--mono);
    font-size: var(--font-size-small);
    text-transform: uppercase;
    color: var(--color-good-blue);
    text-decoration: none;
    transition: all var(--transition-medium);
    letter-spacing: 0.5px;
    display: inline-block;
  }

  .back-link:hover {
    color: var(--color-link-hover);
    transform: translateX(-2px);
  }

  /* Blog post layout */
  .blog-post {
    max-width: var(--width-column-wide);
    margin: 0 auto;
    padding: 2rem 1rem;
  }

  .post-header {
    margin-bottom: 3rem;
    text-align: left;
  }

  .post-header h1 {
    font-family: var(--sans);
    font-weight: var(--font-weight-bold);
    font-size: var(--font-size-giant);
    margin: 0 0 1rem 0;
    line-height: 1.1;
    text-transform: capitalize;
  }

  .post-tease {
    font-size: var(--font-size-medium);
    color: var(--color-secondary-gray);
    line-height: 1.4;
    margin: 0 0 2rem 0;
    font-weight: 300;
  }

  .post-meta {
    font-family: var(--mono);
    font-size: var(--font-size-small);
    color: var(--color-secondary-gray);
    text-transform: capitalize;
    letter-spacing: 0.5px;
  }

  .authors {
    margin-left: 1rem;
    text-transform: capitalize;
  }

  .tags {
    margin-top: 1rem;
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    gap: 0.5rem;
  }

  .tag {
    background: var(--color-input-bg);
    padding: 0.25rem 0.75rem;
    border-radius: var(--border-radius);
    font-size: var(--font-size-xsmall);
  }

  .post-content {
    margin-bottom: 3rem;
  }
  /* Mobile styles */
  @media (max-width: 768px) {
    .blog-post {
      padding: 2rem 0.5rem;
    }
    
    .post-header h1 {
      font-size: var(--font-size-giant);
    }

    .post-tease {
      font-size: var(--font-size-medium);
    }

    .floating-nav {
      top: 0.75rem;
      right: 0.75rem;
    }

    .back-link {
      font-size: 12px;
    }

  }
</style>