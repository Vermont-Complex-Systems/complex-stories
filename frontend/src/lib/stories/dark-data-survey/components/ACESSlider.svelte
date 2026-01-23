<script>
	import { Slider } from "bits-ui";

	let { value = $bindable(0), disabled = false } = $props();

	// Slider range from 0 to 5.5 with 0.25 step
	const min = 0;
	const max = 5.5;
	const step = 0.25;

	// bits-ui expects an array, but we want to expose a single number
	let internalValue = $state([value]);

	// Sync external value changes to internal array
	$effect(() => {
		if (value !== internalValue[0]) {
			internalValue = [value];
		}
	});

	// Sync internal array changes to external value
	$effect(() => {
		if (internalValue[0] !== value) {
			value = internalValue[0];
		}
	});
</script>

<div class="slider-container">
	<Slider.Root
		bind:value={internalValue}
		{min}
		{max}
		{step}
		{disabled}
		class="slider-root"
		trackPadding={2}
	>
		{#snippet children({ tickItems, thumbItems })}
			<span class="slider-track">
				<Slider.Range class="slider-range" />
			</span>
			{#each thumbItems as { index } (index)}
				<Slider.Thumb
					{index}
					class="slider-thumb"
				/>
			{/each}
			{#each tickItems as { index, value: tickValue } (index)}
				<Slider.Tick
					{index}
					class="slider-tick"
				/>
				{#if tickValue % 1 === 0 && tickValue <= 6}
					<Slider.TickLabel
						{index}
						class="slider-tick-label"
						position="bottom"
					>
						{Math.floor(tickValue)}
					</Slider.TickLabel>
				{/if}
			{/each}
		{/snippet}
	</Slider.Root>
</div>

<style>
	.slider-container {
		width: 100%;
		padding: 2rem 0;
	}

	.slider-container :global(.slider-root) {
		position: relative;
		display: flex;
		width: 100%;
		touch-action: none;
		user-select: none;
		align-items: center;
	}

	.slider-container :global(.slider-track) {
		position: relative;
		height: 15px;
		width: 100%;
		flex-grow: 1;
		cursor: pointer;
		overflow: hidden;
		border-radius: 9999px;
		background-color: rgba(255, 255, 255, 0.2);
	}

	.slider-container :global(.slider-range) {
		position: absolute;
		height: 100%;
		background-color: rgba(255, 255, 255, 0.6);
	}

	.slider-container :global(.slider-thumb) {
		z-index: 5;
		display: block;
		width: 25px;
		height: 25px;
		cursor: pointer;
		border-radius: 9999px;
		border: 2px solid rgba(255, 255, 255, 0.9);
		background-color: white;
		box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.3);
		transition: all 0.2s;
	}

	.slider-container :global(.slider-thumb:hover) {
		border-color: white;
		box-shadow: 0 2px 6px 0 rgba(0, 0, 0, 0.4);
	}

	.slider-container :global(.slider-thumb:focus-visible) {
		outline: 2px solid rgba(255, 255, 255, 0.8);
		outline-offset: 2px;
	}

	.slider-container :global(.slider-thumb[data-active]) {
		border-color: white;
		transform: scale(0.98);
	}

	.slider-container :global(.slider-thumb:disabled) {
		pointer-events: none;
		opacity: 0.5;
	}

	.slider-container :global(.slider-tick) {
		z-index: 1;
		height: 15px;
		width: 1px;
		background-color: rgba(0, 0, 0, 0.2);
	}

	.slider-container :global(.slider-tick-label) {
		margin-top: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		line-height: 1;
		color: white;
	}

	.slider-container :global(.slider-tick-label[data-bounded]) {
		color: rgba(255, 255, 255, 0.8);
	}
</style>
