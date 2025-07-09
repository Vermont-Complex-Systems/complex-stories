<script>
	import Scrolly from "$lib/components/helpers/Scrolly.svelte";
	import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
	import TextInterpolator from "./TextInterpolator.svelte";
	import Hero from './Hero.svelte';
	import StackedSlider from "./StackedSlider.svelte";
	import Scatter from "./Scatter.svelte";
	
	let { story, data } = $props();
	
	// Separate scroll indices for each section
	let firstScrollyIndex = $state(0);
	let secondScrollyIndex = $state(0);
	let thirdScrollyIndex = $state(0);
	
	const intro = data.intro;
	const steps = data.firstSection;
	const secondSectionSteps = data.secondSection;

	let currentSection = $state(undefined);

	// count how many objects in data 
	const sectionNums = Object.keys(data).length;

	let firstProgress = $state(0);
	let secondProgress = $state(0);
	let thirdProgress = $state(0);

	let width = $state(innerWidth > 1200 ? 500 : 350);
	let height = 600;
	const padding = { top: 20, right: 40, bottom: 20, left: 60 };

	let valueForSlider = $derived.by(() => {
		console.log("secondScrollyIndex", secondScrollyIndex);
		if (secondScrollyIndex < 2) {
			return 1
		} else if (secondScrollyIndex == 2) {
			return 5
		} else if (secondScrollyIndex == 3) {
			return 1
		} else {
			return 7
		}
	});

	// Fix the modeForSlider variable (it was undefined)
	let modeForSlider = $state("default");
</script>

