<!-- Sidebar.svelte -->
<script>
    import { Accordion, Button, Separator } from "bits-ui";
    import MultiFileUpload from './sidebar/MultiFileUpload.svelte';
    import AlphaControl from './sidebar/AlphaControl.svelte';
    import DataInfo from './sidebar/DataInfo.svelte';
    import StatusCard from './sidebar/StatusCard.svelte';
    import YearSlider from './sidebar/YearSlider.svelte';
    
    import {
        uiState,
        alphas,
        dataState,
        toggleSidebar,
        handleFileUpload,
        loadBabynamesData
    } from '../state.svelte.ts';

    let alphaIndex = $state(7);
    let jumpYears = 5;

    // Arrow navigation functions for both periods
    function shiftBothPeriodsLeft() {
        // Shift period 1
        const range1Size = dataState.period1[1] - dataState.period1[0];
        let newStart1 = dataState.period1[0] - jumpYears;
        let newEnd1 = newStart1 + range1Size;

        if (newStart1 < 1880) {
            newStart1 = 1880;
            newEnd1 = newStart1 + range1Size;
        }

        dataState.period1 = [newStart1, newEnd1];

        // Shift period 2
        const range2Size = dataState.period2[1] - dataState.period2[0];
        let newStart2 = dataState.period2[0] - jumpYears;
        let newEnd2 = newStart2 + range2Size;

        if (newStart2 < 1880) {
            newStart2 = 1880;
            newEnd2 = newStart2 + range2Size;
        }

        dataState.period2 = [newStart2, newEnd2];
    }

    function shiftBothPeriodsRight() {
        // Shift period 1
        const range1Size = dataState.period1[1] - dataState.period1[0];
        let newStart1 = dataState.period1[0] + jumpYears;
        let newEnd1 = newStart1 + range1Size;

        if (newEnd1 > 2020) {
            newEnd1 = 2020;
            newStart1 = newEnd1 - range1Size;
        }

        dataState.period1 = [newStart1, newEnd1];

        // Shift period 2
        const range2Size = dataState.period2[1] - dataState.period2[0];
        let newStart2 = dataState.period2[0] + jumpYears;
        let newEnd2 = newStart2 + range2Size;

        if (newEnd2 > 2020) {
            newEnd2 = 2020;
            newStart2 = newEnd2 - range2Size;
        }

        dataState.period2 = [newStart2, newEnd2];
    }

    function canShiftLeft() {
        return dataState.period1[0] <= 1880 && dataState.period2[0] <= 1880;
    }

    function canShiftRight() {
        return dataState.period1[1] >= 2020 && dataState.period2[1] >= 2020;
    }
</script>

