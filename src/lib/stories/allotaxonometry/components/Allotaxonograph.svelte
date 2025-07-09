<script>
    import { Dashboard } from 'allotaxonometer-ui';
    import { allotax } from '../state.svelte.ts';
</script>

{#if allotax.isDataReady}
    <Dashboard {...allotax} />
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