<div id="story">
	<Hero />
	
	<!-- First Section -->
	<section class="scrolly-section">
		<div class="chart-container-scrolly">
			<TextInterpolator progress={firstProgress} currentStep={firstScrollyIndex} />
		</div>
		<div class="spacer"></div>
		<Scrolly bind:value={firstScrollyIndex} bind:scrollProgress={firstProgress} offset={innerWidth > 1200 ? '50vh' : '20vh'}>
			{#each steps as text, i}
				{@const active = firstScrollyIndex === i}
				<div class="step" class:active>
					<p> 
						<Md text={text.value}/>
					</p>
				</div>
			{/each}
		</Scrolly>
		<div class="spacer"></div>
	</section>	
	
	<div class="spacer"></div>
	
	<!-- Content Break -->
	<div class="centered-max-width">
		<h2>What is a token?</h2>
	</div>
	
	<!-- Second Section -->
	<section class="scrolly-section">
		<div class="chart-container-scrolly" style="display: {secondScrollyIndex > 0 ? 'block' : 'none'};">
			<StackedSlider bind:sliderValue={valueForSlider} renderMode={modeForSlider} scrollyIndex={secondScrollyIndex}></StackedSlider>
		</div>
		
		<Scrolly bind:value={secondScrollyIndex} bind:scrollProgress={secondProgress} offset={innerWidth > 1200 ? '50vh' : '20vh'}>
			{#each secondSectionSteps as text, i}
				{@const active = secondScrollyIndex === i}
				<div class="step" class:active>
					<p> 
						<Md text={text.value}/>
					</p>
				</div>
			{/each}
		</Scrolly>
	</section>
	
	<!-- Content Break -->
	<div class="centered-max-width">
		<h2>The Distributional Hypothesis</h2>
		<p>The Distributional Hypothesis states that words that occur in the same contexts tend to have similar meanings. So how does an LLM group different words?</p>
	</div>
	
	<!-- Third Section -->
	<section class="scrolly-section">
		<div class="chart-container-scrolly" style="display: {thirdScrollyIndex > 0 ? 'block' : 'none'};">
			<Scatter value={thirdScrollyIndex} steps={steps} />
		</div>
		
		<Scrolly bind:value={thirdScrollyIndex} bind:scrollProgress={thirdProgress} offset={innerWidth > 1200 ? '50vh' : '20vh'}>
			{#each secondSectionSteps as text, i}
				{@const active = thirdScrollyIndex === i}
				<div class="step" class:active>
					<p> 
						<Md text={text.value}/>
					</p>
				</div>
			{/each}
		</Scrolly>
	</section>
</div>

<style>
	/* Use :global() to override global styles */
	:global(body) {
		background-color: #f8ecd4 !important;
		background-image:
			url("data:image/svg+xml;utf8,<svg width='400' height='400' xmlns='http://www.w3.org/2000/svg'><filter id='noise'><feTurbulence type='fractalNoise' baseFrequency='0.055' numOctaves='2' seed='7'/><feColorMatrix type='saturate' values='0.1'/></filter><rect width='100%' height='100%' filter='url(%23noise)' opacity='0.22'/></svg>"),
			radial-gradient(ellipse at center, rgba(0,0,0,0) 20%, rgba(80,60,30,0.40) 100%);
		background-blend-mode: multiply, normal;
		background-size: 100% 100%, 100% 100%;
		background-repeat: repeat, no-repeat;
		color: #3b2f1e;
		font-family: 'Tiempos Text', 'Iowan Old Style', 'Times New Roman', Times, serif;
	}

	#story {
		--color-bg: #f8ecd4;
		background-color: var(--color-bg);
		background-image:
			url("data:image/svg+xml;utf8,<svg width='400' height='400' xmlns='http://www.w3.org/2000/svg'><filter id='noise'><feTurbulence type='fractalNoise' baseFrequency='0.055' numOctaves='2' seed='7'/><feColorMatrix type='saturate' values='0.1'/></filter><rect width='100%' height='100%' filter='url(%23noise)' opacity='0.22'/></svg>"),
			radial-gradient(ellipse at center, rgba(0,0,0,0) 20%, rgba(80,60,30,0.40) 100%);
		background-blend-mode: multiply, normal;
		background-size: 100% 100%, 100% 100%;
		background-repeat: repeat, no-repeat;
		color: #3b2f1e;
		font-family: 'Tiempos Text', 'Iowan Old Style', 'Times New Roman', Times, serif;
		min-height: 100vh;
	}

	/* Centered content sections */
	.centered-max-width {
		margin: 2rem auto;
		max-width: 800px;
		padding: 0 2rem;
		text-align: center;
	}

	.centered-max-width h2 {
		font-size: 36px;
		margin-bottom: 1rem;
		color: #3b2f1e;
	}

	.centered-max-width p {
		font-size: 22px;
		line-height: 1.6;
		color: #3b2f1e;
	}

	/* Scrolly sections */
	.scrolly-section {
		margin: 2rem auto;
		max-width: none;
		padding: 0 1rem;
		position: relative;
	}

	.chart-container-scrolly {
		width: 50%;
		height: 750px;
		position: sticky;
		top: calc(50vh - 375px);
		right: 5%;
		margin-left: auto;
		z-index: 1;
	}

	.spacer {
		height: 75vh;
	}

	.step {
		height: 80vh;
		display: flex;
		place-items: center;
		justify-content: flex-start;
		position: relative;
		z-index: 2;
	}

	.step p {
		padding: 1.5rem 2rem;
		background: rgba(248, 248, 255, 0.95);
		color: #333;
		border-radius: 8px;
		font-size: 1.4rem;
		display: flex;
		flex-direction: column;
		justify-content: center;
		transition: all 500ms ease;
		box-shadow: 2px 4px 20px rgba(0, 0, 0, 0.15);
		width: 40%;
		max-width: 500px;
		margin-left: 5%;
		backdrop-filter: blur(5px);
		border: 1px solid rgba(255, 255, 255, 0.2);
	}

	.step.active p {
		background: rgba(255, 255, 255, 0.98);
		box-shadow: 4px 8px 30px rgba(0, 0, 0, 0.25);
		transform: scale(1.02);
	}

	/* Responsive adjustments */
	@media (max-width: 1200px) {
		.chart-container-scrolly {
			width: 60%;
			height: 600px;
		}
		
		.step p {
			width: 50%;
			font-size: 1.2rem;
			padding: 1rem 1.5rem;
		}
	}

	@media (max-width: 768px) {
		.chart-container-scrolly {
			width: 100%;
			height: 400px;
			position: relative;
			top: auto;
			margin: 2rem 0;
		}
		
		.step {
			height: 60vh;
		}
		
		.step p {
			width: 90%;
			margin: 0 auto;
			font-size: 1.1rem;
		}
		
		.scrolly-section {
			padding: 0 0.5rem;
		}
	}
</style>