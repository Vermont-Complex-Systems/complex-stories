<script lang="ts">
    import YearSlider from './sidebar/YearSlider.svelte';
    import AlphaSlider from './sidebar/AlphaSlider.svelte';
    import LocationSelector from './sidebar/LocationSelector.svelte';
    import SexToggle from './sidebar/SexToggle.svelte';
    import TopNSelector from './sidebar/TopNSelector.svelte';
    import MultiFileUpload from './sidebar/MultiFileUpload.svelte';
    import PeriodJumpControls from './sidebar/PeriodJumpControls.svelte';
    import DataInfo from './sidebar/DataInfo.svelte';
    import DownloadSection from './sidebar/DownloadSection.svelte';
    import { fileState, dashboardState, alphas } from '../sidebar-state.svelte.ts';

    // Props passed from parent (Index.svelte owns query and instance)
    let { query, instance } = $props();

    // Derived values from props
    const displayTitles = $derived(query.data?.title || ['System 1', 'System 2']);
    const me = $derived(instance?.me);
    const rtd = $derived(instance?.rtd);
    const isDataReady = $derived(!!query.data && !!instance);

    // Check if we got fewer results than requested
    const showTopNWarning = $derived(
        isDataReady &&
        query.data &&
        ((query.data.elem1?.length || 0) < dashboardState.fetchedTopN ||
         (query.data.elem2?.length || 0) < dashboardState.fetchedTopN)
    );

    // Auto-dismiss warning after 5 seconds
    $effect(() => {
        if (showTopNWarning) {
            dashboardState.warningDismissed = false;
            const timer = setTimeout(() => {
                dashboardState.warningDismissed = true;
            }, 5000);
            return () => clearTimeout(timer);
        }
    });
</script>

<div class="sidebar-content">
    <div class="sidebar-header">
        <h2 class="sidebar-title">Allotaxonograph</h2>
    </div>

    <div class="sidebar-body">
        <MultiFileUpload
            bind:sys1={fileState.uploadedSys1}
            bind:sys2={fileState.uploadedSys2}
            bind:title={fileState.uploadedTitle}
            handleFileUpload={(file, system) => fileState.handleFileUpload(file, system)}
            uploadStatus={fileState.uploadStatus}
            uploadWarnings={fileState.uploadWarnings}
        />

        <div class="separator"></div>

        {#if !fileState.hasUploadedFiles}
            <div class="location-control">
                <LocationSelector label="Location" />
            </div>

            <div class="topn-control">
                <TopNSelector />

                {#if showTopNWarning && !dashboardState.warningDismissed && query.data}
                    {@const count1 = query.data.elem1?.length || 0}
                    {@const count2 = query.data.elem2?.length || 0}
                    <div class="topn-warning" class:fade-out={dashboardState.warningDismissed}>
                        <svg class="warning-icon" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                        <div class="warning-text">
                            {#if count1 < dashboardState.fetchedTopN && count2 < dashboardState.fetchedTopN}
                                <span>System 1: {count1.toLocaleString()} names, System 2: {count2.toLocaleString()} names (requested {dashboardState.fetchedTopN.toLocaleString()})</span>
                            {:else if count1 < dashboardState.fetchedTopN}
                                <span>System 1: Only {count1.toLocaleString()} names available (requested {dashboardState.fetchedTopN.toLocaleString()})</span>
                            {:else}
                                <span>System 2: Only {count2.toLocaleString()} names available (requested {dashboardState.fetchedTopN.toLocaleString()})</span>
                            {/if}
                        </div>
                    </div>
                {/if}
            </div>

            <div class="sex-control">
                <SexToggle />
            </div>

            <div class="separator"></div>

            <div class="alpha-control">
                <AlphaSlider />
            </div>

            <div class="separator"></div>

            <div class="year-control">
                <YearSlider
                    bind:value={dashboardState.period1}
                    min={dashboardState.dateMin}
                    max={dashboardState.dateMax}
                    label="Period 1"
                />
            </div>

            <div class="year-control">
                <YearSlider
                    bind:value={dashboardState.period2}
                    min={dashboardState.dateMin}
                    max={dashboardState.dateMax}
                    label="Period 2"
                />
            </div>

            <PeriodJumpControls />
   
            <button class="load-button" onclick={() => dashboardState.loadData()} disabled={query.isLoading}>
                {#if query.isLoading}
                    <div class="loading-spinner"></div>
                    Loading...
                {:else}
                    Update
                {/if}
            </button>
        {/if}

        {#if isDataReady}
            <DataInfo title={displayTitles} {me} {rtd} {isDataReady}
            />
        {/if}

        <div class="separator"></div>

        <div class="download-control">
            <DownloadSection {isDataReady} />
        </div>
    </div>
</div>

<style>
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

    .sex-control {
        margin-bottom: 1rem;
        margin-top: 0.5rem;
    }

    .topn-control {
        margin-bottom: 1rem;
        margin-top: 0.5rem;
    }

    .download-control {
        margin-bottom: 1rem;
        margin-top: 1rem;
    }

    .topn-warning {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        margin-top: 0.5rem;
        padding: 0.5rem 0.75rem;
        background-color: rgba(251, 191, 36, 0.1);
        border: 1px solid rgba(251, 191, 36, 0.3);
        border-radius: 6px;
        font-size: 0.75rem;
        color: #d97706;
        line-height: 1.4;
        animation: fadeIn 0.3s ease-in;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .warning-icon {
        flex-shrink: 0;
        width: 1rem;
        height: 1rem;
        color: #f59e0b;
        margin-top: 0.1rem;
    }

    .warning-text {
        flex: 1;
    }

    .warning-text span {
        font-weight: 500;
    }

    /* Dark mode support for warning */
    @media (prefers-color-scheme: dark) {
        .topn-warning {
            background-color: rgba(251, 191, 36, 0.15);
            border-color: rgba(251, 191, 36, 0.4);
            color: #fbbf24;
        }

        .warning-icon {
            color: #fbbf24;
        }
    }

    .year-control {
        margin-bottom: 2rem;
        margin-top: 2.5rem;
    }

    .year-control:last-of-type {
        border-bottom: none;
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

    .load-button:hover:not(:disabled) {
        background-color: var(--color-input-bg);
        border-color: var(--color-text);
        transform: translateY(-1px);
    }

    .load-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .loading-spinner {
        width: 1rem;
        height: 1rem;
        border: 2px solid var(--color-border);
        border-top: 2px solid var(--color-text);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .separator {
        border-top: 1px solid var(--color-border);
        margin: 1.5rem -1.5rem;
    }
</style>
