<script>
    import Md from '$lib/components/helpers/MarkdownRenderer.svelte';

    let {
        alphas,
        alphaIndex = $bindable(),
        currentAlpha
    } = $props();

    // Format alpha as LaTeX fraction for display
    function formatAlpha(alpha) {
        if (alpha === 0) return '$0$';
        if (alpha === Infinity) return '∞';

        const fractions = {
            [1/4]: '$\\frac{1}{4}$',
            [2/4]: '$\\frac{1}{2}$',
            [3/4]: '$\\frac{3}{4}$',
            [3/2]: '$\\frac{3}{2}$'
        };

        return fractions[alpha] ? fractions[alpha] : `$${alpha}$`;
    }

    // Only show labels for key values to avoid crowding
    function shouldShowLabel(alpha) {
        const keyValues = [0, 1/4, 1/2, 3/4, 1, 3/2, 2, 3, 5, Infinity];
        return keyValues.includes(alpha);
    }

    // Map alpha values to positions - proper spacing that reflects actual numeric differences
    // Actual diffs: 3/4→1 (0.25), 1→3/2 (0.5), 3/2→2 (0.5), 2→3 (1), 3→5 (2)
    const getNumericValue = (alpha) => {
        if (alpha === Infinity) return 3.5;  // ∞ at end
        if (alpha === 5) return 2.85;         // 3→5: 0.6 spacing (compressed from 2)
        if (alpha === 3) return 2.25;         // 2→3: 0.5 spacing (compressed from 1)
        if (alpha === 2) return 1.7;         // 3/2→2: 0.35 spacing
        if (alpha === 3/2) return 1.35;       // 1→3/2: 0.35 spacing (same as 3/2→2!)
        return alpha;                        // Keep 0, 1/4, 1/2, 3/4, 1 at true values
    };

    const minAlpha = $derived(getNumericValue(alphas[0])); // 0
    const maxAlpha = $derived(getNumericValue(alphas[alphas.length - 1])); // 3.5 (representing Infinity)

    // Calculate position percentage for each alpha value
    function getTickPosition(alpha) {
        const numericValue = getNumericValue(alpha);
        return ((numericValue - minAlpha) / (maxAlpha - minAlpha)) * 100;
    }

    // Calculate positions array for all alphas
    const tickPositions = $derived(alphas.map(getTickPosition));

    // Slider percentage for pointer based on actual alpha value position
    let sliderPosition = $derived.by(() => {
        return getTickPosition(currentAlpha) + "%";
    });

    let container;

    function onDrag(event) {
        const rect = container.getBoundingClientRect();
        const x = Math.min(Math.max(event.clientX - rect.left, 0), rect.width);
        const percent = x / rect.width;

        // Find the closest tick position
        let closestIndex = 0;
        let minDistance = Math.abs(tickPositions[0] - percent * 100);

        for (let i = 1; i < tickPositions.length; i++) {
            const distance = Math.abs(tickPositions[i] - percent * 100);
            if (distance < minDistance) {
                minDistance = distance;
                closestIndex = i;
            }
        }

        alphaIndex = closestIndex;
    }

    function startDrag(event) {
        onDrag(event);

        const move = (e) => onDrag(e);
        const up = () => {
            window.removeEventListener("pointermove", move);
            window.removeEventListener("pointerup", up);
        };

        window.addEventListener("pointermove", move);
        window.addEventListener("pointerup", up);
    }
</script>

<div class="alpha-slider-container" bind:this={container}>
    <div
        class="alpha-pointer-wrapper"
        style="left: {sliderPosition}"
        onpointerdown={startDrag}
    >
        <div class="alpha-current-value">
            α = {currentAlpha === Infinity ? '∞' : currentAlpha}
        </div>
        <div class="alpha-pointer">▼</div>
    </div>

    <input
        type="range"
        min="0"
        max={alphas.length - 1}
        value={alphaIndex}
        oninput={(e) => alphaIndex = +e.target.value}
        class="alpha-slider"
    />

    <div class="alpha-ticks">
        {#each alphas as alpha, i}
            <div
                class="alpha-tick"
                style="left: {tickPositions[i]}%"
            >
                <div class="tick-mark"></div>
                {#if shouldShowLabel(alpha)}
                    <div class="tick-label">
                        <Md text={formatAlpha(alpha)} />
                    </div>
                {/if}
            </div>
        {/each}
    </div>
</div>

<style>
    /* Container */
    .alpha-slider-container {
        position: relative;
        width: 300px;
        padding-top: 0;
        padding-bottom: 0;
        user-select: none;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* Pointer wrapper (draggable) */
    .alpha-pointer-wrapper {
        position: absolute;
        top: -48px;
        transform: translateX(-50%);
        cursor: pointer;
        text-align: center;
    }

    /* Pointer label "α = x" */
    .alpha-current-value {
        font-size: 0.8rem;
        margin-bottom: -1.5px;
        font-weight: 500;
        color: var(--color-fg, #333);
        text-align: left;
        white-space: nowrap;
    }

    /* ▼ triangle pointer */
    .alpha-pointer {
        font-size: 0.95rem;
        line-height: 1;
    }

    /* Thin line slider track */
    .alpha-slider {
        -webkit-appearance: none;
        appearance: none;

        width: 100%;
        height: 1px; /* ← EXACT THIN LINE */
        background: var(--color-border, #999);

        position: relative;
        top: 0;
        left: 0;

        margin: 0;
        padding: 0;
        border: none;
        border-radius: 0;

        pointer-events: none; /* Pointer does NOT interact with native slider */
    }

    /* Track overrides – Chrome/Safari */
    .alpha-slider::-webkit-slider-runnable-track {
        height: 2px;
        background: var(--color-border, #999);
    }

    /* Hide thumb entirely – Chrome/Safari */
    .alpha-slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 0;
        height: 0;
    }

    /* Track override – Firefox */
    .alpha-slider::-moz-range-track {
        height: 2px;
        background: var(--color-border, #999);
    }

    /* Hide thumb – Firefox */
    .alpha-slider::-moz-range-thumb {
        width: 0;
        height: 0;
        border: none;
        background: transparent;
    }

    /* Tick container */
    .alpha-ticks {
        position: absolute;
        top: -4px; /* Just under the slider line */
        left: 0;
        width: 100%;
        pointer-events: none;
    }

    /* Each tick is positioned absolutely at exact % */
    .alpha-tick {
        position: absolute;
        transform: translateX(-50%);
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    /* Vertical tick line */
    .tick-mark {
        width: 1px;
        height: 10px;
        background: var(--color-border, #999);
        margin-bottom: -15px;
    }

    /* Tick label */
    .tick-label {
        color: var(--color-fg, #666);
        white-space: nowrap;
    }
</style>