<script>
	import Scrolly from "$lib/components/helpers/Scrolly.svelte";
	
	let { story } = $props();
	let value = $state();
	let currentStep = $derived(story.steps[value]);
</script>

<section id="scrolly">
	<div class="sticky-viz">
		<h2>Climate Story</h2>
		
		{#if currentStep}
			<div class="content-card">
				<div class="step-number">Step {value + 1}</div>
				<p class="story-text">{currentStep.text}</p>
				<div class="data-preview">
					{JSON.stringify(currentStep.data, null, 2)}
				</div>
			</div>
		{:else}
			<div class="content-card">
				<p class="start-message">Scroll down to begin the story</p>
			</div>
		{/if}
	</div>
	
	<div class="spacer"></div>
	
	<Scrolly bind:value>
		{#each story.steps as step, i}
			<div class="step"></div>
		{/each}
	</Scrolly>
	
	<div class="spacer"></div>
</section>

<style>
	.sticky-viz {
		position: sticky;
		top: 2rem;
		height: 70vh;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		margin: 0 2rem;
		padding: 2rem;
	}

	.sticky-viz h2 {
		margin: 0 0 2rem 0;
		font-size: 1.8rem;
		color: #2d3748;
	}

	.content-card {
		background: white;
		border-radius: 12px;
		padding: 2rem;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
		border: 1px solid #e2e8f0;
		text-align: center;
		max-width: 500px;
		width: 100%;
	}

	.step-number {
		color: #667eea;
		font-weight: 600;
		font-size: 1rem;
		margin-bottom: 1rem;
	}

	.story-text {
		font-size: 1.2rem;
		line-height: 1.6;
		color: #2d3748;
		margin: 0 0 1.5rem 0;
	}

	.data-preview {
		background: #f7fafc;
		border-radius: 8px;
		padding: 1rem;
		font-family: monospace;
		font-size: 0.9rem;
		color: #4a5568;
	}

	.start-message {
		color: #718096;
		font-size: 1.1rem;
		margin: 0;
	}

	.step {
		height: 80vh;
	}

	.spacer {
		height: 75vh;
	}
</style>