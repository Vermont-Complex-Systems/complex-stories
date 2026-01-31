<!-- src/routes/blog/+page.svelte -->
<script>
  import Meta from "$lib/components/Meta.svelte";
  import Research from "$lib/components/Research.svelte";

  import { getResearchGroups } from '$lib/research.remote';

  const posts = await getResearchGroups();

</script>

<Meta 
  title="Groups at UVM"
  description="Research groups at the University of Vermont."
/>

<Research {posts} />