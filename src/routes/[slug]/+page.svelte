<script>
	import ClimateChange from "$lib/components/stories/ClimateChange.svelte";
	import SpaceExploration from "$lib/components/stories/SpaceExploration.svelte";
	
	let { data } = $props();
	
	const components = {
		'climate-change': ClimateChange,
		'space-exploration': SpaceExploration,
	};
	
	// Use slug as the component type
	const StoryComponent = components[data.story.slug];
</script>

<div class="story-intro">
	<h1>{data.story.title}</h1>
	<p class="story-description">{data.story.description}</p>
</div>

{#if StoryComponent}
	<StoryComponent story={data.story} />
{:else}
	<p>Story component not found for: {data.story.slug}</p>
{/if}

<style>
	.story-intro {
		padding: 2rem 1rem;
		text-align: center;
		border-bottom: 1px solid #e2e8f0;
	}

	.story-intro h1 {
		margin: 0 0 0.5rem 0;
		font-size: 2.5rem;
		font-weight: bold;
	}

	.story-intro p {
		color: #6b7280;
		font-size: 1.1rem;
		max-width: 600px;
		margin: 0 auto;
	}
</style>