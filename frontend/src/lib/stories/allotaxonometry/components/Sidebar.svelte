<script lang="ts">
    import YearSlider from './sidebar/YearSlider.svelte';
    import AlphaSlider from './sidebar/AlphaSlider.svelte';
    import LocationSelector from './sidebar/LocationSelector.svelte';
    import SexToggle from './sidebar/SexToggle.svelte';
    import TopNSelector from './sidebar/TopNSelector.svelte';
    import MultiFileUpload from './sidebar/MultiFileUpload.svelte';
    import DataInfo from './sidebar/DataInfo.svelte';
    import DownloadSection from './sidebar/DownloadSection.svelte';
    import * as stateModule from '../sidebar-state.svelte.ts';

    // Props passed from parent
    let {
        query,
        instance,
        displayTitles,
        me,
        rtd,
        isDataReady,
        actualCounts,
        showTopNWarning
    } = $props();
</script>

<div class="sidebar-content">
    <div class="sidebar-header">
        <h2 class="sidebar-title">Allotaxonograph</h2>
    </div>

    <div class="sidebar-body">
        <MultiFileUpload
            bind:sys1={stateModule.state.uploadedSys1}
            bind:sys2={stateModule.state.uploadedSys2}
            bind:title={stateModule.state.uploadedTitle}
            handleFileUpload={stateModule.handleFileUpload}
            uploadStatus={stateModule.state.uploadStatus}
            uploadWarnings={stateModule.state.uploadWarnings}
        />

        <div class="separator"></div>

        {#if !stateModule.derived.hasUploadedFiles}
            <div class="location-control">
                <LocationSelector
                    bind:value={stateModule.state.selectedLocation}
                    label="Location"
                    adapter={stateModule.state.adapter}
                    isLoading={stateModule.state.locationsLoading}
                    isError={stateModule.state.locationsError}
                />
            </div>

            <div class="topn-control">
                <TopNSelector bind:value={stateModule.state.selectedTopN} />
                
                {#if showTopNWarning && !stateModule.state.warningDismissed && actualCounts}
                    {@const counts = actualCounts}
                    <div class="topn-warning" class:fade-out={stateModule.state.warningDismissed}>
                        <svg class="warning-icon" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                        <div class="warning-text">
                            {#if counts.period1 < stateModule.state.fetchedTopN && counts.period2 < stateModule.state.fetchedTopN}
                                <span>System 1: {counts.period1.toLocaleString()} names, System 2: {counts.period2.toLocaleString()} names (requested {stateModule.state.fetchedTopN.toLocaleString()})</span>
                            {:else if counts.period1 < stateModule.state.fetchedTopN}
                                <span>System 1: Only {counts.period1.toLocaleString()} names available (requested {stateModule.state.fetchedTopN.toLocaleString()})</span>
                            {:else}
                                <span>System 2: Only {counts.period2.toLocaleString()} names available (requested {stateModule.state.fetchedTopN.toLocaleString()})</span>
                            {/if}
                        </div>
                    </div>
                {/if}
            </div>
            
            <div class="sex-control">
                <SexToggle bind:sex={stateModule.state.selectedSex} />
            </div>


            <div class="separator"></div>
        {/if}

        <div class="alpha-control">
            <AlphaSlider
                alphas={stateModule.alphas}
                alphaIndex={stateModule.state.alphaIndex}
                currentAlpha={stateModule.derived.currentAlpha}
                onAlphaChange={stateModule.onAlphaChange}
            />
        </div>
        
        <div class="separator"></div>

        {#if !stateModule.derived.hasUploadedFiles}
            <div class="year-control">
                <YearSlider
                    bind:value={stateModule.state.period1}
                    min={stateModule.derived.dateMin}
                    max={stateModule.derived.dateMax}
                    label="Period 1"
                />
            </div>

            <div class="year-control">
                <YearSlider
                    bind:value={stateModule.state.period2}
                    min={stateModule.derived.dateMin}
                    max={stateModule.derived.dateMax}
                    label="Period 2"
                />
            </div>

            <div class="arrow-controls">
                <button class="arrow-btn" onclick={stateModule.shiftBothPeriodsLeft} disabled={!stateModule.canShiftLeft()}>
                    ← {stateModule.state.jumpYears} yrs back
                </button>
                <span class="arrow-separator">•</span>
                <button class="arrow-btn" onclick={stateModule.shiftBothPeriodsRight} disabled={!stateModule.canShiftRight()}>
                    {stateModule.state.jumpYears} yrs forward →
                </button>
            </div>

            <div class="jump-control">
                <label for="jumpYears" class="jump-label">Jump by:</label>
                <input
                    id="jumpYears"
                    type="number"
                    bind:value={stateModule.state.jumpYears}
                    min="1"
                    max="50"
                    class="jump-input"
                />
                <span class="jump-unit">years</span>
            </div>
        {/if}

        {#if !stateModule.derived.hasUploadedFiles}
            <button class="load-button" onclick={stateModule.loadData} disabled={query.isLoading}>
                {#if query.isLoading}
                    <div class="loading-spinner"></div>
                    Loading...
                {:else}
                    Update
                {/if}
            </button>
        {/if}

        {#if isDataReady}
            <DataInfo
                title={displayTitles}
                {me}
                {rtd}
                {isDataReady}
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
        color: var(--color-text);
    }

    .arrow-btn:hover:not(:disabled) {
        transform: scale(1.05);
        background: var(--color-input-bg);
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
        color: var(--color-text);
    }

    .jump-input {
        width: 50px;
        padding: 0.25rem 0.5rem;
        border: 1px solid var(--color-border);
        border-radius: 3px;
        font-size: 0.85rem;
        text-align: center;
        background-color: var(--color-bg);
        color: var(--color-text);
    }

    .jump-input:focus {
        outline: none;
        border-color: var(--color-good-blue, #3b82f6);
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
    }

    .jump-unit {
        font-size: 0.85rem;
        color: var(--color-text-secondary);
    }

    .separator {
        border-top: 1px solid var(--color-border);
        margin: 1.5rem -1.5rem;
    }
</style>
