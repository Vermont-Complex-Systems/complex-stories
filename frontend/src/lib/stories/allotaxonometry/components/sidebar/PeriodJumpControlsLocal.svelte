<script>
    let {
        period1 = $bindable([1895, 1895]),
        period2 = $bindable([1968, 1968]),
        dateMin = 1880,
        dateMax = 2023,
        onJump = () => {}
    } = $props();

    let jumpYears = $state(10);

    function calculateShiftedRange(currentRange, shiftAmount, minBound, maxBound) {
        const rangeSize = currentRange[1] - currentRange[0];
        let newStart = currentRange[0] + shiftAmount;
        let newEnd = newStart + rangeSize;

        // Clamp to lower bound
        if (newStart < minBound) {
            newStart = minBound;
            newEnd = newStart + rangeSize;
        }

        // Clamp to upper bound
        if (newEnd > maxBound) {
            newEnd = maxBound;
            newStart = newEnd - rangeSize;
        }

        return [newStart, newEnd];
    }

    function shiftBothPeriodsLeft() {
        period1 = calculateShiftedRange(period1, -jumpYears, dateMin, dateMax);
        period2 = calculateShiftedRange(period2, -jumpYears, dateMin, dateMax);
        console.log('Jumped left:', jumpYears, 'years');
        // Auto-trigger the update after a short delay
        setTimeout(() => onJump(), 0);
    }

    function shiftBothPeriodsRight() {
        period1 = calculateShiftedRange(period1, jumpYears, dateMin, dateMax);
        period2 = calculateShiftedRange(period2, jumpYears, dateMin, dateMax);
        console.log('Jumped right:', jumpYears, 'years');
        // Auto-trigger the update after a short delay
        setTimeout(() => onJump(), 0);
    }

    const canShiftLeft = $derived(period1[0] > dateMin || period2[0] > dateMin);
    const canShiftRight = $derived(period1[1] < dateMax || period2[1] < dateMax);
</script>

<div class="period-jump-controls">
    <div class="arrow-controls">
        <button
            class="arrow-btn"
            onclick={shiftBothPeriodsLeft}
            disabled={!canShiftLeft}
        >
            ← {jumpYears} yrs back
        </button>
        <span class="arrow-separator">•</span>
        <button
            class="arrow-btn"
            onclick={shiftBothPeriodsRight}
            disabled={!canShiftRight}
        >
            {jumpYears} yrs forward →
        </button>
    </div>

    <div class="jump-control">
        <label for="jumpYears" class="jump-label">Jump by:</label>
        <input
            id="jumpYears"
            type="number"
            bind:value={jumpYears}
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

    /* Remove spinner arrows */
    .jump-input::-webkit-outer-spin-button,
    .jump-input::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }

    .jump-input[type=number] {
        -moz-appearance: textfield;
    }
</style>
