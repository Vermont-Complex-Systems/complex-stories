<!-- src/routes/blog/+page.svelte -->
<script>
  import Meta from "$lib/components/Meta.svelte";
  import Research from "$lib/components/Research.svelte";

  let../../research-at-uvm/$types.js { data } = $props();
  const { posts } = data;

</script>

<Meta 
  title="Groups at UVM"
  description="Research groups at the University of Vermont."
/>

<Research {posts} />