<div class="sidebar-content">
    <div class="sidebar-header">
        {#if !uiState.sidebarCollapsed}
            <h2 class="sidebar-title">Allotaxonograph</h2>
        {/if}
        <Button.Root onclick={toggleSidebar} variant="ghost" size="sm">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                {#if uiState.sidebarCollapsed}
                    <path d="M9 18l6-6-6-6"/>
                {:else}
                    <path d="M15 18l-6-6 6-6"/>
                {/if}
            </svg>
        </Button.Root>
    </div>
    
    {#if !uiState.sidebarCollapsed}
        <div class="sidebar-body">
            <Accordion.Root type="multiple" value={["upload", "alpha", "years", "info"]} class="accordion">
                
                <!-- Direct Click Upload -->
                <MultiFileUpload
                    bind:sys1={dataState.allotax.sys1.dat}
                    bind:sys2={dataState.allotax.sys2.dat}
                    bind:title={dataState.allotax.title}
                    {handleFileUpload}
                    uploadStatus={uiState.uploadStatus}
                    uploadWarnings={uiState.uploadWarnings}
                />
                
                <Separator.Root/>
                
                <!-- Alpha Control -->
                <AlphaControl
                    allotax={dataState.allotax}
                    bind:alphaIndex={alphaIndex}
                    {alphas}
                />
                
                <Separator.Root/>
                
                <!-- Year Range Control -->
                <Accordion.Item value="years" class="accordion-item">
                    <Accordion.Header class="accordion-header">
                        <Accordion.Trigger class="accordion-trigger">
                            Year Ranges: [{dataState.period1[0]}-{dataState.period1[1]}] vs [{dataState.period2[0]}-{dataState.period2[1]}]
                            <svg class="chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="m6 9 6 6 6-6"/>
                            </svg>
                        </Accordion.Trigger>
                    </Accordion.Header>
                    <Accordion.Content class="accordion-content">
                        <YearSlider
                            bind:value={dataState.period1}
                            label="Period 1"
                        />

                        <YearSlider
                            bind:value={dataState.period2}
                            label="Period 2"
                        />

                        <div class="arrow-controls">
                            <button class="arrow-btn" onclick={shiftBothPeriodsLeft} disabled={canShiftLeft()}>
                                ← Shift 5 years back
                            </button>
                            <span class="arrow-separator">•</span>
                            <button class="arrow-btn" onclick={shiftBothPeriodsRight} disabled={canShiftRight()}>
                                Shift 5 years forward →
                            </button>
                        </div>
                    </Accordion.Content>
                </Accordion.Item>

                <Separator.Root/>

                <!-- Submit Button -->
                <div class="submit-section">
                    <Button.Root
                        onclick={loadBabynamesData}
                        class="submit-button"
                        disabled={dataState.isLoading}
                    >
                        {#if dataState.isLoading}
                            <div class="loading-spinner"></div>
                            Loading...
                        {:else}
                            Load Data
                        {/if}
                    </Button.Root>
                </div>

                <Separator.Root/>

                <!-- Data Info -->
                <DataInfo
                    title={dataState.allotax.title}
                    me={dataState.allotax.me}
                    rtd={dataState.allotax.rtd}
                    isDataReady={dataState.allotax.isDataReady}
                />
            </Accordion.Root>

            <StatusCard isDataReady={dataState.allotax.isDataReady} />
        </div>
    {:else}
        <div class="sidebar-collapsed">
            <div class="collapsed-item" title="Current: {dataState.allotax.title[0]} vs {dataState.allotax.title[1]}">
                <div class="comparison-mini">
                    <span class="sys-indicator sys1">1</span>
                    <span class="vs-mini">vs</span>
                    <span class="sys-indicator sys2">2</span>
                </div>
            </div>

            <div class="collapsed-item" title="Alpha: {dataState.allotax.alpha}">
                <div class="alpha-icon">α</div>
                <div class="alpha-mini">{dataState.allotax.alpha.toString().slice(0, 4)}</div>
            </div>

            <div class="collapsed-item" title={dataState.allotax.isDataReady ? 'Ready' : 'Processing...'}>
                <div class="status-dot {dataState.allotax.isDataReady ? 'ready' : 'processing'}"></div>
            </div>
        </div>
    {/if}
</div>

<style>
    .sidebar-content {
        height: 100%;
        display: flex;
        flex-direction: column;
        background-color: var(--color-sidebar-bg);
        border-right: 1px solid var(--color-border);
    }

    .sidebar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        border-bottom: 1px solid var(--color-border);
        background-color: var(--color-sidebar-header-bg);
    }

    .sidebar-title {
        font-size: var(--16px);
        font-weight: var(--font-weight-bold);
        color: var(--color-text-primary);
        margin: 0;
    }

    .sidebar-body {
        flex: 1;
        overflow-y: auto;
        padding: 0;
    }

    /* Collapsed sidebar styles */
    .sidebar-collapsed {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        padding: 1rem 0.5rem;
        align-items: center;
    }

    .collapsed-item {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.25rem;
        padding: 0.5rem;
        border-radius: var(--border-radius);
        cursor: pointer;
        transition: background-color var(--transition-fast) ease;
    }

    .collapsed-item:hover {
        background-color: var(--color-input-bg);
    }

    .comparison-mini {
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }

    .sys-indicator {
        width: 1.25rem;
        height: 1.25rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: var(--10px);
        font-weight: var(--font-weight-bold);
        color: white;
    }

    .sys-indicator.sys1 {
        background-color: var(--color-good-blue);
    }

    .sys-indicator.sys2 {
        background-color: var(--color-electric-green);
    }

    .vs-mini {
        font-size: var(--10px);
        font-weight: var(--font-weight-bold);
        color: var(--color-text-secondary);
    }

    .alpha-icon {
        font-size: 1.25rem;
        font-weight: var(--font-weight-bold);
        color: var(--color-text-primary);
    }

    .alpha-mini {
        font-size: var(--10px);
        color: var(--color-text-secondary);
        font-weight: var(--font-weight-medium);
    }

    .status-dot {
        width: 0.75rem;
        height: 0.75rem;
        border-radius: 50%;
        transition: background-color var(--transition-medium) ease;
    }

    .status-dot.ready {
        background-color: var(--color-electric-green);
        box-shadow: 0 0 0 2px rgba(58, 230, 96, 0.3);
    }

    .status-dot.processing {
        background-color: var(--color-warning);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Accordion styles */
    :global(.accordion) {
        width: 100%;
    }

    :global(.accordion-trigger) {
        width: 100%;
        padding: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: var(--font-weight-medium);
        font-size: var(--14px);
        background-color: transparent;
        border: none;
        cursor: pointer;
        transition: background-color var(--transition-fast) ease;
        color: var(--color-text-primary);
    }

    :global(.accordion-trigger:hover) {
        background-color: var(--color-input-bg);
    }

    :global(.accordion-content) {
        padding: 0 1rem 1rem 1rem;
        overflow: visible;
    }

    .chevron {
        transition: transform var(--transition-fast) ease;
    }

    .submit-section {
        padding: 1rem;
        text-align: center;
    }

    :global(.submit-button) {
        width: 100%;
        background-color: var(--color-good-blue);
        color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1rem;
        font-size: var(--14px);
        font-weight: var(--font-weight-medium);
        cursor: pointer;
        transition: background-color var(--transition-fast) ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    :global(.submit-button:hover:not(:disabled)) {
        background-color: #2563eb;
    }

    :global(.submit-button:disabled) {
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

    .arrow-controls {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 1rem;
        padding: 1rem 0;
        border-top: 1px solid var(--color-border);
        overflow: visible;
    }

    .arrow-btn {
        padding: 0.5rem;
        border: none;
        background: transparent;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: var(--12px);
        transition: all 150ms ease;
        white-space: nowrap;
    }

    .arrow-btn:hover:not(:disabled) {
        transform: scale(1.05);
        background: rgba(0,0,0,0.05);
        border-radius: var(--border-radius);
    }

    .arrow-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .arrow-separator {
        font-size: 16px;
        color: var(--color-text-secondary);
    }
</style>