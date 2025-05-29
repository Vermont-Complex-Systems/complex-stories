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

<style>
  section {
    margin-top: 16px;
  }

  ul {
    padding: 0;
    display: grid;
    grid-template-columns: 1fr;
    gap: 48px 24px;
    margin: 0 auto;
    max-width: 1400px;
    padding: 0 24px;
  }

  li {
    margin: 0;
    list-style-type: none;
    padding: 0;
    --padding: clamp(20px, 3vw, 56px);
  }

  @media only screen and (min-width: 600px) {
    ul {
      grid-template-columns: repeat(2, 1fr);
      gap: 56px 32px;
    }
    
    li {
      --padding: clamp(24px, 4vw, 56px);
    }
  }

  @media only screen and (min-width: 960px) {
    ul {
      grid-template-columns: repeat(3, 1fr);
      gap: 64px 40px;
      max-width: 1600px;
    }
    
    li {
      --padding: clamp(32px, 5vw, 64px);
    }
  }
</style>