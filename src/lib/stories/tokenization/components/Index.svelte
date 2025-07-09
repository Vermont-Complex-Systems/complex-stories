<script>
	import Scrolly from "$lib/components/helpers/Scrolly.svelte";
	import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
	import TextInterpolator from "./TextInterpolator.svelte";
	import Hero from './Hero.svelte';
	import StackedSlider from "./StackedSlider.svelte";
	import Scatter from "./Scatter.svelte";
	import { browser } from '$app/environment';
	
	let { story, data } = $props();
	
	// Separate scroll indices for each section
	let firstScrollyIndex = $state(0);
	let secondScrollyIndex = $state(0);
	let thirdScrollyIndex = $state(0);
	
	const intro = data.intro;
	const steps = data.firstSection;
	const secondSectionSteps = data.secondSection;

	let currentSection = $state(undefined);
	let firstProgress = $state(0);
	let secondProgress = $state(0);
	let thirdProgress = $state(0);

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

	let modeForSlider = $state("default");

	// Safe window width check
	let innerWidth = $state(browser ? window.innerWidth : 1200);
	
	if (browser) {
		// Update innerWidth on resize
		const updateWidth = () => {
			innerWidth = window.innerWidth;
		};
		window.addEventListener('resize', updateWidth);
	}
</script>

<!-- Story wrapper with parchment theme -->
<div class="story-theme">
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
					<div class="step-content">
						<Md text={text.value}/>
					</div>
				</div>
			{/each}
		</Scrolly>
		<div class="spacer"></div>
	</section>	
	
	<div class="spacer"></div>
	
	<!-- Content Break -->
	<div class="story-section-break">
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
					<div class="step-content">
						<Md text={text.value}/>
					</div>
				</div>
			{/each}
		</Scrolly>
	</section>
	
	<!-- Content Break -->
	<div class="story-section-break">
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
					<div class="step-content">
						<Md text={text.value}/>
					</div>
				</div>
			{/each}
		</Scrolly>
	</section>
</div>

