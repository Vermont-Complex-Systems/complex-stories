<script>
  import { getContext } from "svelte";
  import Stories from "$lib/components/Stories.svelte";

  const { stories } = getContext("Home");
</script>

<main>
  <div class="column-wide">
    <header>
      <h1>Scrollytelling Stories</h1>
      <p>Interactive data stories that unfold as you scroll</p>
    </header>
    
    <Stories {stories} />
  </div>
</main>

<style>
  main {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0;
  }

  .column-wide {
    max-width: 1280px;
    padding: 0 16px;
  }

  header {
    text-align: center;
    margin-bottom: 3rem;
    padding: 2rem 0;
  }

  h1 {
    font-size: clamp(2rem, 5vw, 3rem);
    margin: 0 0 1rem 0;
  }

  p {
    font-size: 1.2rem;
    color: #666;
    margin: 0;
  }
</style>