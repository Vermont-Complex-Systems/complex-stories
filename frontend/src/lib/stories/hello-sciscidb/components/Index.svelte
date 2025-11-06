<script>
    import Spinner from '$lib/components/helpers/Spinner.svelte'
    import { countData } from '$stories/hello-sciscidb/data.remote.js';
</script>

<h1>Hello scisciDB</h1>

{#await countData({start_year: 2000, end_year: 2005})}
    <div class="loading-container">
        <Spinner />
  </div>
{:then data} 
    {console.log(data)}
{/await}

<style>
    .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 50vh;
    gap: 1rem;
  }
</style>