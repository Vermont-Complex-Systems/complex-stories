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

<!-- Floating navigation -->
<div class="floating-nav">
  <nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="{base}/" class="breadcrumb-link">Home</a>
    <span class="breadcrumb-separator">/</span>
    <a href="{base}/blog" class="breadcrumb-link">Blog</a>
  </nav>
  
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
    <h1>{blog.title}</h1>
    
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

  <footer class="post-footer column-regular">
    <a href="{base}/blog" class="back-link">← Back to Blog</a>
  </footer>
</article>

<style>
  /* Floating navigation container */
  .floating-nav {
    position: fixed;
    top: 2.5rem; /* Keep this the same */
    right: 2.5rem;
    z-index: var(--z-overlay);
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  /* Breadcrumb in floating position */
  .breadcrumb {
    font-family: var(--mono);
    font-size: var(--font-size-small);
    color: var(--color-secondary-gray);
    text-transform: uppercase;
    white-space: nowrap;
  }

  .breadcrumb-link {
    color: var(--color-link);
    text-decoration: none;
    transition: color var(--transition-medium);
  }

  .breadcrumb-link:hover {
    color: var(--color-link-hover);
  }

  .breadcrumb-separator {
    margin: 0 0.5rem;
    opacity: 0.6;
  }

  /* Theme toggle */
  .floating-theme-toggle {
    position: static; /* Changed since it's now in floating-nav */
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
    flex-shrink: 0; /* Prevent shrinking */
  }
  
  .floating-theme-toggle:hover {
    background: transparent !important;
    border: none !important;
    transform: rotate(var(--right-tilt)) scale(1.05);
    box-shadow: none !important;
    opacity: 0.7;
  }
  
  :global(.dark) .floating-theme-toggle {
    background: transparent !important;
    border: none !important;
    color: var(--color-fg) !important;
    box-shadow: none !important;
  }
  
  :global(.dark) .floating-theme-toggle:hover {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    opacity: 0.7;
  }

  /* YOUR EXISTING STYLES */
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

  .post-meta {
    font-family: var(--mono);
    font-size: var(--font-size-small);
    color: var(--color-secondary-gray);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .authors {
    margin-left: 1rem;
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

  .post-footer {
    text-align: center;
    border-top: 1px solid var(--color-border);
    padding-top: 2rem;
  }

  .back-link {
    font-family: var(--mono);
    font-size: var(--font-size-small);
    text-transform: uppercase;
    color: var(--color-link);
    text-decoration: underline;
  }

  .back-link:hover {
    color: var(--color-link-hover);
  }

  @media (max-width: 768px) {
    .blog-post {
      padding: 1rem 0.5rem;
    }
    
    .post-header h1 {
      font-size: var(--font-size-large);
    }

    .floating-nav {
      top: 0.75rem;
      right: 0.75rem;
      flex-direction: column;
      align-items: flex-end;
      gap: 0.5rem;
    }

    .breadcrumb {
      font-size: var(--font-size-xsmall);
    }
  }

  /* All your existing global styles unchanged */
  :global(.post-content blockquote) {
    border: none;
    margin: 2rem 0;
    padding: 0 0 0 1.5rem;
    background: none;
    font-size: 1.2em;
    line-height: 1.2;
    color: #2c5aa0;
    border-left: 3px solid #2c5aa0;
  }

  :global(.post-content blockquote p) {
    margin: 0;
  }

  :global(.dark .post-content blockquote) {
    color: #4a90e2;
    border-left-color: #4a90e2;
  }

  :global(.post-content) {
    font-family: "New York", "Times New Roman", Georgia, serif;
    font-size: 1.3rem;
    line-height: 1.2;
    color: var(--color-fg);
  }

  :global(.post-content p) {
    margin: 1.5rem 0;
    font-weight: 400;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  :global(.post-content ul) {
    margin: 1.5rem 0;
    padding-left: 1.5rem;
  }

  :global(.post-content li) {
    margin: 0.75rem 0;
    line-height: 1.2;
  }

  :global(.post-content ul ul li) {
    margin: 0.5rem 0;
  }

  :global(.post-content ol) {
    margin: 1.5rem 0;
    padding-left: 1.5rem;
  }

  :global(.post-content ol li) {
    margin: 0.75rem 0;
    line-height: 1.2;
  }
  
</style>