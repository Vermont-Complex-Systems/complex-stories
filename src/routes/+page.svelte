<script>
  import { setContext } from "svelte";
  import version from "$lib/utils/version.js";
  import Home from "$lib/components/Home.svelte";
  let { data } = $props();

  const { summaries } = data;

  version();

  setContext("Home", { stories: summaries });
</script>

<Home />