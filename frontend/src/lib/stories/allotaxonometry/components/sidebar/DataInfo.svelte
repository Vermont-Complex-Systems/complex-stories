<script>
    let { title, me, rtd, isDataReady } = $props();
</script>

<div class="data-info">
    <div class="stats">
        <div class="stat">
            <span class="stat-label">Items</span>
            <span class="stat-value">{me[0].ranks.length.toLocaleString()}</span>
        </div>
        <div class="stat">
            <span class="stat-label">Divergence</span>
            <span class="stat-value">{rtd.normalization.toFixed(4)}</span>
        </div>
    </div>
</div>

<style>
    .data-info {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-top: 1rem;
    }


    .stats {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }

    .stat {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0.75rem;
        background-color: var(--color-input-bg);
        border-radius: var(--border-radius);
        border: 1px solid var(--color-border);
    }

    .stat-label {
        font-size: var(--12px);
        color: var(--color-secondary-gray);
        margin-bottom: 0.25rem;
        font-family: var(--font-form);
    }

    .stat-value {
        font-size: var(--14px);
        font-weight: var(--font-weight-bold);
        color: var(--color-fg);
        font-family: var(--font-form);
    }
</style>