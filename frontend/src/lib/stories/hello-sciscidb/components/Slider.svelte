<script>
    import { Slider } from "bits-ui";

    let { 
        min = 1900, 
        max = 2025, 
        value = $bindable(1970),
        step = 1,
    } = $props();
</script>

<div class="slider-container">
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

