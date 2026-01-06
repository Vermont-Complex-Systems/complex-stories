<script>
    import { dashboardState } from '../../sidebar-state.svelte.ts';
</script>

<div class="period-jump-controls">
    <div class="arrow-controls">
        <button
            class="arrow-btn"
            onclick={() => dashboardState.shiftBothPeriodsLeft()}
            disabled={!dashboardState.canShiftLeft()}
        >
            ← {dashboardState.jumpYears} yrs back
        </button>
        <span class="arrow-separator">•</span>
        <button
            class="arrow-btn"
            onclick={() => dashboardState.shiftBothPeriodsRight()}
            disabled={!dashboardState.canShiftRight()}
        >
            {dashboardState.jumpYears} yrs forward →
        </button>
    </div>

    <div class="jump-control">
        <label for="jumpYears" class="jump-label">Jump by:</label>
        <input
            id="jumpYears"
            type="number"
            bind:value={dashboardState.jumpYears}
            min="1"
            max="50"
            class="jump-input"
        />
        <span class="jump-unit">years</span>
    </div>
</div>

<style>
    .arrow-controls {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0.75rem 0 0.25rem 0;
        padding: 0.25rem 0;
    }

    .arrow-btn {
        padding: 0.5rem;
        border: none;
        background: transparent;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
        transition: all 150ms ease;
        white-space: nowrap;
        color: var(--color-text);
    }

    .arrow-btn:hover:not(:disabled) {
        transform: scale(1.05);
        background: var(--color-input-bg);
        border-radius: 4px;
    }

    .arrow-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .arrow-separator {
        margin: 0 0.5rem;
        font-size: 16px;
    }

    .jump-control {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin: 0.25rem 0 0.75rem 0;
    }

    .jump-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--color-text);
    }

    .jump-input {
        width: 50px;
        padding: 0.25rem 0.5rem;
        border: 1px solid var(--color-border);
        border-radius: 3px;
        font-size: 0.85rem;
        text-align: center;
        background-color: var(--color-bg);
        color: var(--color-text);
    }

    .jump-input:focus {
        outline: none;
        border-color: var(--color-good-blue, #3b82f6);
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
    }

    .jump-unit {
        font-size: 0.85rem;
        color: var(--color-text-secondary);
    }
</style>
