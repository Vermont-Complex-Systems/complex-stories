<script>
    import { browser } from '$app/environment';
    import { onMount, untrack } from 'svelte';
    import { Dashboard, Allotaxonograph } from 'allotaxonometer-ui';
    
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

    // ============================================================================
    // File Upload State
    // ============================================================================
    let uploadedSys1 = $state(null);
    let uploadedSys2 = $state(null);
    let uploadedTitle = $state(['System 1', 'System 2']);
    const hasUploadedFiles = $derived(!!uploadedSys1 && !!uploadedSys2);

    // ============================================================================
    // UI Parameters (not yet committed to API)
    // ============================================================================
    let period1 = $state([1905, 1925]);
    let period2 = $state([1968, 1998]);

    // Other parameters
    let location = $state('wikidata:Q30');
    let sex = $state('M');
    let limit = $state(10000);

    // ============================================================================
    // Committed Parameters (used for API calls)
    // ============================================================================
    let committedPeriod1Start = $state(1905);
    let committedPeriod1End = $state(1925);
    let committedPeriod2Start = $state(1972);
    let committedPeriod2End = $state(2002);
    let committedLocation = $state('wikidata:Q30');
    let committedSex = $state('M');
    let committedLimit = $state(10000);

    // Derive date strings from committed year ranges
    let dates = $derived(`${committedPeriod1Start},${committedPeriod1End}`);
    let dates2 = $derived(`${committedPeriod2Start},${committedPeriod2End}`);

    // ============================================================================
    // Alpha Parameter (updates immediately)
    // ============================================================================
    const alphas = [0, 1/4, 2/4, 3/4, 1, 3/2, 2, 3, 5, Infinity];
    let alphaIndex = $state(7); // Index for alpha = 3
    let alpha = $derived(alphas[alphaIndex]);

    // ============================================================================
    // Adapter Data & Date Range Logic
    // ============================================================================

    let adapterData = $state([]);
    const dateRange = $derived.by(() => {
        if (!adapterData.length) return { min: 1880, max: 2023 };
        const locationData = adapterData.find(l => l.entity_id === location);
        if (locationData?.min_year && locationData?.max_year) {
            return { min: locationData.min_year, max: locationData.max_year };
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
        }

        // Check if current period2 is outside the new range
        if (period2[0] < dateMin || period2[0] > dateMax) {
            // Set period2 to approximately 75% through the range
            const newYear = Math.floor(dateMin + span * 0.75);
            period2 = [newYear, newYear];
        }
    });

    // ============================================================================
    // Change Tracking & Warnings
    // ============================================================================
    let hasChanges = $derived(
        period1[0] !== committedPeriod1Start ||
        period1[1] !== committedPeriod1End ||
        period2[0] !== committedPeriod2Start ||
        period2[1] !== committedPeriod2End ||
        limit !== committedLimit
    );

    // Auto-fetch when location or sex changes (discrete actions, no Update button needed)
    let reactiveEnabled = false;
    $effect(() => {
        location; sex;
        if (!reactiveEnabled) return;
        untrack(() => updateData());
    });

    // ============================================================================
    // Data Loading & Management
    // ============================================================================

    function handleFilesUploaded(sys1Data, sys2Data, titles) {
        uploadedSys1 = sys1Data;
        uploadedSys2 = sys2Data;
        uploadedTitle = titles;
        sys1 = sys1Data;
        sys2 = sys2Data;
        title = titles;
        allotax.updateData(sys1Data, sys2Data, titles);
    }

    let sys1 = $state(null);
    let sys2 = $state(null);
    let title = $state(['Boys 1905-1925', 'Boys 1972-2002']);
    let isLoading = $state(false);

    function applyLimit(data, n) {
        if (data.length <= n) return data;
        const sliced = data.slice(0, n);
        const total = sliced.reduce((s, d) => s + d.counts, 0);
        return sliced.map(d => ({ ...d, probs: d.counts / total, totalunique: sliced.length }));
    }

    async function fetchBabyNames() {
        if (hasUploadedFiles) {
            const d1 = applyLimit(uploadedSys1, committedLimit);
            const d2 = applyLimit(uploadedSys2, committedLimit);
            sys1 = d1;
            sys2 = d2;
            title = uploadedTitle;
            allotax.updateData(d1, d2, uploadedTitle);
            return;
        }

        isLoading = true;
        try {
            const ngrams = await getTopBabyNames({
                dates,
                dates2,
                locations: committedLocation,
                sex: committedSex,
                limit: committedLimit
            });

            const keys = Object.keys(ngrams);
            sys1 = ngrams[dates] || ngrams[keys[0]];
            sys2 = ngrams[dates2] || ngrams[keys[1]];

            const genderLabel = committedSex === 'M' ? 'Boys' : 'Girls';
            title = [
                `${genderLabel} ${committedPeriod1Start}-${committedPeriod1End}`,
                `${genderLabel} ${committedPeriod2Start}-${committedPeriod2End}`
            ];
            allotax.updateData(sys1, sys2, title);
        } catch (err) {
            console.error('Failed to fetch baby names:', err);
            sys1 = boys1895;
            sys2 = boys1968;
            allotax.updateData(boys1895, boys1968, title);
        } finally {
            isLoading = false;
        }
    }

    // Load initial data on mount
    onMount(async () => {
        try {
            adapterData = await getAdapter();
        } catch (err) {
            console.error('Failed to load adapter:', err);
        }

        fetchBabyNames();
        reactiveEnabled = true;
    });

    // Update function - commits UI changes and fetches new data
    function updateData() {
        // Commit UI state to API parameters
        [committedPeriod1Start, committedPeriod1End] = period1;
        [committedPeriod2Start, committedPeriod2End] = period2;
        committedLocation = location;
        committedSex = sex;
        committedLimit = limit;

        fetchBabyNames();
    }

    // ============================================================================
    // Visualization Data Computation (via Allotaxonograph — uses WASM when available)
    // ============================================================================
    const allotax = new Allotaxonograph();

    $effect(() => {
        allotax.setAlpha(alpha);
    });


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

                            <div class="sex-control">
                                <SexToggle bind:sex />
                            </div>

                            <div class="separator"></div>
                        {/if}

                        <div class="topn-control">
                            <TopNSelector bind:limit />
                            {#if allotax.dat}
                                <div class="topn-available">
                                    max: <span class="sys-badge sys1-badge">1</span>{(sys1?.[0]?.totalunique || sys1?.length || 0).toLocaleString()}
                                    <span class="sys-badge sys2-badge">2</span>{(sys2?.[0]?.totalunique || sys2?.length || 0).toLocaleString()}
                                </div>
                            {/if}
                        </div>

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
                        {/if}

                            <button
                                class="update-button"
                                onclick={updateData}
                                disabled={!hasChanges || isLoading}
                            >
                                {#if isLoading}
                                    <span class="btn-spinner"></span>
                                    Loading...
                                {:else}
                                    Update
                                {/if}
                            </button>

                        {#if allotax.dat}
                            <DataInfo
                                {title}
                                itemCount={sys1?.length || 0}
                                normalization={allotax.rtd?.normalization ?? 0}
                            />
                        {/if}

                        <div class="separator"></div>

                        <DownloadSection isDataReady={!!allotax.dat} />
                    </div>
                </div>
            </aside>

            <main class="main-content">
                <Nav/>

                {#if browser && allotax.dat}
                    <div id="allotaxonometer-dashboard">
                        {#key `${committedPeriod1Start}-${committedPeriod1End}-${committedPeriod2Start}-${committedPeriod2End}-${committedLocation}-${committedSex}-${committedLimit}-${alpha}-${hasUploadedFiles}`}
                            <Dashboard
                                dat={allotax.dat}
                                barData={allotax.barData}
                                balanceData={allotax.balanceData}
                                maxlog10={allotax.maxlog10}
                                divnorm={allotax.rtd?.normalization ?? 1}
                                {title}
                                {alpha}
                                WordshiftWidth={400}
                            />
                        {/key}
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
        width: 16rem;
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

    .topn-available {
        display: flex;
        align-items: center;
        gap: 0.375rem;
        margin-top: 0.375rem;
        font-size: var(--11px, 0.69rem);
        color: var(--color-text-secondary);
        justify-content: flex-end;
    }

    .sys-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 1rem;
        height: 1rem;
        border-radius: 50%;
        font-size: var(--10px, 0.625rem);
        font-weight: 700;
        color: rgb(59, 59, 59);
        flex-shrink: 0;
    }

    .sys1-badge { background-color: rgb(230, 230, 230); }
    .sys2-badge { background-color: rgb(195, 230, 243); }

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

    .btn-spinner {
        display: inline-block;
        width: 0.875rem;
        height: 0.875rem;
        border: 2px solid currentColor;
        border-top-color: transparent;
        border-radius: 50%;
        animation: spin 0.7s linear infinite;
        flex-shrink: 0;
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
