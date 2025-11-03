<script>
    import { Info, ChevronDown } from "@lucide/svelte";

    let { title = "Methodology", text, isCollapsed = true } = $props();
</script>

<div class="methodology-info">
    <button class="info-header clickable" onclick={() => isCollapsed = !isCollapsed} type="button">
        <Info size={12} />
        <span class="info-label">{title}</span>
        <div class="chevron" class:collapsed={isCollapsed}>
            <ChevronDown size={12} />
        </div>
    </button>
    {#if !isCollapsed}
        <div class="detail-content">
            <p>{@html text}</p>
        </div>
    {/if}
</div>

<style>
    .methodology-info {
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        margin-left: -0.75rem;
        margin-right: -0.75rem;
        padding: 0.5rem;
        background: #fffbf0;
        border: 1px solid #f0e68c;
        border-radius: 4px;
        font-size: var(--font-size-xsmall);
    }

    :global(.dark) .methodology-info {
        background: #2a2a2a;
        border-color: #444;
    }

    .info-header {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        margin-bottom: 0.25rem;
        background: none;
        border: none;
        width: 100%;
        text-align: left;
    }

    .info-header.clickable {
        cursor: pointer;
        justify-content: space-between;
        padding: 0.25rem;
        border-radius: 3px;
        transition: background-color 0.2s ease;
    }

    .info-header.clickable:hover {
        background-color: rgba(0, 0, 0, 0.05);
    }

    :global(.dark) .info-header.clickable:hover {
        background-color: rgba(255, 255, 255, 0.05);
    }

    .chevron {
        transition: transform 0.2s ease;
        flex-shrink: 0;
    }

    .chevron.collapsed {
        transform: rotate(-90deg);
    }

    .info-label {
        font-weight: bold;
        font-size: var(--font-size-xsmall);
        color: var(--color-fg, #333);
    }

    .detail-content {
        margin-top: 0.25rem;
    }

    .detail-content :global(p) {
        margin: 0;
        line-height: 1.3;
        color: var(--color-fg, #333);
        font-size: var(--font-size-xsmall);
    }

    .detail-content :global(a) {
        color: var(--color-primary);
        text-decoration: underline;
    }
</style>