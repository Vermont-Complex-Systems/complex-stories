<script>
    import * as d3 from 'd3';
    import Spinner from '$lib/components/helpers/Spinner.svelte'
    import {  data, initializeApp } from './state.svelte.js';
    import { parseDate } from './combinedChartUtils.js'
    import PaperChart from './PaperChart.svelte';
    import { calculateChartHeight, calculateChartWidth } from './layout.js';
    import { innerWidth } from 'svelte/reactivity/window';

    let paperData = $derived(data.paper)
    
    // Initialize on component mount
    initializeApp();

    let width = $derived(
        calculateChartWidth(innerWidth.current, false)
    )

    const height = $derived(
        calculateChartHeight(1300)
    );

    // Create shared time scale for both charts
    let timeScale = $derived.by(() => {
        
        const dates = paperData.map(d => parseDate(d.pub_date));
        const [minDate, maxDate] = d3.extent(dates);
        
        const paddedMinDate = new Date(minDate.getFullYear() - 1, 0, 1);
        const paddedMaxDate = new Date(maxDate.getFullYear() + 1, 11, 31);
        return d3.scaleTime()
            .domain([paddedMinDate, paddedMaxDate])
            .range([50, height - 50]);
    });


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
    <h3>https://openalex.org/A5014570718</h3>
    <PaperChart {timeScale} {width} {height}/>
{/if}