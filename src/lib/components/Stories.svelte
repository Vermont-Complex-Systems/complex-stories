<script>
  import Story from "$lib/components/Story.svelte";
  
  let { stories } = $props();
</script>

<section id="stories">
  <ul>
    {#each stories as story (story.slug)}
      <li>
        <Story {...story} />
      </li>
    {/each}
  </ul>
</section>

<!-- Keep your existing styles -->
<style>
  section {
    margin-top: 16px;
  }

  ul {
    padding: 0;
    display: flex;
    flex-wrap: wrap;
    margin: 0 auto;
  }

  li {
    margin: 0;
    list-style-type: none;
    padding: 32px 16px;
    width: 100%;
    --padding: clamp(16px, 12vw, 48px);
  }

  @media only screen and (min-width: 600px) {
    li {
      width: 50%;
      --padding: clamp(16px, 6vw, 48px);
    }
  }

  @media only screen and (min-width: 960px) {
    li {
      width: 33.3%;
      --padding: clamp(24px, 4vw, 56px);
    }
  }
</style>