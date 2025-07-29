<!-- src/routes/blog/+page.svelte -->
<script>
  import Meta from "$lib/components/Meta.svelte";
  import Research from "$lib/components/Research.svelte";

  let { data } = $props();
  const { posts } = data;

</script>

<Meta 
  title="Blog - Complex Stories"
  description="Insights, tutorials, and thoughts on complex systems, data visualization, and the stories that emerge from data."
/>

<Research {posts} />