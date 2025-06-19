<script>
    import { Accordion, Button, Separator } from "bits-ui";
    import UploadSection from './sidebar/UploadSection.svelte';
    import AlphaControl from './sidebar/AlphaControl.svelte';
    import DataInfo from './sidebar/DataInfo.svelte';
    import StatusCard from './sidebar/StatusCard.svelte';
    
    let { 
        collapsed = false,
        onToggle,
        sys1 = $bindable(null),
        sys2 = $bindable(null),
        title = $bindable(['System 1', 'System 2']),
        alpha = $bindable(0.58),
        alphaIndex = $bindable(7),
        alphas,
        handleFileUpload,
        uploadStatus,
        me,
        rtd,
        isDataReady
    } = $props();
</script>

<aside class="sidebar" style="width: {collapsed ? '4rem' : '15rem'}">
    <div class="sidebar-header">
        {#if !collapsed}
            <h2 class="sidebar-title">Allotaxonograph</h2>
        {/if}
        <Button.Root onclick={onToggle} variant="ghost" size="sm">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                {#if collapsed}
                    <path d="M9 18l6-6-6-6"/>
                {:else}
                    <path d="M15 18l-6-6 6-6"/>
                {/if}
            </svg>
        </Button.Root>
    </div>
    
    {#if !collapsed}
        <div class="sidebar-content">
            <Accordion.Root type="multiple" value={["upload", "alpha", "info"]} class="accordion">
                <UploadSection bind:sys1 bind:sys2 bind:title {handleFileUpload} {uploadStatus} />
                <Separator.Root/>
                <AlphaControl bind:alpha bind:alphaIndex {alphas} />
                <Separator.Root/>
                <DataInfo {title} {me} {rtd} {isDataReady} />
            </Accordion.Root>

            <StatusCard {isDataReady} />
        </div>
    {:else}
        <!-- Collapsed sidebar content -->
        <div class="sidebar-collapsed">
            <div class="collapsed-item" title="Alpha: {alpha}">
                <div class="alpha-icon">α</div>
                <div class="alpha-mini">{alpha.toString().slice(0, 4)}</div>
            </div>
            
            <div class="collapsed-item" title={isDataReady ? 'Ready' : 'Processing...'}>
                <div class="status-dot {isDataReady ? 'ready' : 'processing'}"></div>
            </div>

            <div class="collapsed-item" title="Upload Data">
                📁
            </div>

            <div class="collapsed-item" title="Dataset Info">
                📊
            </div>
        </div>
    {/if}
</aside>


<style>
    /* Sidebar styles */
    .sidebar {
        background-color: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
        transition: width 0.3s ease;
        display: flex;
        flex-direction: column;
    }

    .sidebar-header {
        padding: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid var(--border-color);
        min-height: 80px;
    }

    /* When collapsed, center the toggle button */
    .sidebar[style*="4rem"] .sidebar-header {
        padding: 1rem;
        justify-content: center;
    }

    .sidebar-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
        color: var(--text-primary);
    }

    .sidebar-content {
        padding: 1.5rem;
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        overflow-y: auto;
    }

    .sidebar-collapsed {
        padding: 1rem 0.5rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }

    .collapsed-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.25rem;
        padding: 0.5rem;
        border-radius: var(--radius);
        transition: background-color 0.2s ease;
        cursor: pointer;
    }

    .collapsed-item:hover {
        background-color: var(--border-color);
    }

    .alpha-icon {
        width: 2rem;
        height: 2rem;
        background-color: var(--accent-color);
        border-radius: var(--radius);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.875rem;
        font-weight: 600;
    }

    .alpha-mini {
        font-size: 0.75rem;
        font-family: monospace;
        color: var(--text-secondary);
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }

    .status-dot.ready {
        background-color: var(--success-color);
    }

    .status-dot.processing {
        background-color: var(--warning-color);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

</style>