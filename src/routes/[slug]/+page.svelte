<script>
	import Scrolly from "$lib/components/helpers/Scrolly.svelte";
	
	let { data } = $props();
	let value = $state();
</script>

<h1>{data.story.title}</h1>
<p>{data.story.description}</p>

<section id="scrolly">
	<h2>Step <span>{value !== undefined ? value + 1 : "-"}</span></h2>
	<div class="spacer"></div>
	<Scrolly bind:value>
		{#each data.story.steps as step, i}
			{@const active = value === i}
			<div class="step" class:active>
				<p>{step.text}</p>
			</div>
		{/each}
	</Scrolly>
	<div class="spacer"></div>
</section>

<style>
	h1 {
		text-align: center;
		margin-bottom: 0.5rem;
	}
	
	p {
		text-align: center;
		color: #666;
		margin-bottom: 2rem;
	}

	h2 {
		position: sticky;
		top: 4em;
		background: white;
		padding: 1rem;
		margin: 0;
	}

	.spacer {
		height: 75vh;
	}

	.step {
		height: 80vh;
		background: var(--color-gray-100, #f3f4f6);
		text-align: center;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.step p {
		padding: 1rem;
		font-size: 1.1rem;
		max-width: 600px;
	}
</style>