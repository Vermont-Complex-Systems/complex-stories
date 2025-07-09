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
    margin-top: 1rem; /* Use rem instead of hardcoded 16px */
  }

  ul {
    padding: 0;
    display: grid;
    grid-template-columns: 1fr;
    gap: 3rem 1.5rem; /* Convert px to rem: 48px = 3rem, 24px = 1.5rem */
    margin: 0 auto;
    max-width: 1400px;
    padding: 0 1.5rem; /* Convert 24px to rem */
  }

  li {
    margin: 0;
    list-style-type: none;
    padding: 0;
    --padding: clamp(1.25rem, 3vw, 3.5rem); /* Convert px to rem: 20px=1.25rem, 56px=3.5rem */
  }

  @media only screen and (min-width: 600px) {
    ul {
      grid-template-columns: repeat(2, 1fr);
      gap: 3.5rem 2rem; /* Convert 56px 32px to rem */
    }
    
    li {
      --padding: clamp(1.5rem, 4vw, 3.5rem); /* Convert 24px 56px to rem */
    }
  }

  @media only screen and (min-width: 960px) {
    ul {
      grid-template-columns: repeat(3, 1fr);
      gap: 4rem 2.5rem; /* Convert 64px 40px to rem */
      max-width: 1600px;
    }
    
    li {
      --padding: clamp(2rem, 5vw, 4rem); /* Convert 32px 64px to rem */
    }
  }
</style>