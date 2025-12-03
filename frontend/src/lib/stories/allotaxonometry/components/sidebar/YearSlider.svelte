<script>
    import { Slider } from "bits-ui";

    let {
        min = 1880,
        max = 2020,
        value = $bindable([1950, 1959]),
        step = 1,
        label = "Period"
    } = $props();

    // Debug: Log when value changes
    $effect(() => {
        console.log(`${label} value changed:`, value);
    });

    function handleValueChange(newValue) {
        console.log('onValueChange triggered:', newValue);
        value = newValue;
    }

    function resetToRange() {
        const currentYear = value[0];
        value = [currentYear - 5, currentYear + 5]; // Create a 5-year range around current value
    }
</script>

<div class="range-filter">
    <div class="slider-header">
        <span class="slider-label">{label}</span>
        {#if value[0] === value[1]}
            <button class="reset-button" onclick={resetToRange}>
                ⟷ Range
            </button>
        {/if}
    </div>

    <Slider.Root
        type="multiple"
        value={value}
        onValueChange={handleValueChange}
        {min}
        {max}
        {step}
        class="slider-root"
    >
        {#snippet children({ thumbItems })}
            <span class="slider-track">
                <Slider.Range class="slider-range" />
            </span>

            {#each thumbItems as { index } (index)}
                <Slider.Thumb
                    {index}
                    class="slider-thumb {index === 0 ? 'thumb-left' : 'thumb-right'} {value[0] === value[1] ? 'same-value' : ''}"
                    disabled={value[0] === value[1] && index === 1}
                >
                    {#if index === 0}
                        <span class="year-label-left">{value[index]}</span>

                        <!-- UPDATED HERE -->
                        <span
                            class="bracket-handle"
                            style:pointer-events={value[0] === value[1] && index === 1 ? "none" : "auto"}
                        >|</span>

                    {:else if value[0] !== value[1]}
                        <!-- UPDATED HERE -->
                        <span
                            class="bracket-handle"
                            style:pointer-events={value[0] === value[1] && index === 1 ? "none" : "auto"}
                        >|</span>

                        <span class="year-label-right">{value[index]}</span>
                    {/if}
                </Slider.Thumb>
            {/each}

        {/snippet}
    </Slider.Root>
</div>

<style>
    .range-filter {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        width: 100%;
    }

    .slider-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    .slider-label {
        font-size: var(--12px);
        font-weight: var(--font-weight-medium);
        color: var(--color-text-primary);
    }

    .reset-button {
        font-size: var(--10px);
        padding: 0.25rem 0.5rem;
        border: none;
        background: transparent;
        cursor: pointer;
        transition: all 150ms ease;
        color: var(--color-text-secondary);
    }

    .reset-button:hover {
        color: var(--color-text-primary);
    }

    .year-label-left {
        position: absolute;
        top: -0.5rem;
        right: 1.5rem;
        font-size: 11px;
        pointer-events: none;
    }

    .year-label-right {
        position: absolute;
        top: -0.5rem;
        left: 1.5rem;
        font-size: 11px;
        pointer-events: none;
    }

    :global(.slider-root) {
        position: relative;
        display: flex;
        align-items: center;
        width: 100%;
        height: 2rem;
        touch-action: none;
    }

    .slider-track {
        position: relative;
        flex: 1;
        height: 0.5rem;
        background: #e5e7eb;
        border-radius: 9999px;
        cursor: default;
        overflow: hidden;
        pointer-events: none;
    }

    :global(.slider-range) {
        position: absolute;
        height: 100%;
        background: var(--color-good-blue);
        border-radius: 9999px;
        pointer-events: none;
    }

    :global(.slider-thumb) {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2rem;
        height: 2rem;
        background: transparent;
        border: none;
        transition: all 150ms ease;
        position: relative;
        z-index: 10;
        /* Allow clicks to pass through most of the thumb area */
        pointer-events: none;
    }

    .bracket-handle {
        font-size: 1.5rem;
        font-weight: var(--font-weight-bold);
        color: var(--color-good-blue);
        line-height: 1;
        user-select: none;
        text-shadow: 0 0 2px rgba(255,255,255,0.8);
        cursor: col-resize;
        /* Only the bracket text is draggable */
        pointer-events: auto;
        padding: 4px;
    }

    .bracket-handle:hover {
        transform: scale(1.1);
    }


    :global(.slider-thumb:focus-visible) {
        outline: 2px solid var(--color-good-blue);
        outline-offset: 2px;
        border-radius: var(--border-radius);
    }
</style>