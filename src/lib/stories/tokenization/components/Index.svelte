<script>
	import Scrolly from "$lib/components/helpers/Scrolly.svelte";
	import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
	import WordTree from './WordTree.svelte';
	
	let { story, data } = $props();
	
	
	// const components = { Hero };
	let scrollyIndex = $state();
	
	const steps = data.steps;
	const postIntro = data.postIntro;

	let wordArray = ['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'the', 'lazy', 'dog'];

	let progress = $state(0);

	let width = $state(innerWidth.current > 1200 ? 500 : 350);
	let height = 600;
	const padding = { top: 20, right: 40, bottom: 20, left: 60 };
</script>

<section id="story">
	
	<div class="chart-container-scrolly">
		<div>Active step is {scrollyIndex} at {progress}</div>
		<WordTree wordArray={wordArray}  />
	</div>
	<div class="spacer"></div>
	


<Scrolly bind:value={scrollyIndex} bind:scrollProgress={progress} offset={innerWidth.current > 1200 ? '50vh' : '20vh'}>
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
	/* override some global styles */
	#story {
		--color-bg: #f8ecd4; /* subtle tan */
  background-color: var(--color-bg);
  background-image:
	/* more visible random crinkle/noise SVG texture */
	url("data:image/svg+xml;utf8,<svg width='400' height='400' xmlns='http://www.w3.org/2000/svg'><filter id='noise'><feTurbulence type='fractalNoise' baseFrequency='0.055' numOctaves='2' seed='7'/><feColorMatrix type='saturate' values='0.1'/></filter><rect width='100%' height='100%' filter='url(%23noise)' opacity='0.22'/></svg>"),
	/* vignette for old feel */
	radial-gradient(ellipse at center, rgba(0,0,0,0) 20%, rgba(80,60,30,0.40) 100%);
  background-blend-mode: multiply, normal;
  background-size: 100% 100%, 100% 100%;
  background-repeat: repeat, no-repeat;
  color: #3b2f1e; /* dark brown for text */
  font-family: 'Tiempos Text', Iowan Old Style, Times New Roman, Times, serif;
	}

	/* Only global page styles */
	section {
	margin: 2rem auto;
	max-width: 1200px;
	padding: 0 2rem;
	}

	/* Allow viz sections to overflow the max-width */
	section:has(.chart-container-scrolly) {
	max-width: none; /* Remove width constraint for sections with visualizations */
	padding: 0 1rem; /* Reduce padding to give more space */
	}

	section h2 {
	font-size: 36px;
	margin-bottom: 1rem;
	}

	section p {
	font-size: 22px;
	max-width: 800px;
	line-height: 1.6;
	}


	/* Keep only the first section's scrolly styles */
	.chart-container-scrolly {
	width: 40%;
	height: 550px;
	position: sticky;
	top: calc(50vh - 275px);
	right: 5%;
	margin-left: auto;
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