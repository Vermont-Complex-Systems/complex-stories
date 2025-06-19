<script>
    let { isDataReady } = $props();
</script>

<div class="status-card">
    <div class="status-indicator">
        <div class="status-dot {isDataReady ? 'ready' : 'processing'}"></div>
        <span class="status-text">
            {isDataReady ? 'Ready' : 'Processing...'}
        </span>
    </div>
</div>

<style>
    .status-card {
        padding: 1rem;
        border: 1px solid var(--border-color);
        border-radius: var(--radius);
        background-color: var(--bg-primary);
    }

    .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.75rem;
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

    .status-text {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--text-primary);
    }
</style>