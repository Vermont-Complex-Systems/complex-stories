<!-- src/routes/blog/+page.svelte -->
<script>
  import Meta from "$lib/components/Meta.svelte";
  import Blog from "$lib/components/Blog.svelte";

  import { getBlogs } from '$lib/blog.remote';
</script>

<Meta
  title="Blog - Complex Stories"
  description="Insights, tutorials, and thoughts on complex systems, data visualization, and the stories that emerge from data."
/>

<svelte:boundary>
  <Blog posts={await getBlogs()} />

  {#snippet pending()}
    <p class="loading">Loading posts…</p>
  {/snippet}
</svelte:boundary>

<style>
  .loading {
    text-align: center;
    padding: 4rem 1rem;
    color: var(--color-secondary-gray);
    font-family: var(--sans);
  }
</style>