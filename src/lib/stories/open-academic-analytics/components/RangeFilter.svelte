<script>
    import { Slider } from "bits-ui";

    let { 
        min = 0, 
        max = 70, 
        value = $bindable(max),
        step = 1,
        label = "Max Filter"
    } = $props();
</script>

<div class="range-filter">
    <label class="range-label">{label}</label>
    <Slider.Root 
        type="single"
        bind:value 
        {min} 
        {max} 
        {step}
        class="slider-root"
    >
        <span class="slider-track">
            <Slider.Range class="slider-range" />
        </span>
        <Slider.Thumb index={0} class="slider-thumb" />
    </Slider.Root>
</div>

<style>
    .range-filter {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        width: 100%;
    }

    .range-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--color-fg);
    }

    :global(.slider-root) {
        position: relative;
        display: flex;
        align-items: center;
        width: 100%;
        height: 1.25rem;
        touch-action: none;
    }

    .slider-track {
        position: relative;
        flex: 1;
        height: 0.25rem;
        background: #e5e7eb;
        border-radius: 9999px;
        cursor: pointer;
        overflow: hidden;
    }

    :global(.slider-range) {
        position: absolute;
        height: 100%;
        background: #3b82f6;
        border-radius: 9999px;
    }

    :global(.slider-thumb) {
        display: block;
        width: 1rem;
        height: 1rem;
        background: white;
        border: 2px solid #3b82f6;
        border-radius: 50%;
        cursor: pointer;
        transition: all 150ms ease;
    }

    :global(.slider-thumb:hover) {
        transform: scale(1.1);
    }

    :global(.slider-thumb:focus-visible) {
        outline: 2px solid #3b82f6;
        outline-offset: 2px;
    }

    /* Dark mode */
    .slider-track {
        background: #374151;
    }

    :global(.dark .slider-track) {
        background: #374151;
    }

    :global(.dark .slider-thumb) {
        background: #1f2937;
        border-color: #60a5fa;
    }
</style>