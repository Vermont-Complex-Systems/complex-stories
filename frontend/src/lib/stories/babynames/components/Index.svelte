<script>
    import { Allotaxonograph, Dashboard } from 'allotaxonometer-ui';
    import { getTopBabyNames } from '../data.remote.js';
    import YearSlider from './YearSlider.svelte';
    import LoadingSpinner from './LoadingSpinner.svelte';
    import * as d3 from 'd3';
	import Spinner from '$lib/components/helpers/Spinner.svelte';
	import { data } from '$lib/stories/open-academic-analytics/state.svelte.js';
    const alphas = d3.range(0,18).map(v => +(v/12).toFixed(2)).concat([1, 2, 5, Infinity]);

    // Non-reactive state - plain variables
    let period1 = [1950, 1959];
    let period2 = [1990, 1999];
    let alphaIndex = 7;
    let allotaxInstance = null;
    let isLoading = false;
    let error = null;

    // async function loadData() {
    //     try {
    //         isLoading = true;
    //         error = null;

    //         console.time('Total load data');

    //         console.time('API fetch');
    //         const data = await getTopBabyNames({
    //             dates: ["1950,1959", "1990,1999"],  // hardcoded instead of template literals
    //             locations: ["wikidata:Q30"]
    //         });
    //         console.timeEnd('API fetch');

    //         const keys = Object.keys(data);
    //         const elem1 = data[keys[0]];
    //         const elem2 = data[keys[1]];

    //         if (!elem1 || !elem2) {
    //             throw new Error('No data available for selected periods');
    //         }

    //         console.log('📊 Data size - elem1 keys:', Object.keys(elem1).length);
    //         console.log('📊 Data size - elem2 keys:', Object.keys(elem2).length);

    //         console.time('Allotaxonograph creation');
    //         allotaxInstance = new Allotaxonograph(elem1, elem2, {
    //             alpha: 0.58, // hardcoded instead of alphas[alphaIndex]
    //             title: ["1950-1959", "1990-1999"] // hardcoded instead of template literals
    //         });
    //         console.timeEnd('Allotaxonograph creation');

    //         console.time('State update');
    //         isLoading = false;
    //         console.timeEnd('State update');

    //         console.timeEnd('Total load data');

    //         // Check when the component actually renders
    //         requestAnimationFrame(() => {
    //             console.log('🎨 Component should be rendered now');
    //         });
    //     } catch (err) {
    //         console.error('Failed to load data:', err);
    //         error = err.message;
    //         isLoading = false;
    //     }
    // }

</script>


<div class="app-container">
    <div class="layout">
        <aside class="sidebar-container">
            <div class="sidebar-content">
                <div class="sidebar-header">
                    <h1>Baby Names</h1>
                    <p>Allotaxonometry Analysis</p>
                </div>

                <div class="controls-section">
                    <h3>Time Periods</h3>

                    <div class="year-controls">
                        <div class="static-display">
                            Period 1: {period1[0]}-{period1[1]}
                        </div>
                        <div class="static-display">
                            Period 2: {period2[0]}-{period2[1]}
                        </div>
                    </div>

                </div>

                <div class="controls-section">
                    <h3>Alpha Parameter</h3>
                    <div class="static-display">α = {alphas[alphaIndex]}</div>
                </div>
            </div>
        </aside>

        <main class="main-content">
            {#await getTopBabyNames({ dates: "1991", dates2: "1993" })}
                <LoadingSpinner />
            {:then ngrams} 
                {@const elem1 = ngrams['1991']}
                {@const elem2 = ngrams['1993']}
                {@const dat = new Allotaxonograph(elem1, elem2, {alpha: 0.58, title: ["1991", "1993"]})}    
                {console.log(dat.barData)}
            {/await}
        </main>
    </div>
</div>

<style>
    .app-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 10;
        overflow: hidden;
    }

    .layout {
        display: flex;
        height: 100vh;
        width: 100vw;
        margin: 0;
        padding: 0;
    }

    .sidebar-container {
        flex-shrink: 0;
        width: 20rem;
        background-color: var(--color-input-bg);
        border-right: 1px solid var(--color-border);
        overflow: hidden;
    }

    .sidebar-content {
        height: 100%;
        display: flex;
        flex-direction: column;
        padding: 1.5rem;
        gap: 2rem;
        overflow-y: auto;
    }

    .sidebar-header {
        padding: 1.5rem;
        border-bottom: 1px solid var(--color-border);
    }

    .sidebar-header h1 {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 0 0 0.5rem 0;
        color: var(--color-fg);
    }

    .sidebar-header p {
        font-size: 0.875rem;
        color: var(--color-secondary-gray);
        margin: 0;
    }

    .sidebar-content {
        flex: 1;
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }

    .controls-section {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .controls-section h3 {
        font-size: 1rem;
        font-weight: 600;
        margin: 0;
        color: var(--color-fg);
    }

    .year-controls {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .alpha-control {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .alpha-display {
        text-align: center;
        font-weight: 600;
        padding: 0.5rem;
        background-color: var(--color-bg);
        border-radius: 0.375rem;
        border: 1px solid var(--color-border);
    }

    .alpha-slider {
        width: 100%;
        height: 6px;
        background-color: var(--color-border);
        border-radius: 3px;
        outline: none;
        cursor: pointer;
        -webkit-appearance: none;
        appearance: none;
    }

    .alpha-slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 18px;
        height: 18px;
        background: var(--color-good-blue);
        border-radius: 50%;
        cursor: pointer;
    }

    .alpha-slider::-moz-range-thumb {
        width: 18px;
        height: 18px;
        background: var(--color-good-blue);
        border-radius: 50%;
        cursor: pointer;
        border: none;
    }

    .alpha-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: var(--color-secondary-gray);
    }

    .load-button {
        padding: 0.75rem 1rem;
        background-color: var(--color-good-blue);
        color: white;
        border: none;
        border-radius: 0.375rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 150ms ease;
    }

    .load-button:hover:not(:disabled) {
        background-color: var(--color-good-blue-hover);
    }

    .load-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .main-content {
        flex: 1;
        overflow: auto;
        background-color: var(--color-bg);
        max-width: none;
        margin: 0;
        padding: 5.5rem 0 0 0;
    }


    .navigation-arrows {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }

    .arrow-button {
        background: none;
        border: none;
        color: var(--color-fg);
        font-size: 0.75rem;
        cursor: pointer;
        padding: 0.125rem 0.25rem;
        transition: opacity 150ms ease;
        white-space: nowrap;
    }

    .arrow-button:hover:not(:disabled) {
        opacity: 0.7;
    }

    .arrow-button:disabled {
        opacity: 0.3;
        cursor: not-allowed;
    }

    .arrow-separator {
        color: var(--color-secondary-gray);
        font-size: 0.75rem;
    }
</style>