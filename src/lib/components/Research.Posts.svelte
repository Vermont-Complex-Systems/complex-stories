<!-- src/lib/components/Blog.Posts.svelte -->
<script>
  import { base } from "$app/paths";
  const imagePath = `${base}/common/thumbnails/snapshots`;
  let { posts } = $props();

</script>

<section class="blog-posts">
  {#if posts && posts.length > 0}
    <div class="posts-grid">
      {#each posts as post}
        <article class="post-card">

          <div class="screenshot">
            <img src="{imagePath}/{post.oa_uid}.jpg" loading="lazy" alt="Thumbnail for {post.slug}" />
          </div>
        
          <a href="{post.group_url}" class="post-link">
            <header class="post-header">
              <h3 class="post-title">
                {post.title || 'Untitled Post'}
              </h3>
              <div class="post-meta">
                <time datetime={post.date?.toISOString()}>
                  {post.month || 'No date'}
                </time>
                {#if post.author && post.author.length > 0}
                  <span class="author">by {post.author.join(', ')}</span>
                {/if}
              </div>
            </header>
            

            {#if post.tags && post.tags.length > 0}
              <div class="post-tags">
                {#each post.tags.slice(0, 3) as tag}
                  <span class="tag">{tag}</span>
                {/each}
              </div>
            {/if}
          </a>
        </article>
      {/each}
    </div>
  {:else}
    <div class="no-posts">
      <p>No blog posts found.</p>
    </div>
  {/if}
</section>

<style>
  .blog-posts {
    margin: 2rem 0;
  }

  .posts-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
    max-width: var(--width-column-wide);
    margin: 0 auto;
    padding: 0 1rem;
  }

  @media (min-width: 768px) {
    .posts-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (min-width: 1200px) {
    .posts-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  .post-card {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    overflow: hidden;
    transition: all var(--transition-medium);
    min-height: 250px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  }

  .post-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    background: rgba(255, 255, 255, 0.9);
  }

  :global(.dark) .post-card {
    background: rgba(30, 30, 30, 0.8);
    border-color: rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  }

  :global(.dark) .post-card:hover {
    background: rgba(40, 40, 40, 0.9);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  }

  .post-link {
    display: block;
    padding: 1.5rem;
    text-decoration: none;
    color: inherit;
    height: 100%;
    min-height: 200px;
  }

  .post-title {
    font-family: var(--sans);
    font-weight: var(--font-weight-bold);
    font-size: var(--font-size-medium);
    margin: 0 0 0.5rem 0;
    line-height: 1.2;
    color: var(--color-fg);
  }

  .post-meta {
    font-family: var(--mono);
    font-size: var(--font-size-xsmall);
    color: var(--color-secondary-gray);
    text-transform: uppercase;
    margin-bottom: 1rem;
  }

  .author {
    margin-left: 0.5rem;
  }

  .post-excerpt p {
    color: var(--color-secondary-gray);
    margin: 0;
    line-height: 1.5;
    font-size: var(--font-size-small);
  }

  .post-tags {
    margin-top: 1rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .tag {
    background: rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 0.25rem 0.5rem;
    border-radius: calc(var(--border-radius) / 2);
    font-size: var(--font-size-xsmall);
    font-family: var(--mono);
    text-transform: uppercase;
    color: var(--color-fg);
    transition: all var(--transition-fast);
  }

  .tag:hover {
    background: rgba(255, 255, 255, 0.4);
  }

  :global(.dark) .tag {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.1);
  }

  :global(.dark) .tag:hover {
    background: rgba(255, 255, 255, 0.15);
  }

  .no-posts {
    text-align: center;
    padding: 2rem;
    color: var(--color-secondary-gray);
  }
</style>