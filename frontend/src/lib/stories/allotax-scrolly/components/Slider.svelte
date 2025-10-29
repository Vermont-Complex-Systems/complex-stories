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
        color: #333;
        margin-bottom: 0.25rem;
    }

    .slider-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        max-width: 300px;
        gap: 0.5rem;
        padding: 1rem;
    }

    .alpha-slider {
        width: 100%;
        height: 6px;
        background-color: #ddd;
        border-radius: 3px;
        outline: none;
        cursor: pointer;
        -webkit-appearance: none;
        appearance: none;
    }

    .alpha-slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 20px;
        height: 20px;
        background: #007cba;
        border-radius: 50%;
        cursor: pointer;
    }

    .alpha-slider::-moz-range-thumb {
        width: 20px;
        height: 20px;
        background: #007cba;
        border-radius: 50%;
        cursor: pointer;
        border: none;
    }

    .slider-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.7rem;
        color: #666;
        opacity: 0.6;
    }
</style>