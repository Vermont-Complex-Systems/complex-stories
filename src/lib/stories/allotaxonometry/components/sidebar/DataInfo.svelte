<script>
    import { Accordion } from "bits-ui";
    
    let { title, me, rtd, isDataReady } = $props();
</script>

<Accordion.Item value="info" class="accordion-item">
    <Accordion.Header>
        <Accordion.Trigger class="accordion-trigger">
            <span>📊 Dataset Info</span>
        </Accordion.Trigger>
    </Accordion.Header>
    <Accordion.Content class="accordion-content">
        <div class="data-info">
            <div class="info-item">
                <span class="info-label">System 1</span>
                <span class="info-value">{title[0]}</span>
            </div>
            
            <div class="info-item">
                <span class="info-label">System 2</span>
                <span class="info-value">{title[1]}</span>
            </div>
            
            {#if isDataReady}
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
            {/if}
        </div>
    </Accordion.Content>
</Accordion.Item>

<style>
    .data-info {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .info-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem;
        background-color: var(--bg-secondary);
        border-radius: var(--radius);
        border: 1px solid var(--border-color);
    }

    .info-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--text-secondary);
    }

    .info-value {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--text-primary);
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
        background-color: var(--bg-secondary);
        border-radius: var(--radius);
        border: 1px solid var(--border-color);
    }

    .stat-label {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-bottom: 0.25rem;
    }

    .stat-value {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-primary);
    }
</style>