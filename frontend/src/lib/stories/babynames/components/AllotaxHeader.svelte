<script>
    import { page } from '$app/stores';
    import HelpPopover from './HelpPopover.svelte';
    import { createQuery } from '@tanstack/svelte-query';
    
    let {
        country1,
        country2,
        date1,
        date2,
        topN,
        alphaIndex,
        alphas,
        currentAlpha,
        comparisonMode,
        topNgramsQuery,
        params
    } = $props();


    const countries = [
        'United States',
        'United Kingdom',
        'Canada',
        'Australia',
        'Denmark',
        'Germany',
        'France'
    ];

    const isAllotaxRoute = $derived($page.url.pathname.startsWith('/allotax'));
    const isFetching = $derived(topNgramsQuery?.isFetching || false);

    // Local state for debounced inputs
    let localDate1 = $state(1900);
    let localDate2 = $state(2020);
    let localTopN = $state(topN);
    
    // Debounce timeouts
    let date1Timeout;
    let date2Timeout;
    let topNTimeout;

    // Initialize local values when props change externally
    $effect(() => {
        localDate1 = date1;
    });

    $effect(() => {
        localDate2 = date2;
    });

    $effect(() => {
        localTopN = topN;
    });

    // Watch for changes to localDate1 and update params with debounce
    $effect(() => {
        // Skip if localDate1 is the same as date1 (from prop initialization)
        if (localDate1 === date1) return;

        if (date1Timeout) clearTimeout(date1Timeout);
        date1Timeout = setTimeout(() => {
            // Only update if date is valid
            if (localDate1) {
                params.set('date', `${localDate1.year}-${String(localDate1.month).padStart(2, '0')}-${String(localDate1.day).padStart(2, '0')}`);
            }
        }, 1000);
    });

    // Watch for changes to localDate2 and update params with debounce
    $effect(() => {
        // Skip if localDate2 is the same as date2 (from prop initialization)
        if (localDate2 === date2) return;

        if (date2Timeout) clearTimeout(date2Timeout);
        date2Timeout = setTimeout(() => {
            // Only update if date is valid
            if (localDate2) {
                params.set('date2', `${localDate2.year}-${String(localDate2.month).padStart(2, '0')}-${String(localDate2.day).padStart(2, '0')}`);
            }
        }, 1000);
    });

    function handleTopNChange() {
        if (topNTimeout) clearTimeout(topNTimeout);
        topNTimeout = setTimeout(() => {
            // Only update if topN is a valid positive number
            if (localTopN && localTopN > 0) {
                params.set('topN', localTopN.toString());
            }
        }, 500);
    }

    function toggleRoute() {
        if (isAllotaxRoute) {
            goto('/');
        } else {
            goto('/allotax');
        }
    }
</script>


