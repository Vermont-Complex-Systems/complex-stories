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
                        
                        {#if value[0] === value[1]}
                            <button class="reset-on-bracket-label" onclick={resetToRange}>range</button>
                            <button class="reset-on-bracket" onclick={resetToRange}>⟷</button>
                        {/if}

                        <span class="bracket-handle">|</span>

                        <span class="year-label-left">{value[index]}</span>

                    {:else if value[0] !== value[1]}
                        <span class="bracket-handle">|</span>
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

    .reset-on-bracket-label,
    .reset-on-bracket {
        position: absolute;
        top: -2rem;       /* moves it above the bracket */
        left: 50%;
        transform: translateX(-50%);
        background: transparent;
        border: none;
        padding: 0;
        font-size: 20px;
        cursor: pointer;
        pointer-events: auto; /* allow clicking */
        z-index: 20;
        color: var(--color-text);
    }

    .reset-on-bracket-label {
        font-size: 10px;
    }

    .year-label-left {
        position: absolute;
        top: 0.1rem;
        right: 0.75rem;
        font-size: 11px;
        pointer-events: none;
        color: var(--color-text);
    }

    .year-label-right {
        position: absolute;
        top: 0.1rem;
        left: 0.75rem;
        font-size: 11px;
        pointer-events: none;
        color: var(--color-text);
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
        height: 0.8rem;
        background: var(--color-border);
        border-radius: 9999px;
        cursor: default;
        overflow: hidden;
        pointer-events: none;
    }

    :global(.slider-range) {
        position: absolute;
        height: 100%;
        background: #555;
        border-radius: 9999px;
        pointer-events: none;
    }

    :global(.dark .slider-range) {
        background: #999;
    }

    :global(.slider-range.single-year-draggable) {
        pointer-events: auto;
        cursor: grab;
        transition: all 150ms ease;
    }

    :global(.slider-range.single-year-draggable:hover) {
        background: #333;
        transform: scaleY(1.2);
    }

    :global(.dark .slider-range.single-year-draggable:hover) {
        background: #bbb;
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
        background: transparent !important;
        border: none !important;
        transition: all 150ms ease;
        position: relative;
        z-index: 10;
        /* Allow clicks to pass through most of the thumb area */
        pointer-events: none;
        /* Completely hide any default thumb styling from bits-ui */
        outline: none !important;
        box-shadow: none !important;
        /* Remove any default positioning offsets */
        top: 0 !important;
        transform: translateY(0.15rem) !important; /* Align with slider track center */
    }

    /* Hide any nested thumb elements that bits-ui might create */
    :global(.slider-thumb::before),
    :global(.slider-thumb::after),
    :global(.slider-thumb [data-slider-thumb]) {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
    }

    /* Aggressively hide any default thumb background or borders */
    :global(.slider-thumb > *:not(.bracket-handle):not(.year-label-left):not(.year-label-right):not(.reset-on-bracket):not(.reset-on-bracket-label)) {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
    }

    .bracket-handle {
        font-size: 1.5rem;
        font-weight: var(--font-weight-bold);
        line-height: 0.75;
        user-select: none;
        color: var(--color-text);
        cursor: col-resize;
        /* Only the bracket text is draggable */
        pointer-events: auto;
        padding: 5px;
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