<script>
  import Meta from "$lib/components/Meta.svelte";
  import Author from "$lib/components/Author.svelte";

  let { data } = $props();

  const { stories, author } = data;

  const copy = {
    title: author.name,
    description: "Author bio and published stories"
  };

  const preloadFont = [
    "https://vermont-complex-systems.github.io/VSCI-cool-website/assets/fonts/tiempos/TiemposTextWeb-Regular.woff2",
    "https://vermont-complex-systems.github.io/VSCI-cool-website/assets/fonts/tiempos/TiemposTextWeb-Bold.woff2",
    "https://vermont-complex-systems.github.io/VSCI-cool-website/assets/fonts/atlas/AtlasGrotesk-Regular-Web.woff2",
    "https://vermont-complex-systems.github.io/VSCI-cool-website/assets/fonts/atlas/AtlasGrotesk-Bold-Web.woff2",
    "https://vermont-complex-systems.github.io/VSCI-cool-website/assets/fonts/atlas/AtlasTypewriter-Medium-Web.woff2"
  ];
</script>

<Meta {copy} {preloadFont} />
<Author {stories} {author} />