<div class="controls" class:is-loading={isFetching}>
    <div class="controls-inner">
        <div class="date-controls">
            <div class="date-input">
                <label for="comparisonMode">Compare:</label>
                <select id="comparisonMode" value={comparisonMode} onchange={(e) => {
                    const newMode = e.target.value;
                    params.set('mode', newMode);
                    // Clean up params based on mode
                    if (newMode === 'dates') {
                        params.delete('country2');
                        if (!params.has('date2')) params.set('date2', params.get('date1'));
                    } else {
                        params.delete('date2');
                        if (!params.has('country2')) params.set('country2', params.get('country1'));
                    }
                }} disabled={isFetching}>
                    <option value="dates">Dates</option>
                    <option value="countries">Countries</option>
                </select>
            </div>

            {#if comparisonMode === 'dates'}
                <div class="date-input">
                    <label for="country1">Country:</label>
                    <select id="country1" value={country1} onchange={(e) => params.set('country', e.target.value)} disabled={isFetching}>
                        {#each countries as country}
                            <option value={country}>{country}</option>
                        {/each}
                    </select>
                </div>
                <div class="date-input">
                    <label for="date1">Date 1:</label>
                    <DatePicker bind:value={localDate1} {isDateUnavailable} disabled={isFetching} />
                </div>
                <div class="date-input">
                    <label for="date2">Date 2:</label>
                    <DatePicker bind:value={localDate2} {isDateUnavailable} disabled={isFetching} />
                </div>
            {:else}
                <div class="date-input">
                    <label for="date1">Date:</label>
                     <DatePicker bind:value={localDate1} {isDateUnavailable} disabled={isFetching} />
                </div>
                <div class="date-input">
                    <label for="country1">Country 1:</label>
                    <select id="country1" class="country-select" value={country1} onchange={(e) => params.set('country', e.target.value)} disabled={isFetching}>
                        {#each countries as country}
                            <option value={country}>{country}</option>
                        {/each}
                    </select>
                </div>
                <div class="date-input">
                    <label for="country2">Country 2:</label>
                    <select id="country2" class="country-select" value={country2} onchange={(e) => params.set('country2', e.target.value)} disabled={isFetching}>
                        {#each countries as country}
                            <option value={country}>{country}</option>
                        {/each}
                    </select>
                </div>
            {/if}
            <div class="date-input">
                <label for="topN">Top N:</label>
                <input type="number" id="topN" bind:value={localTopN} oninput={handleTopNChange} step="5000" disabled={isFetching} style="max-width: 100px;" />
            </div>
            <div class="alpha-control">
                <div class="alpha-display">
                    <span class="alpha-label">α =</span>
                    <span class="alpha-value">{currentAlpha === Infinity ? '∞' : currentAlpha}</span>
                </div>
                <input
                    type="range"
                    min="0"
                    max={alphas.length - 1}
                    value={alphaIndex}
                    oninput={(e) => params.set('alphaIndex', e.target.value)}
                    class="alpha-slider"
                    disabled={isFetching}
                />
            </div>
        </div>

        <div class="help-button">
            <HelpPopover side="bottom" align="end" sideOffset={8} />
        </div>

        <button onclick={toggleRoute} class="route-toggle">
            {isAllotaxRoute ? 'Pano →' : 'Allotax →'}
        </button>
    </div>
</div>

<style>
    .controls {
        position: sticky;
        top: 0;
        z-index: 100;
        background-color: var(--color-input-bg, #f9f9f9);
        border-bottom: 1px solid var(--color-border, #e0e0e0);
        transition: opacity 0.2s;
    }

    .controls.is-loading {
        opacity: 0.7;
    }

    .controls.is-loading .date-controls {
        pointer-events: none;
    }

    .controls.is-loading input,
    .controls.is-loading select {
        cursor: wait;
    }

    .controls-inner {
        padding: 0.55rem 0;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        position: relative;
    }

    .date-controls {
        display: flex;
        gap: 1rem;
        align-items: center;
    }

    .date-input {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .date-input label {
        font-size: 0.875rem;
        color: var(--color-fg, #666);
        white-space: nowrap;
    }

    .date-input input,
    .date-input select {
        padding: 0.rem;
        border: 1px solid var(--color-border, #ddd);
        border-radius: 4px;
        font-size: 0.875rem;
        background-color: white;
        transition: opacity 0.2s;
    }

    .date-input input:disabled,
    .date-input select:disabled {
        cursor: wait;
        opacity: 0.6;
    }

    .date-input select {
        min-width: 100px;
        padding: 0.5rem;
    }

    .country-select {
        min-width: 140px !important;
    }

    .alpha-control {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .alpha-display {
        display: flex;
        align-items: baseline;
        gap: 0.5rem;
    }

    .alpha-label {
        font-size: 0.875rem;
        color: var(--color-fg, #666);
    }

    .alpha-value {
        font-size: 1rem;
        font-weight: 500;
        color: var(--color-fg, #333);
    }

    .alpha-slider {
        width: 100px;
        height: 16px;
        background: transparent;
        outline: none;
        cursor: pointer;
        -webkit-appearance: none;
        appearance: none;
        transition: opacity 0.2s;
        margin: 0;
        padding: 0;
    }


    .alpha-slider:disabled {
        cursor: wait;
        opacity: 0.6;
    }

    .alpha-slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 16px;
        height: 16px;
        background: var(--color-fg, #333);
        border-radius: 50%;
        cursor: pointer;
        margin-top: -6px;
    }

    .alpha-slider::-moz-range-thumb {
        width: 16px;
        height: 16px;
        background: var(--color-fg, #333);
        border-radius: 50%;
        cursor: pointer;
        border: none;
    }

    .route-toggle {
        padding: 0.5rem 1rem;
        background-color: #373737;
        color: white;
        border: none;
        border-radius: 4px;
        font-size: 0.875rem;
        font-weight: 500;
        cursor: pointer;
        transition: background-color 0.2s;
        white-space: nowrap;
    }

    .route-toggle:hover {
        background-color: #1d4ed8;
    }

    .help-button {
        display: flex;
        align-items: center;
    }
</style>
