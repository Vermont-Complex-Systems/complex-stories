<script lang="ts">
    // import Sidebar from './Sidebar.svelte';
    import Spinner from '$lib/components/helpers/Spinner.svelte';
    import { Dashboard, Allotaxonograph } from 'allotaxonometer-ui';
    import { getTopBabyNames, getAvailableLocations } from '../allotax.remote.js';
    import YearSlider from './sidebar/YearSlider.svelte';
    import AlphaSlider from './sidebar/AlphaSlider.svelte';
    import LocationSelector from './sidebar/LocationSelector.svelte';
    import MultiFileUpload from './sidebar/MultiFileUpload.svelte';
    import { createQuery } from '@tanstack/svelte-query';

    // Local state for years - separate periods for each system
    let period1 = $state([1940, 1959]);
    let period2 = $state([1990, 2009]);
    let sidebarCollapsed = $state(false);
    let jumpYears = $state(5);
    let alphaIndex = $state(7);
    let selectedLocation = $state('united_states');

    // File upload state
    let uploadedSys1 = $state(null);
    let uploadedSys2 = $state(null);
    let uploadedTitle = $state(['System 1', 'System 2']);
    let uploadStatus = $state('');
    let uploadWarnings = $state([]);

    // Check if any files are uploaded
    let hasUploadedFiles = $derived(uploadedSys1 || uploadedSys2);

    // Simple file upload handler
    async function handleFileUpload(file: File, system: 'sys1' | 'sys2') {
        uploadStatus = `Loading ${file.name}...`;
        uploadWarnings = [];

        try {
            // Simple CSV/JSON parsing - you'd implement parseDataFile or similar
            const text = await file.text();
            let data: any;

            if (file.name.endsWith('.json')) {
                data = JSON.parse(text);
            } else if (file.name.endsWith('.csv')) {
                // Basic CSV parsing - could use d3.csvParse here
                const lines = text.split('\n');
                const headers = lines[0].split(',');
                data = lines.slice(1).filter((line: string) => line.trim()).map((line: string) => {
                    const values = line.split(',');
                    const obj: any = {};
                    headers.forEach((header: string, i: number) => {
                        obj[header.trim()] = values[i]?.trim();
                    });
                    return obj;
                });
            }

            if (system === 'sys1') {
                uploadedSys1 = data;
                uploadedTitle[0] = file.name.replace(/\.(json|csv)$/i, '');
            } else {
                uploadedSys2 = data;
                uploadedTitle[1] = file.name.replace(/\.(json|csv)$/i, '');
            }

            uploadStatus = `${system.toUpperCase()}: ${file.name} loaded successfully!`;
            setTimeout(() => uploadStatus = '', 3000);

            // Automatically trigger data refresh when files are uploaded
            loadData();

            return { success: true, fileName: file.name };
        } catch (error: unknown) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            uploadStatus = `Error loading ${file.name}: ${errorMessage}`;
            setTimeout(() => uploadStatus = '', 5000);
            return { success: false, error: errorMessage };
        }
    }

    // Alpha values: 0, 1/4, 2/4, 3/4, 1, 3/2, 2, 3, 5, ∞
    const alphas = [0, 1/4, 2/4, 3/4, 1, 3/2, 2, 3, 5, Infinity];

    // Alpha derived values
    const currentAlpha = $derived(alphas[alphaIndex]);

    // Alpha change handler
    function onAlphaChange(newIndex: number) {
        alphaIndex = newIndex;
        // No need to refetch data - alpha is a client-side visualization parameter
    }

    // Query function
    async function fetchBabyNames() {
        // If files are uploaded, use them instead of API data
        if (hasUploadedFiles) {
            const elem1 = uploadedSys1 || [];
            const elem2 = uploadedSys2 || [];

            return new Allotaxonograph(elem1, elem2, {
                alpha: currentAlpha,
                title: uploadedTitle
            });
        }

        // Otherwise use API data
        const period1Str = `${period1[0]},${period1[1]}`;
        const period2Str = `${period2[0]},${period2[1]}`;

        const ngrams = await getTopBabyNames({
            dates: period1Str,
            dates2: period2Str,
            location: selectedLocation
        });

        // Get the first two keys from the response (they should be the period ranges)
        const keys = Object.keys(ngrams);
        const elem1 = ngrams[keys[0]];
        const elem2 = ngrams[keys[1]];

        return new Allotaxonograph(elem1, elem2, {
            alpha: currentAlpha,
            title: [`${period1[0]}-${period1[1]}`, `${period2[0]}-${period2[1]}`]
        });
    }

    // Locations state - fetch once on mount
    let locations = $state([]);
    let locationsLoading = $state(true);
    let locationsError = $state(false);

    // Fetch locations on mount
    $effect(() => {
        (async () => {
            try {
                console.log('Fetching locations...');
                locations = await getAvailableLocations();
                console.log('Locations loaded:', locations);
                locationsLoading = false;
            } catch (error) {
                console.error('Failed to fetch locations:', error);
                locationsError = true;
                locationsLoading = false;
            }
        })();
    });

    // Create query for baby names data - don't include periods/location to avoid auto-refresh on slider drag
    const query = createQuery(() => ({
        queryKey: ['babynames', currentAlpha, hasUploadedFiles, !!uploadedSys1, !!uploadedSys2, JSON.stringify(uploadedTitle)],
        queryFn: fetchBabyNames,
        enabled: true, // Run automatically on load
        staleTime: 5 * 60 * 1000, // 5 minutes - don't refetch for 5 mins
        gcTime: 10 * 60 * 1000, // 10 minutes - keep in cache for 10 mins
    }));

    // Function to trigger data loading
    function loadData() {
        query.refetch();
    }

    // Extract data properties as derived values for better control
    const instance = $derived(query.data);
    const dat = $derived(instance?.dat);
    const barData = $derived(instance?.barData);
    const balanceData = $derived(instance?.balanceData);
    const maxlog10 = $derived(instance?.maxlog10);
    const divnorm = $derived(instance?.divnorm);
    const displayTitles = $derived(instance?.title || ['System 1', 'System 2']);

    // Arrow navigation functions for both periods
    function shiftBothPeriodsLeft() {
        // Shift period 1
        const range1Size = period1[1] - period1[0];
        let newStart1 = period1[0] - jumpYears;
        let newEnd1 = newStart1 + range1Size;

        if (newStart1 < 1880) {
            newStart1 = 1880;
            newEnd1 = newStart1 + range1Size;
        }

        period1 = [newStart1, newEnd1];

        // Shift period 2
        const range2Size = period2[1] - period2[0];
        let newStart2 = period2[0] - jumpYears;
        let newEnd2 = newStart2 + range2Size;

        if (newStart2 < 1880) {
            newStart2 = 1880;
            newEnd2 = newStart2 + range2Size;
        }

        period2 = [newStart2, newEnd2];

        // Auto-refetch data after jumping
        loadData();
    }

    function shiftBothPeriodsRight() {
        // Shift period 1
        const range1Size = period1[1] - period1[0];
        let newStart1 = period1[0] + jumpYears;
        let newEnd1 = newStart1 + range1Size;

        if (newEnd1 > 2020) {
            newEnd1 = 2020;
            newStart1 = newEnd1 - range1Size;
        }

        period1 = [newStart1, newEnd1];

        // Shift period 2
        const range2Size = period2[1] - period2[0];
        let newStart2 = period2[0] + jumpYears;
        let newEnd2 = newStart2 + range2Size;

        if (newEnd2 > 2020) {
            newEnd2 = 2020;
            newStart2 = newEnd2 - range2Size;
        }

        period2 = [newStart2, newEnd2];

        // Auto-refetch data after jumping
        loadData();
    }

    function canShiftLeft() {
        return period1[0] > 1880 || period2[0] > 1880;
    }

    function canShiftRight() {
        return period1[1] < 2020 || period2[1] < 2020;
    }
