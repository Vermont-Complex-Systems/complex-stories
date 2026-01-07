<script>
    import * as d3 from 'd3';
    import { Dashboard } from 'allotaxonometer-ui';
    import { combElems, rank_turbulence_divergence, diamond_count, wordShift_dat, balanceDat } from 'allotaxonometer-ui';
    import Nav from './Nav.svelte';
    import SexToggle from './sidebar/SexToggle.svelte';
    import TopNSelector from './sidebar/TopNSelector.svelte';
    import AlphaSliderLocal from './sidebar/AlphaSliderLocal.svelte';
    import YearSlider from './sidebar/YearSlider.svelte';
    import LocationSelector from './sidebar/LocationSelector.svelte';
    import PeriodJumpControlsLocal from './sidebar/PeriodJumpControlsLocal.svelte';
    import MultiFileUploadLocal from './sidebar/MultiFileUploadLocal.svelte';
    import DownloadSection from './sidebar/DownloadSection.svelte';
    import DataInfo from './sidebar/DataInfo.svelte';
    import { getTopBabyNames, getAdapter } from '../allotax.remote';
    
    import boys1968 from '../data/boys-1968.json';
    import boys1895 from '../data/boys-1895.json';

    // File upload state
    let uploadedSys1 = $state(null);
    let uploadedSys2 = $state(null);
    let uploadedTitle = $state(['System 1', 'System 2']);
    const hasUploadedFiles = $derived(!!uploadedSys1 && !!uploadedSys2);

    // Year range state - two separate sliders for comparison
    let period1 = $state([1905, 1925]); // Single year by default
    let period2 = $state([1968, 1998]); // Single year by default

    // Other parameters (UI state - not sent to API until update)
    let location = $state('wikidata:Q30');
    let sex = $state('M');
    let limit = $state(10000);

    // Committed parameters (actually used for API calls)
    let committedPeriod1 = $state([1905, 1925]);
    let committedPeriod2 = $state([1972, 2002]);
    let committedLocation = $state('wikidata:Q30');
    let committedSex = $state('M');
    let committedLimit = $state(10000);

    // Derive date strings from committed year ranges
    let dates = $derived(`${committedPeriod1[0]},${committedPeriod1[1]}`);
    let dates2 = $derived(`${committedPeriod2[0]},${committedPeriod2[1]}`);

    // Alpha slider state (updates immediately - no update button needed)
    const alphas = [0, 1/4, 2/4, 3/4, 1, 3/2, 2, 3, 5, Infinity];
    let alphaIndex = $state(7); // Index for alpha = 2
    let alpha = $derived(alphas[alphaIndex]);

    // Fetch location adapter data
    const adapterQuery = getAdapter();
    const adapterData = $derived(adapterQuery.error ? [] : (adapterQuery.current || []));

    // Derive date range based on selected location
    const dateRange = $derived.by(() => {
        if (!adapterData?.length) return { min: 1880, max: 2023 };
        const locationData = adapterData.find(l => l[1] === location);
        if (locationData && locationData[4] && locationData[5]) {
            return { min: locationData[4], max: locationData[5] };
        }
        return { min: 1880, max: 2023 };
    });

    const dateMin = $derived(dateRange.min);
    const dateMax = $derived(dateRange.max);

    // Adjust periods when date range changes (location change)
    $effect(() => {
        // Calculate span of available years
        const span = dateMax - dateMin;

        // Check if current period1 is outside the new range
        if (period1[0] < dateMin || period1[0] > dateMax) {
            // Set period1 to approximately 25% through the range
            const newYear = Math.floor(dateMin + span * 0.25);
            period1 = [newYear, newYear];
            console.log('Adjusted period1 to:', newYear);
        }

        // Check if current period2 is outside the new range
        if (period2[0] < dateMin || period2[0] > dateMax) {
            // Set period2 to approximately 75% through the range
            const newYear = Math.floor(dateMin + span * 0.75);
            period2 = [newYear, newYear];
            console.log('Adjusted period2 to:', newYear);
        }
    });

    // Check if there are uncommitted changes
    let hasChanges = $derived(
        period1[0] !== committedPeriod1[0] ||
        period2[0] !== committedPeriod2[0] ||
        location !== committedLocation ||
        sex !== committedSex ||
        limit !== committedLimit
    );

    // Track what topN was fetched for warning message
    let fetchedTopN = $state(10000);
    let warningDismissed = $state(false);

    // Check if we got fewer results than requested
    const showTopNWarning = $derived.by(() => {
        if (hasUploadedFiles || !me || warningDismissed) return false;
        const count1 = me[0]?.ranks?.length || 0;
        const count2 = me[1]?.ranks?.length || 0;
        return count1 < fetchedTopN || count2 < fetchedTopN;
    });

    // Auto-dismiss warning after 5 seconds
    $effect(() => {
        if (showTopNWarning) {
            warningDismissed = false;
            const timer = setTimeout(() => {
                warningDismissed = true;
            }, 5000);
            return () => clearTimeout(timer);
        }
    });

    // Update function - commits changes and triggers API call
    function updateData() {
        committedPeriod1 = [...period1];
        committedPeriod2 = [...period2];
        committedLocation = location;
        committedSex = sex;
        committedLimit = limit;
        fetchedTopN = limit; // Track what we actually requested
    }

    // Callback when files are uploaded
    function handleFilesUploaded(sys1Data, sys2Data, titles) {
        console.log('Files uploaded, setting data');
        uploadedSys1 = sys1Data;
        uploadedSys2 = sys2Data;
        uploadedTitle = titles;
    }

    // Fetch data from API (only when committed parameters change and no uploaded files)
    const apiQuery = $derived(!hasUploadedFiles ? getTopBabyNames({
        dates,
        dates2,
        location: committedLocation,
        sex: committedSex,
        limit: committedLimit
    }) : null);

    // Extract data from query, returning null on error (triggers static fallback)
    const apiData = $derived(apiQuery?.error ? null : apiQuery?.current);

    // Extract systems from either uploaded files or API response
    // Falls back to static data if API is unavailable
    const sys1 = $derived.by(() => {
        if (hasUploadedFiles) return uploadedSys1;
        if (apiData) return apiData[dates] || apiData[Object.keys(apiData)[0]];
        // Fallback to static data if API failed
        return boys1895;
    });

    const sys2 = $derived.by(() => {
        if (hasUploadedFiles) return uploadedSys2;
        if (apiData) return apiData[dates2] || apiData[Object.keys(apiData)[1]];
        // Fallback to static data if API failed
        return boys1968;
    });

    const title = $derived.by(() => {
        if (hasUploadedFiles) return uploadedTitle;
        // If using fallback static data, show static data titles (single years only)
        if (!apiData) return ['Boys 1895', 'Boys 1968'];
        // Otherwise show the actual requested dates with dash separator
        const range1 = `${committedPeriod1[0]}-${committedPeriod1[1]}`;
        const range2 = `${committedPeriod2[0]}-${committedPeriod2[1]}`;
        return [`${sex === 'M' ? 'Boys' : 'Girls'} ${range1}`, `${sex === 'M' ? 'Boys' : 'Girls'} ${range2}`];
    });

    // Compute visualization data using utility functions
    const me = $derived(sys1 && sys2 ? combElems(sys1, sys2) : null);
    const rtd = $derived(me ? rank_turbulence_divergence(me, alpha) : null);
    const dat = $derived(me && rtd ? diamond_count(me, rtd) : null);
    const barData = $derived(me && dat ? wordShift_dat(me, dat).slice(0, 30) : []);
    const balanceData = $derived(sys1 && sys2 ? balanceDat(sys1, sys2) : []);
    const maxlog10 = $derived(me ? Math.ceil(d3.max([Math.log10(d3.max(me[0].ranks)), Math.log10(d3.max(me[1].ranks))])) : 0);
    const divnorm = $derived(rtd ? rtd.normalization : 1);

