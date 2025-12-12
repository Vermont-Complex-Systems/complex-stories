<script>
    let {
        value = $bindable(10000),
        label = "Top N tokens",
        min = 100,
        max = 50000,
        step = 100
    } = $props();

    function handleChange(event) {
        const newValue = parseInt(event.target.value);
        if (!isNaN(newValue)) {
            value = Math.max(min, Math.min(max, newValue));
        }
    }
</script>

<div class="topn-selector">
    <div class="selector-header">
        <span class="selector-label">{label}</span>
        <!-- <span class="current-value">{value.toLocaleString()}</span> -->
    </div>

    <div class="selector-control">
        <input
            type="number"
            {value}
            onchange={handleChange}
            {min}
            {max}
            {step}
            class="topn-input"
        />
    </div>
</div>

<style>
    .topn-selector {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        width: 100%;
    }

    .selector-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.25rem;
    }

    .selector-label {
        font-size: var(--12px, 0.75rem);
        font-weight: var(--font-weight-medium, 500);
        color: var(--color-text-primary);
    }

    .current-value {
        font-size: var(--11px, 0.69rem);
        color: var(--color-text-secondary);
        font-weight: var(--font-weight-medium, 500);
    }

    .selector-control {
        position: relative;
    }

    .topn-input {
        width: 100%;
        padding: 0.75rem 1rem;
        border: 1px solid var(--color-border);
        border-radius: 6px;
        font-size: 0.875rem;
        background-color: var(--color-bg);
        color: var(--color-text-primary);
        transition: all 0.15s ease;
        font-family: var(--sans, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif);
    }

    .topn-input:hover {
        border-color: var(--color-good-blue, #3b82f6);
        box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.1);
    }

    .topn-input:focus {
        outline: none;
        border-color: var(--color-good-blue, #3b82f6);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    /* Remove spinner arrows in Chrome, Safari, Edge, Opera */
    .topn-input::-webkit-outer-spin-button,
    .topn-input::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }

    /* Remove spinner arrows in Firefox */
    .topn-input[type=number] {
        -moz-appearance: textfield;
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .topn-input {
            padding: 1rem;
            font-size: 1rem;
        }
    }
</style>
