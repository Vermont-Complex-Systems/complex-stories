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

        // If we're in single-year mode, enforce that both values stay the same
        if (value[0] === value[1] && newValue[0] !== newValue[1]) {
            // Don't allow range creation - keep the year that was moved
            const movedYear = newValue[0] !== value[0] ? newValue[0] : newValue[1];
            value = [movedYear, movedYear];
        } else {
            value = newValue;
        }
    }

    function resetToRange() {
        const currentYear = value[0];
        value = [currentYear - 5, currentYear + 5]; // Create a 5-year range around current value
    }

    // Handle single year dragging
    let isDraggingSingleYear = $state(false);
    let dragStartX = $state(0);
    let dragStartValue = $state(0);

    function handleRangeMouseDown(e) {
        if (value[0] === value[1]) {
            isDraggingSingleYear = true;
            dragStartX = e.clientX;
            dragStartValue = value[0];

            const handleMouseMove = (moveEvent) => {
                if (!isDraggingSingleYear) return;

                const deltaX = moveEvent.clientX - dragStartX;
                const rangeWidth = e.currentTarget.parentElement.offsetWidth;
                const totalRange = max - min;
                const deltaValue = Math.round((deltaX / rangeWidth) * totalRange);

                const newYear = Math.max(min, Math.min(max, dragStartValue + deltaValue));
                value = [newYear, newYear];
            };

            const handleMouseUp = () => {
                isDraggingSingleYear = false;
                document.removeEventListener('mousemove', handleMouseMove);
                document.removeEventListener('mouseup', handleMouseUp);
            };

            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
        }
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
        {#snippet children({ thumbItems, tickItems })}
            <span class="slider-track">
                <Slider.Range
                    class="slider-range {value[0] === value[1] ? 'single-year-draggable' : ''}"
                    onmousedown={handleRangeMouseDown}
                />
            </span>

            {#each thumbItems as { index } (index)}
                <Slider.Thumb
                    {index}
                    class="slider-thumb {index === 0 ? 'thumb-left' : 'thumb-right'} {value[0] === value[1] ? 'same-value' : ''}"
                    disabled={value[0] === value[1]}
                >
                    {#if index === 0}
                        <span class="year-label-left">{value[index]}</span>

                        <span
                            class="bracket-handle"
                            style:pointer-events={value[0] === value[1] ? "none" : "auto"}
                        >|</span>

                    {:else if value[0] !== value[1]}
                        <span
                            class="bracket-handle"
                            style:pointer-events={value[0] === value[1] ? "none" : "auto"}
                        >|</span>

                        <span class="year-label-right">{value[index]}</span>
                    {/if}
                </Slider.Thumb>
            {/each}

            <!-- Add tick marks at min and max -->
            <Slider.Tick index={0} />
            <Slider.TickLabel index={0} position="bottom">{min}</Slider.TickLabel>

            <Slider.Tick index={tickItems.length - 1} />
            <Slider.TickLabel index={tickItems.length - 1} position="bottom">{max}</Slider.TickLabel>

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

    :global(.slider-range.single-year-draggable) {
        pointer-events: auto;
        cursor: grab;
        transition: all 150ms ease;
    }

    :global(.slider-range.single-year-draggable:hover) {
        background: var(--color-good-blue-hover);
        transform: scaleY(1.2);
    }

    :global(.slider-range.single-year-draggable:active) {
        cursor: grabbing;
        transform: scaleY(1.3);
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

    :global(.slider-thumb[disabled]) .bracket-handle {
        opacity: 0.5;
        cursor: not-allowed;
    }

    :global(.slider-thumb[disabled]) .bracket-handle:hover {
        transform: none;
    }


    :global(.slider-thumb:focus-visible) {
        outline: 2px solid var(--color-good-blue);
        outline-offset: 2px;
        border-radius: var(--border-radius);
    }

</style>