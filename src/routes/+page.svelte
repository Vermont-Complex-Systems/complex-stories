<script>
  import Stories from "$lib/components/Stories.svelte";
  
  let { data } = $props();
</script>

<div class="home">
  <header>
    <h1>Complex Stories</h1>
    <p>Interactive data stories that unfold as you scroll</p>
  </header>
  
  <Stories stories={data.summaries} />
</div>

<style>
  .home {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1rem;
  }

  header {
    text-align: center;
    margin-bottom: 3rem;
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