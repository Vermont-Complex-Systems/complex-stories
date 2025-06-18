<!-- src/routes/blog/+page.svelte -->
<script>
  import Meta from "$lib/components/Meta.svelte";
  import Blog from "$lib/components/Blog.svelte";

  let { data } = $props();
  const { posts } = data;

  const copy = {
    title: "Blog - Complex Stories",
    description: "Insights, tutorials, and thoughts on complex systems, data visualization, and the stories that emerge from data."
  };
</script>

<Meta 
  title={copy.title}
  description={copy.description}
/>

<Blog {posts} />