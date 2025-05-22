<script>
	import Scrolly from "$lib/components/helpers/Scrolly.svelte";
	
	import { Plot, RectY, RuleY, binX } from 'svelteplot';
    import { range } from 'd3-array';
    import { randomNormal } from 'd3-random';
	
	let { story } = $props();
	let value = $state();
	let currentStep = $derived(story.steps[value]);
</script>

<Plot grid>
    <RectY 
        {...binX({ 
            data: range(10000).map(randomNormal()),
        }, { y: 'count' })} 
        opacity={0.7} />
    <RuleY data={[0]} />
</Plot>

<section id="scrolly">
	<div class="timeline-viz">
		<h2>Timeline: <span>{currentStep?.data.year || "Start"}</span></h2>
		
		{#if currentStep}
			<div class="timeline-content">
				<div class="year-display">{currentStep.data.year}</div>
				<div class="event-display">{currentStep.data.event}</div>
				<p class="event-description">{currentStep.text}</p>
			</div>
		{:else}
			<div class="timeline-content">
				<p class="start-message">Scroll down to begin the timeline</p>
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
	.timeline-viz {
		position: sticky;
		top: 2rem;
		height: 70vh;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		background: white;
		border-radius: 12px;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
		border: 1px solid #e2e8f0;
		margin: 0 2rem;
		padding: 2rem;
	}

	.timeline-viz h2 {
		margin: 0 0 2rem 0;
		font-size: 1.8rem;
		color: #2d3748;
	}

	.timeline-viz h2 span {
		color: #667eea;
		font-weight: bold;
	}

	.timeline-content {
		text-align: center;
		max-width: 400px;
	}

	.year-display {
		font-size: 3rem;
		font-weight: bold;
		color: #667eea;
		margin-bottom: 1rem;
	}

	.event-display {
		font-size: 1.2rem;
		font-weight: 600;
		color: #4a5568;
		margin-bottom: 1rem;
		text-transform: capitalize;
	}

	.event-description {
		font-size: 1.1rem;
		line-height: 1.6;
		color: #2d3748;
		margin: 0;
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