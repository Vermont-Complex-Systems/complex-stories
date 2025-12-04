<script>
    let {
        message = 'Loading...',
        isError = false,
        errorMessage = 'No data available. Please select valid dates.'
    } = $props();
</script>

<div class="loading-container">
    <div class="loading-content">
        {#if isError}
            <p class="error-text">{errorMessage}</p>
        {:else}
            <div class="spinner"></div>
            <p class="loading-text">{message}</p>
        {/if}
    </div>
</div>

<style>
    .loading-container {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: calc(100vh - 200px);
    }

    .loading-content {
        text-align: center;
    }

    .spinner {
        width: 2rem;
        height: 2rem;
        border: 3px solid var(--color-border, #e0e0e0);
        border-top: 3px solid var(--color-good-blue, #3b82f6);
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
        color: var(--color-fg, #333);
        margin: 0;
    }

    .error-text {
        font-size: 1rem;
        color: #dc2626;
        margin: 0;
    }
</style>
