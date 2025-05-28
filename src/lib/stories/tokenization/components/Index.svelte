<script>
	import Scrolly from "$lib/components/helpers/Scrolly.svelte";
	import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
	
	let { story, data } = $props();
	
	
	// const components = { Hero };
	let scrollyIndex = $state();
	
	const steps = data.steps;
	const postIntro = data.postIntro;


	let width = $state(innerWidth.current > 1200 ? 500 : 350);
	let height = 600;
	const padding = { top: 20, right: 40, bottom: 20, left: 60 };
</script>

<section id="scrolly">
	
	
	<div class="spacer"></div>
	
	<Scrolly bind:value={scrollyIndex}  offset={innerWidth.current > 1200 ? '50vh' : '20vh'}>
		{#each steps as text, i}
                {@const active = scrollyIndex === i}
                <div class="step" class:active>
					<p> 
						<Md text={text.value}/>
                        <!-- {@html text.value} -->
                    </p>
                </div>
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

	.spacer {
    height: 75vh;
  }

  .step {
    height: 80vh;
    display: flex;
    place-items: center;
    justify-content: center;
  }

  .step p {
    padding: 0.5rem 1rem;
    background: whitesmoke;
    color: #333;
    border-radius: 5px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: background 500ms ease;
    box-shadow: 1px 1px 10px rgba(0, 0, 0, 0.2);
    z-index: 10;
    width: 40%;
    transform: translateX(-60%);
  }
</style>