</script>

<div class="app-container">
        <div class="layout">
            <aside class="sidebar-container {sidebarCollapsed ? 'collapsed' : ''}">
                <div class="sidebar-content">
                    <div class="sidebar-header">
                        <h2 class="sidebar-title">Allotaxonograph</h2>
                    </div>

                    <div class="sidebar-body">
                        <MultiFileUpload
                            bind:sys1={uploadedSys1}
                            bind:sys2={uploadedSys2}
                            bind:title={uploadedTitle}
                            {handleFileUpload}
                            {uploadStatus}
                            {uploadWarnings}
                        />

                        <div class="separator"></div>

                        {#if !hasUploadedFiles}
                            <div class="location-control">
                                <LocationSelector
                                    bind:value={selectedLocation}
                                    label="Location"
                                    {locations}
                                    isLoading={locationsLoading}
                                    isError={locationsError}
                                />
                            </div>

                            <div class="separator"></div>
                        {/if}

                        <div class="alpha-control">
                        <AlphaSlider
                            {alphas}
                            {alphaIndex}
                            {currentAlpha}
                            {onAlphaChange}
                        />
                    </div>

                    <div class="separator"></div>

                    {#if !hasUploadedFiles}
                        <div class="year-control">
                            <YearSlider
                                bind:value={period1}
                                min={1880}
                                max={2020}
                                label="Period 1"
                            />
                        </div>

                        <div class="year-control">
                            <YearSlider
                                bind:value={period2}
                                min={1880}
                                max={2020}
                                label="Period 2"
                            />
                        </div>

                        <div class="arrow-controls">
                            <button class="arrow-btn" onclick={shiftBothPeriodsLeft} disabled={!canShiftLeft()}>
                                ← {jumpYears} yrs back
                            </button>
                            <span class="arrow-separator">•</span>
                            <button class="arrow-btn" onclick={shiftBothPeriodsRight} disabled={!canShiftRight()}>
                                {jumpYears} yrs forward →
                            </button>
                        </div>

                        <div class="jump-control">
                            <label for="jumpYears" class="jump-label">Jump by:</label>
                            <input
                                id="jumpYears"
                                type="number"
                                bind:value={jumpYears}
                                min="1"
                                max="50"
                                class="jump-input"
                            />
                            <span class="jump-unit">years</span>
                        </div>
                    {/if}
                    
                    {#if !hasUploadedFiles}
                        <div class="separator"></div>

                        <button class="load-button" onclick={loadData} disabled={query.isLoading}>
                            {#if query.isLoading}
                                <div class="loading-spinner"></div>
                                Loading...
                            {:else}
                                Update
                            {/if}
                        </button>
                    {/if}

                    </div>
                </div>
            </aside>
            
            <main class="main-content">
                {#if query.isLoading}
                    <div class="main-loading">
                        <Spinner />
                        <p>Loading rust-wasm and baby names comparison...</p>
                    </div>
                {:else if query.isError}
                    <div class="error">
                        <p>Failed to load baby names data:</p>
                        <p>{query.error?.message || 'Unknown error'}</p>
                    </div>
                {:else if query.isSuccess}
                    <Dashboard
                        {dat}
                        {barData}
                        {balanceData}
                        {maxlog10}
                        {divnorm}
                        title={displayTitles}
                        alpha={currentAlpha}
                        WordshiftWidth={400}
                        />
                {:else}
                    <div class="welcome">
                        <h2>Baby Names Comparison</h2>
                        <p>Adjust settings in the sidebar to explore different time periods and locations.</p>
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

    .sidebar-container {
        flex-shrink: 0;
        width: 17rem;
        background-color: var(--color-input-bg);
        border-right: 1px solid var(--color-border);
        transition: width var(--transition-medium) ease;
        overflow: hidden;
    }

    .sidebar-container.collapsed {
        width: 5rem;
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

    /* Responsive */
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

    
    .sidebar-content {
        height: 100%;
        display: flex;
        flex-direction: column;
        background-color: var(--color-sidebar-bg, #f8f9fa);
    }

    .sidebar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        border-bottom: 1px solid var(--color-border, #e0e0e0);
        background-color: var(--color-sidebar-header-bg, #fff);
    }

    .sidebar-title {
        font-size: var(--16px, 1rem);
        font-weight: var(--font-weight-bold, 600);
        color: var(--color-text-primary, #333);
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
        padding-bottom: 1rem;
    }

    .year-control {
        margin-bottom: 1.5rem;
        margin-top: 2.5rem;
        padding-bottom: 1rem;
    }

    .year-control:last-of-type {
        border-bottom: none;
    }

    .alpha-control {
        margin-bottom: 4.5rem;
        margin-top: 2rem;
        padding: 1.5rem 0;
        display: flex;
        align-items: center;
        position: relative;
        justify-content: center;
    }

    /* Mobile responsive styles for alpha control */
    @media (max-width: 768px) {
        .alpha-control {
            width: 100%;
            justify-content: center;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
    }


    .load-button {
        width: 100%;
        padding: 0.75rem 1rem;
        margin: 1rem 0;
        background-color: var(--color-good-blue, #3b82f6);
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 0.95rem;
        font-weight: 500;
        cursor: pointer;
        transition: background-color 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    .load-button:hover:not(:disabled) {
        background-color: var(--color-good-blue-hover, #2563eb);
    }

    .load-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .loading-spinner {
        width: 1rem;
        height: 1rem;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top: 2px solid white;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .main-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        gap: 1rem;
    }

    .welcome {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        text-align: center;
        color: var(--color-text-secondary, #666);
    }

    .welcome h2 {
        margin-bottom: 1rem;
        color: var(--color-text, #333);
    }

    .arrow-controls {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0.75rem 0 0.25rem 0;
        padding: 0.25rem 0;
    }

    .arrow-btn {
        padding: 0.5rem;
        border: none;
        background: transparent;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
        transition: all 150ms ease;
        white-space: nowrap;
        color: var(--color-text, #333);
    }

    .arrow-btn:hover:not(:disabled) {
        transform: scale(1.05);
        background: rgba(0,0,0,0.05);
        border-radius: 4px;
    }

    .arrow-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .arrow-separator {
        margin: 0 0.5rem;
        font-size: 16px;

    }

    .jump-control {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin: 0.25rem 0 0.75rem 0;
    }

    .jump-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--color-text, #333);
    }

    .jump-input {
        width: 50px;
        padding: 0.25rem 0.5rem;
        border: 1px solid rgba(0, 0, 0, 0.2);
        border-radius: 3px;
        font-size: 0.85rem;
        text-align: center;
        background-color: white;
    }

    .jump-input:focus {
        outline: none;
        border-color: var(--color-good-blue, #3b82f6);
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
    }

    .jump-unit {
        font-size: 0.85rem;
        color: var(--color-text-secondary, #666);
    }

    .error {
        padding: 2rem;
        text-align: center;
        color: #ef4444;
    }

    .separator {
        border-top: 1px solid rgba(0, 0, 0, 0.1);
        margin: 1.5rem -1.5rem;
    }
</style>