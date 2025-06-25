<script>
    import { Dashboard } from 'allotaxonometer-ui';
    import { dataProcessor, uiState } from './state.svelte.ts';

    let { height = 815 } = $props();

    // Simple derived dimensions
    let dashboardWidth = $derived(uiState.sidebarCollapsed ? 1200 : 900);
    let wordshiftWidth = $derived(uiState.sidebarCollapsed ? 550 : 400);
</script>

{#if dataProcessor.isDataReady}
    <Dashboard 
        dat={dataProcessor.dat}
        alpha={dataProcessor.alpha}
        divnorm={dataProcessor.rtd?.normalization}
        barData={dataProcessor.barData}
        balanceData={dataProcessor.balanceData}
        title={uiState.title}
        maxlog10={dataProcessor.maxlog10}
        max_count_log={dataProcessor.max_count_log}
        height={height}
        width={dashboardWidth}
        DiamondHeight={600}
        DiamondWidth={600}
        marginInner={160}
        marginDiamond={40}
        WordshiftWidth={wordshiftWidth}
        xDomain={[-dataProcessor.max_shift * 1.5, dataProcessor.max_shift * 1.5]}
        class="dashboard"
    />
{:else}
    <div class="loading-container">
        <div class="loading-content">
            <div class="spinner"></div>
            <p class="loading-text">Loading allotaxonograph...</p>
        </div>
    </div>
{/if}

<style>
    .loading-container {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        min-height: 400px;
    }

    .loading-content {
        text-align: center;
    }

    .spinner {
        width: 2rem;
        height: 2rem;
        border: 3px solid var(--color-border);
        border-top: 3px solid var(--color-good-blue);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .loading-text {
        font-size: 1rem;
        color: var(--color-fg);
        margin: 0;
        font-family: var(--font-body);
    }
</style>