<style>
	/* =============================================================================
	   STORY THEME SCOPE
	   
	   Override design tokens for this specific story
	   ============================================================================= */
	
	.story-theme {
		/* Override semantic color tokens for parchment theme */
		--color-bg: #f8ecd4;
		--color-fg: #3b2f1e;
		--color-secondary-gray: #8b7355;
		--color-link: #5d4037;
		--color-link-hover: #3e2723;
		--color-border: rgba(59, 47, 30, 0.2);
		--color-selection: rgba(139, 115, 85, 0.3);
		
		/* Override typography tokens */
		--font-body: 'Tiempos Text', 'Iowan Old Style', 'Times New Roman', Times, serif;
		
		/* Story-specific tokens */
		--story-texture-opacity: 0.22;
		--story-vignette-strength: 0.4;
		
		/* Force full screen coverage */
		position: relative;
		width: 100vw;
		margin-left: calc(-50vw + 50%);
		padding: 0;
		box-sizing: border-box;
		
		/* Apply the theme */
		background-color: var(--color-bg);
		background-image:
			url("data:image/svg+xml;utf8,<svg width='400' height='400' xmlns='http://www.w3.org/2000/svg'><filter id='parchment-noise'><feTurbulence type='fractalNoise' baseFrequency='0.055' numOctaves='2' seed='7'/><feColorMatrix type='saturate' values='0.1'/></filter><rect width='100%' height='100%' filter='url(%23parchment-noise)' opacity='0.22'/></svg>"),
			radial-gradient(ellipse at center, rgba(0,0,0,0) 20%, rgba(80,60,30,0.4) 100%);
		background-blend-mode: multiply, normal;
		background-size: 400px 400px, 100% 100%;
		background-repeat: repeat, no-repeat;
		background-attachment: fixed;
		color: var(--color-fg);
		font-family: var(--font-body);
		min-height: 100vh;
	}
	
	/* =============================================================================
	   STORY-SPECIFIC LAYOUT
	   ============================================================================= */
	
	.story-section-break {
		max-width: var(--width-column-wide);
		margin: 4rem auto;
		padding: 0 2rem;
		text-align: center;
	}
	
	.story-section-break h2 {
		font-size: var(--font-size-xlarge);
		font-family: var(--sans);
		font-weight: var(--font-weight-bold);
		color: var(--color-fg);
		margin-bottom: 1rem;
	}
	
	.story-section-break p {
		font-size: var(--font-size-medium);
		line-height: 1.6;
		color: var(--color-secondary-gray);
		max-width: 600px;
		margin: 0 auto;
	}
	
	/* =============================================================================
	   SCROLLYTELLING LAYOUT
	   ============================================================================= */
	
	.scrolly-section {
		position: relative;
		margin: 2rem auto;
		max-width: none;
		padding: 0 1rem;
	}
	
	.chart-container-scrolly {
		width: 50%;
		height: 750px;
		position: sticky;
		top: calc(50vh - 375px);
		right: 5%;
		margin-left: auto;
		z-index: var(--z-middle);
	}
	
	.spacer {
		height: 75vh;
	}
	
	.step {
		height: 80vh;
		display: flex;
		align-items: center;
		justify-content: flex-start;
		position: relative;
		z-index: var(--z-top);
	}
	
	.step-content {
		width: 40%;
		max-width: 500px;
		margin-left: 5%;
		padding: 1.5rem 2rem;
		
		/* Parchment-themed step styling */
		background: rgba(255, 255, 255, 0.9);
		backdrop-filter: blur(8px);
		border: 1px solid var(--color-border);
		border-radius: var(--border-radius);
		box-shadow: 
			0 4px 20px rgba(59, 47, 30, 0.1),
			0 1px 3px rgba(59, 47, 30, 0.2);
		
		/* Typography */
		font-size: var(--font-size-small);
		line-height: 1.6;
		color: #333;
		
		/* Smooth transitions */
		transition: all var(--transition-medium) ease;
		transform: translateY(0);
		opacity: 0.8;
	}
	
	.step.active .step-content {
		background: rgba(255, 255, 255, 0.98);
		box-shadow: 
			0 8px 30px rgba(59, 47, 30, 0.15),
			0 2px 6px rgba(59, 47, 30, 0.25);
		transform: translateY(-4px) scale(1.02);
		opacity: 1;
	}
	
	/* =============================================================================
	   RESPONSIVE DESIGN
	   ============================================================================= */
	
	@media (max-width: 1200px) {
		.chart-container-scrolly {
			width: 60%;
			height: 600px;
		}
		
		.step-content {
			width: 50%;
			font-size: var(--font-size-smallish);
			padding: 1.25rem 1.75rem;
		}
	}
	
	@media (max-width: 768px) {
		.story-section-break {
			margin: 3rem auto;
			padding: 0 1rem;
		}
		
		.story-section-break h2 {
			font-size: var(--font-size-large);
		}
		
		.chart-container-scrolly {
			width: 100%;
			height: 400px;
			position: relative;
			top: auto;
			margin: 2rem auto;
		}
		
		.step {
			height: 60vh;
			justify-content: center;
		}
		
		.step-content {
			width: 90%;
			margin: 0 auto;
			font-size: var(--font-size-smallish);
			padding: 1rem 1.5rem;
		}
		
		.step.active .step-content {
			transform: translateY(-2px) scale(1.01);
		}
		
		.scrolly-section {
			padding: 0 0.5rem;
		}
	}
	
	@media (max-width: 480px) {
		.step-content {
			padding: 1rem;
			font-size: var(--font-size-xsmall);
		}
		
		.story-section-break h2 {
			font-size: var(--font-size-medium);
		}
		
		.story-section-break p {
			font-size: var(--font-size-small);
		}
	}
</style>