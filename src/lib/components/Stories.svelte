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
    gap: 48px 24px; /* Increased gap: 48px vertical, 24px horizontal */
    margin: 0 auto;
    max-width: 1400px; /* Increased from 1200px to give more room */
    padding: 0 24px; /* Add horizontal padding */
  }

  li {
    margin: 0;
    list-style-type: none;
    padding: 0; /* Remove padding since gap handles spacing */
    --padding: clamp(20px, 3vw, 56px); /* Increased base padding */
  }

  @media only screen and (min-width: 600px) {
    ul {
      grid-template-columns: repeat(2, 1fr);
      gap: 56px 32px; /* Bigger gaps on tablet */
    }
    
    li {
      --padding: clamp(24px, 4vw, 56px);
    }
  }

  @media only screen and (min-width: 960px) {
    ul {
      grid-template-columns: repeat(3, 1fr);
      gap: 64px 40px; /* Even bigger gaps on desktop */
      max-width: 1600px; /* Even more room on desktop */
    }
    
    li {
      --padding: clamp(32px, 5vw, 64px); /* Increased desktop padding */
    }
  }
</style>