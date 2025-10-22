<!-- Sidebar.svelte -->
<script>
    import { Accordion, Button, Separator } from "bits-ui";
    import MultiFileUpload from './sidebar/MultiFileUpload.svelte';
    import AlphaControl from './sidebar/AlphaControl.svelte';
    import DataInfo from './sidebar/DataInfo.svelte';
    import StatusCard from './sidebar/StatusCard.svelte';
    
    import { 
        allotax,
        uiState,
        alphas,
        toggleSidebar,
        handleFileUpload
    } from '../state.svelte.ts';

    let alphaIndex = $state(7);
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
            <Accordion.Root type="multiple" value={["upload", "alpha", "info"]} class="accordion">
                
                <!-- Direct Click Upload -->
                <MultiFileUpload 
                    bind:sys1={allotax.sys1}
                    bind:sys2={allotax.sys2}
                    bind:title={allotax.title}
                    {handleFileUpload}
                    uploadStatus={uiState.uploadStatus}
                    uploadWarnings={uiState.uploadWarnings}
                />
                
                <Separator.Root/>
                
                <!-- Alpha Control -->
                <AlphaControl 
                    {allotax}
                    bind:alphaIndex={alphaIndex}
                    {alphas} 
                />
                
                <Separator.Root/>
                
                <!-- Data Info -->
                <DataInfo 
                    title={allotax.title} 
                    me={allotax.me} 
                    rtd={allotax.rtd} 
                    isDataReady={allotax.isDataReady} 
                />
            </Accordion.Root>

            <StatusCard isDataReady={allotax.isDataReady} />
        </div>
    {:else}
        <div class="sidebar-collapsed">
            <div class="collapsed-item" title="Current: {allotax.title[0]} vs {allotax.title[1]}">
                <div class="comparison-mini">
                    <span class="sys-indicator sys1">1</span>
                    <span class="vs-mini">vs</span>
                    <span class="sys-indicator sys2">2</span>
                </div>
            </div>
            
            <div class="collapsed-item" title="Alpha: {allotax.alpha}">
                <div class="alpha-icon">α</div>
                <div class="alpha-mini">{allotax.alpha.toString().slice(0, 4)}</div>
            </div>
            
            <div class="collapsed-item" title={allotax.isDataReady ? 'Ready' : 'Processing...'}>
                <div class="status-dot {allotax.isDataReady ? 'ready' : 'processing'}"></div>
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
    }
</style>