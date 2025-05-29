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
    gap: 32px 16px; /* 32px vertical, 16px horizontal gap */
    margin: 0 auto;
    max-width: 1200px; /* Optional: constrain max width */
  }

  li {
    margin: 0;
    list-style-type: none;
    padding: 0 16px; /* Only horizontal padding now */
    --padding: clamp(16px, 12vw, 48px);
  }

  @media only screen and (min-width: 600px) {
    ul {
      grid-template-columns: repeat(2, 1fr);
    }
    
    li {
      --padding: clamp(16px, 6vw, 48px);
    }
  }

  @media only screen and (min-width: 960px) {
    ul {
      grid-template-columns: repeat(3, 1fr);
    }
    
    li {
      --padding: clamp(24px, 4vw, 56px);
    }
  }
</style>