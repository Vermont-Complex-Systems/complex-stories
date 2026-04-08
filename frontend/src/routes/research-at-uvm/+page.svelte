<!-- src/routes/research-at-uvm/+page.svelte -->
<script>
  import Meta from "$lib/components/Meta.svelte";
  import Research from "$lib/components/Research.svelte";

  import { getResearchGroups } from '$lib/research.remote';
</script>

<Meta
  title="Groups at UVM"
  description="Research groups at the University of Vermont."
/>

<svelte:boundary>
  <Research posts={await getResearchGroups()} />

  {#snippet pending()}
    <p class="loading">Loading research groups…</p>
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