</script>

<div class="app-container">
        <div class="layout">
            <aside class="sidebar-container">
                <div class="sidebar-content">
                    <div class="sidebar-header">
                        <h2 class="sidebar-title">Allotaxonograph</h2>
                    </div>

                    <div class="sidebar-body">
                        <MultiFileUploadLocal
                            onFilesUploaded={handleFilesUploaded}
                        />

                        <div class="separator"></div>

                        {#if !hasUploadedFiles}
                            <div class="location-control">
                                <LocationSelector
                                    bind:location
                                    adapter={adapterData || []}
                                    label="Location"
                                />
                            </div>

                            <div class="topn-control">
                                <TopNSelector bind:limit />

                                {#if showTopNWarning && me}
                                    {@const count1 = me[0]?.ranks?.length || 0}
                                    {@const count2 = me[1]?.ranks?.length || 0}
                                    <div class="topn-warning">
                                        <svg class="warning-icon" viewBox="0 0 20 20" fill="currentColor">
                                            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                                        </svg>
                                        <div class="warning-text">
                                            {#if count1 < fetchedTopN && count2 < fetchedTopN}
                                                <span>System 1: {count1.toLocaleString()} names, System 2: {count2.toLocaleString()} names (requested {fetchedTopN.toLocaleString()})</span>
                                            {:else if count1 < fetchedTopN}
                                                <span>System 1: Only {count1.toLocaleString()} names available (requested {fetchedTopN.toLocaleString()})</span>
                                            {:else}
                                                <span>System 2: Only {count2.toLocaleString()} names available (requested {fetchedTopN.toLocaleString()})</span>
                                            {/if}
                                        </div>
                                    </div>
                                {/if}
                            </div>

                            <div class="sex-control">
                                <SexToggle bind:sex />
                            </div>

                            <div class="separator"></div>
                        {/if}

                        <div class="alpha-control">
                            <AlphaSliderLocal bind:alphaIndex {alphas} />
                        </div>

                        {#if !hasUploadedFiles}
                            <div class="separator"></div>

                            <div class="year-control">
                                <YearSlider
                                    bind:value={period1}
                                    label="Period 1"
                                    min={dateMin}
                                    max={dateMax}
                                />
                            </div>

                            <div class="year-control">
                                <YearSlider
                                    bind:value={period2}
                                    label="Period 2"
                                    min={dateMin}
                                    max={dateMax}
                                />
                            </div>

                            <PeriodJumpControlsLocal
                                bind:period1
                                bind:period2
                                {dateMin}
                                {dateMax}
                                onJump={updateData}
                            />

                            <button
                                class="update-button"
                                onclick={updateData}
                                disabled={!hasChanges}
                            >
                                {hasChanges ? 'Update' : 'Up to date'}
                            </button>
                        {/if}

                        {#if me && rtd}
                            <DataInfo {title} {me} {rtd} />
                        {/if}

                        <div class="separator"></div>

                        <DownloadSection isDataReady={!!dat} />
                    </div>
                </div>
            </aside>

            <main class="main-content">
                <Nav/>

                {#if dat}
                    <div id="allotaxonometer-dashboard">
                        <Dashboard
                            {dat}
                            {barData}
                            {balanceData}
                            {maxlog10}
                            {divnorm}
                            {title}
                            {alpha}
                            WordshiftWidth={400}
                        />
                    </div>
                {:else}
                    <div class="loading">
                        <div class="loading-content">
                            <div class="spinner"></div>
                            <p>Loading baby names data...</p>
                        </div>
                    </div>
                {/if}
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

    .main-content {
        flex: 1;
        overflow: auto;
        background-color: var(--color-bg);
        max-width: none;
        margin: 0;
        padding: 5.5rem 0 0 0;
        transition: padding-left var(--transition-medium) ease;
    }

    .sidebar-container {
        flex-shrink: 0;
        width: 17rem;
        background-color: var(--color-input-bg);
        border-right: 1px solid var(--color-border);
        transition: width var(--transition-medium) ease;
        overflow: hidden;
    }

    .sidebar-content {
        height: 100%;
        display: flex;
        flex-direction: column;
        background-color: var(--color-input-bg);
    }

    .sidebar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        border-bottom: 1px solid var(--color-border);
        background-color: var(--color-bg);
    }

    .sidebar-title {
        font-size: var(--16px, 1rem);
        font-weight: var(--font-weight-bold, 600);
        color: var(--color-text-primary);
        margin: 0;
    }

    .sidebar-body {
        flex: 1;
        overflow-y: auto;
        padding: 1.5rem;
    }

    .location-control {
        margin-bottom: 1.5rem;
        margin-top: 1rem;
    }

    .topn-control {
        margin-bottom: 1rem;
        margin-top: 0.5rem;
    }

    .sex-control {
        margin-bottom: 1rem;
        margin-top: 0.5rem;
    }

    .alpha-control {
        margin-bottom: 3rem;
        margin-top: 2rem;
        padding: 1.5rem 0;
        display: flex;
        align-items: center;
        position: relative;
        justify-content: center;
    }

    .year-control {
        margin-bottom: 2rem;
        margin-top: 2.5rem;
    }

    .separator {
        border-top: 1px solid var(--color-border);
        margin: 1.5rem -1.5rem;
    }

    .topn-warning {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        padding: 0.75rem;
        margin-top: 0.75rem;
        margin-bottom: 0.5rem;
        background-color: rgba(251, 191, 36, 0.1);
        border: 1px solid rgba(251, 191, 36, 0.3);
        border-radius: 6px;
        font-size: var(--12px, 0.75rem);
        color: var(--color-text-primary);
    }

    .warning-icon {
        width: 1.25rem;
        height: 1.25rem;
        flex-shrink: 0;
        color: rgba(251, 191, 36, 1);
        margin-top: 0.125rem;
    }

    .warning-text {
        flex: 1;
        line-height: 1.4;
    }

    .warning-text span {
        display: block;
    }

    .update-button {
        width: 100%;
        padding: 0.75rem 1rem;
        margin: 1rem 0;
        background-color: var(--color-bg);
        color: var(--color-text);
        border: 1px solid var(--color-border);
        border-radius: 6px;
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    .update-button:hover:not(:disabled) {
        background-color: var(--color-input-bg);
        border-color: var(--color-text);
        transform: translateY(-1px);
    }

    .update-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .loading {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        color: var(--color-text-secondary);
    }

    .loading-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.5rem;
    }

    .loading-content p {
        font-size: 1rem;
        color: var(--color-text-secondary);
        margin: 0;
    }

    .spinner {
        width: 3rem;
        height: 3rem;
        border: 4px solid var(--color-border);
        border-top-color: var(--color-good-blue, #3b82f6);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    /* Mobile */
    @media (max-width: 768px) {
        .layout {
            flex-direction: column;
        }

        .sidebar-container {
            width: 100% !important;
            height: auto;
            border-right: none;
            border-bottom: 1px solid var(--color-border);
        }
    }
</style>
