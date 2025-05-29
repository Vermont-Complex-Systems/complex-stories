<!-- src/routes/+page.svelte -->
<script>
  import CoauthorBubbleChart from './BubbleChart.svelte';
  import data from "../data/dodds_coauthors.csv";
</script>

<svelte:head>
  <title>Coauthor Collaboration Timeline</title>
</svelte:head>

<main>
  <h1>Coauthor Collaboration Analysis</h1>
  <CoauthorBubbleChart {data} />
</main>

<style>
  main {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  h1 {
    text-align: center;
    color: #333;
    margin-bottom: 2rem;
  }
</style>