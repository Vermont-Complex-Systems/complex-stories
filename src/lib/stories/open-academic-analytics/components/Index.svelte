<script>
    import * as d3 from 'd3';
    import Spinner from '$lib/components/helpers/Spinner.svelte'
    import {  data, initializeApp } from './state.svelte.js';
    import Dashboard from './Dashboard.svelte';
    
    // Initialize on component mount
    initializeApp();
</script>

{#if data.isInitializing}
    <div class="loading-container">
        <Spinner />
    </div>
{:else if data.error}
    <div class="error-container">
        <p>Error: {data.error}</p>
            <button onclick={() => initializeApp()}>Retry</button>
        </div>
{:else}
    <Dashboard />
{/if}