<script>
  import { setContext } from "svelte";
  import Meta from "$lib/components/Meta.svelte";
  import Home from "$lib/components/Home.svelte";

  let { data } = $props();
  const { stories } = data;

  // Make stories available to Home component via context
  setContext("Home", { stories });
</script>

<Meta 
  title="Scrollytelling Stories"
  description="Interactive data stories that unfold as you scroll"
/>

<Home />