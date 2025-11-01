<script>
  import { setContext } from "svelte";
  import Meta from "$lib/components/Meta.svelte";
  import Home from "$lib/components/Home.svelte";

  let { data } = $props();
  const { stories } = data;

  // Only preload fonts actually used above-the-fold on homepage
  const preloadFont = [
    "/assets/fonts/atlas/AtlasGrotesk-Regular-Web.woff2",
    "/assets/fonts/atlas/AtlasGrotesk-Bold-Web.woff2",
    "/assets/fonts/atlas/AtlasTypewriter-Medium-Web.woff2"
  ];

  // Make stories available to Home component via context
  setContext("Home", { stories });
</script>

<Meta 
  title="Complex Stories"
  description="Scientific data essays that uncover the challenges of computational science."
  {preloadFont}
/>

<Home />