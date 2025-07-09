<script>
    let { alphaIndex = $bindable(), alphas } = $props();
    let alpha = $derived(alphas[alphaIndex]);
</script>

<div class="slider-container">
    <div class="alpha-display">
        <span class="alpha-value">α = {alpha}</span>
    </div>
    <input 
        type="range"
        min="0"
        max={alphas.length - 1}
        bind:value={alphaIndex}
        class="alpha-slider"
    />
    <div class="slider-labels">
        <span>0</span>
        <span>∞</span>
    </div>
</div>

<style>

    .alpha-display {
        text-align: center;
        padding: 0.5rem;
        background-color: transparent;
        border: none;
    }

    .alpha-value {
        font-size: 0.9rem;
        font-weight: 500;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
    }

    .slider-container {
        display: block;
        margin-left: auto;
        margin-right: auto;

        max-width: 300px;
        flex-direction: column;
        gap: 0.25rem;
    }

    .alpha-slider {
        width: 100%;
        height: 3px;
        background-color: var(--border-color);
        border-radius: 2px;
        outline: none;
        cursor: pointer;
        -webkit-appearance: none;
        appearance: none;
    }

    .alpha-slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 12px;
        height: 12px;
        background: var(--accent-color);
        border-radius: 50%;
        cursor: pointer;
    }

    .alpha-slider::-moz-range-thumb {
        width: 12px;
        height: 12px;
        background: var(--accent-color);
        border-radius: 50%;
        cursor: pointer;
        border: none;
    }

    .slider-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.7rem;
        color: var(--text-muted);
        opacity: 0.6;
    }
</style>