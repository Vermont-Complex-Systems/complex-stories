<script>
  import Meta from "$lib/components/Meta.svelte";
  import Home from "$lib/components/Home.svelte";

</script>

<Meta
  title="Complex Stories"
  description="Scientific data essays that uncover the challenges of computational science."
/>

<svelte:boundary>
  <Home />

  {#snippet pending()}
    <p class="loading">Loading stories…</p>
  {/snippet}
</svelte:boundary>

<style>
  .loading {
    text-align: center;
    padding: 4rem 1rem;
    color: var(--color-secondary-gray);
    font-family: var(--sans);
  }
</style>