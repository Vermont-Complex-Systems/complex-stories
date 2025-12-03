<script>
    import { Slider } from "bits-ui";

    let {
        period1 = $bindable([1950, 1959]),
        period2 = $bindable([1990, 1999]),
        minYear = 1880,
        maxYear = 2020
    } = $props();

    // Convert periods to slider format [start, end]
    let period1Range = $state([...period1]);
    let period2Range = $state([...period2]);

    // Update bindable props when internal state changes
    $effect(() => {
        period1[0] = period1Range[0];
        period1[1] = period1Range[1];
    });

    $effect(() => {
        period2[0] = period2Range[0];
        period2[1] = period2Range[1];
    });
</script>

<div class="timeline-container">
    <!-- Period 1 Timeline -->
    <div class="timeline-section">
        <div class="timeline-header">
            <span class="period-title">Period 1</span>
            <span class="period-display">{period1Range[0]} - {period1Range[1]} ({period1Range[1] - period1Range[0] + 1} years)</span>
        </div>

        <div class="timeline">
            <!-- Timeline labels -->
            <div class="timeline-labels">
                <span class="year-label">{minYear}</span>
                <span class="year-label center">1950</span>
                <span class="year-label center">2000</span>
                <span class="year-label">{maxYear}</span>
            </div>

            <!-- Period 1 Slider -->
            <Slider.Root
                type="multiple"
                value={period1Range}
                onValueChange={(value) => period1Range = value}
                min={minYear}
                max={maxYear}
                step={1}
                class="period-slider"
            >
                {#snippet children({ thumbItems, tickItems })}
                    <span class="slider-track">
                        <Slider.Range class="slider-range period-1-range" />
                    </span>

                    {#each thumbItems as { index } (index)}
                        <Slider.Thumb {index} class="slider-thumb period-1-thumb">
                            <div class="thumb-bracket">[</div>
                        </Slider.Thumb>
                    {/each}
                {/snippet}
            </Slider.Root>
        </div>
    </div>

    <!-- Period 2 Timeline -->
    <div class="timeline-section">
        <div class="timeline-header">
            <span class="period-title">Period 2</span>
            <span class="period-display">{period2Range[0]} - {period2Range[1]} ({period2Range[1] - period2Range[0] + 1} years)</span>
        </div>

        <div class="timeline">
            <!-- Timeline labels -->
            <div class="timeline-labels">
                <span class="year-label">{minYear}</span>
                <span class="year-label center">1950</span>
                <span class="year-label center">2000</span>
                <span class="year-label">{maxYear}</span>
            </div>

            <!-- Period 2 Slider -->
            <Slider.Root
                type="multiple"
                value={period2Range}
                onValueChange={(value) => period2Range = value}
                min={minYear}
                max={maxYear}
                step={1}
                class="period-slider"
            >
                {#snippet children({ thumbItems })}
                    <span class="slider-track">
                        <Slider.Range class="slider-range period-2-range" />
                    </span>

                    {#each thumbItems as { index } (index)}
                        <Slider.Thumb {index} class="slider-thumb period-2-thumb">
                            <div class="thumb-bracket">[</div>
                        </Slider.Thumb>
                    {/each}
                {/snippet}
            </Slider.Root>
        </div>
    </div>
</div>

<style>
    .timeline-container {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        padding: 0.5rem;
    }

    .timeline-section {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .timeline-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 0.25rem;
    }

    .period-title {
        font-weight: var(--font-weight-medium);
        font-size: var(--14px);
        color: var(--color-text-primary);
    }

    .period-display {
        font-size: var(--12px);
        color: var(--color-text-secondary);
        font-weight: var(--font-weight-medium);
    }

    .timeline {
        position: relative;
        height: 3rem;
    }

    .timeline-labels {
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 1rem;
        padding: 0 0.75rem;
        font-size: var(--10px);
        color: var(--color-text-secondary);
        margin-bottom: 0.5rem;
    }

    .year-label.center {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
    }

    .year-label.center:first-of-type {
        left: 25%;
    }

    .year-label.center:last-of-type {
        left: 75%;
    }

    :global(.period-slider) {
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
        cursor: pointer;
        overflow: hidden;
    }

    :global(.slider-range) {
        position: absolute;
        height: 100%;
        border-radius: 9999px;
    }

    :global(.period-1-range) {
        background: var(--color-good-blue);
    }

    :global(.period-2-range) {
        background: var(--color-electric-green);
    }

    :global(.slider-thumb) {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 1.5rem;
        height: 1.5rem;
        cursor: pointer;
        transition: all 150ms ease;
        background: transparent;
        border: none;
    }

    :global(.slider-thumb:hover) {
        transform: scale(1.1);
    }

    .thumb-bracket {
        font-size: 1.5rem;
        font-weight: var(--font-weight-bold);
        line-height: 1;
        color: var(--color-text-primary);
        text-shadow: 0 0 2px rgba(255,255,255,0.8);
        user-select: none;
    }

    :global(.period-1-thumb) .thumb-bracket {
        color: var(--color-good-blue);
    }

    :global(.period-2-thumb) .thumb-bracket {
        color: var(--color-electric-green);
    }

    :global(.slider-thumb:focus-visible) {
        outline: 2px solid var(--color-text-primary);
        outline-offset: 2px;
        border-radius: var(--border-radius);
    }
</style>