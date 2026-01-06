<script>
    import { Slider } from "bits-ui";

    let { 
        min = 1900, 
        max = 2025, 
        value = $bindable(1970),
        step = 1,
    } = $props();
</script>

<div class="range-filter">
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
        background: #959595;
        border-radius: 9999px;
    }

    :global(.slider-thumb) {
        display: block;
        width: 1rem;
        height: 1rem;
        background: white;
        border: 2px solid #959595;
        border-radius: 50%;
        cursor: pointer;
        transition: all 150ms ease;
    }

    :global(.slider-thumb:hover) {
        transform: scale(1.1);
    }

    :global(.slider-thumb:focus-visible) {
        outline: 2px solid #7a7a7a;
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
        border-color: #999999;
    }
</style>