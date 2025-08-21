<script>
	import Scrolly from "$lib/components/helpers/Scrolly.svelte";
	import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
	import TextInterpolator from "./TextInterpolator.svelte";
	import Hero from './Hero.svelte';
	import StackedSlider from "./StackedSlider.svelte";
	import Scatter from "./Scatter.svelte";
	import { browser } from '$app/environment';
	
	let { story, data } = $props();
	
	// Global state for which section is currently active
	let activeSection = $state('none');
	let activeSectionData = $state({});
	
	// Individual section states
	let firstSectionIndex = $state(undefined);
	let firstSectionProgress = $state(0);
	
	let secondSectionIndex = $state(undefined);
	let secondSectionProgress = $state(0);
	
	let thirdSectionIndex = $state(undefined);
	let thirdSectionProgress = $state(0);
	
	const firstSectionSteps = data.firstSection;
	const secondSectionSteps = data.secondSection;
	const thirdSectionSteps = data.secondSection; // Reusing for now
	
	// Safe window width check
	let innerWidth = $state(browser ? window.innerWidth : 1200);
	
	if (browser) {
		let resizeTimeout;
		const updateWidth = () => {
			clearTimeout(resizeTimeout);
			resizeTimeout = setTimeout(() => {
				innerWidth = window.innerWidth;
			}, 100);
		};
		window.addEventListener('resize', updateWidth);
	}

	// Dynamic offset calculation
	let scrollyOffset = $derived(() => {
		if (innerWidth > 1200) return '50vh';
		if (innerWidth > 768) return '40vh';
		return '30vh';
	});
	
	// Update active section based on which section has an active step
	$effect(() => {
		if (firstSectionIndex !== undefined) {
			activeSection = 'first';
			activeSectionData = {
				index: firstSectionIndex,
				progress: firstSectionProgress
			};
		} else if (secondSectionIndex !== undefined) {
			activeSection = 'second';
			activeSectionData = {
				index: secondSectionIndex,
				progress: secondSectionProgress
			};
		} else if (thirdSectionIndex !== undefined) {
			activeSection = 'third';
			activeSectionData = {
				index: thirdSectionIndex,
				progress: thirdSectionProgress
			};
		} else {
			activeSection = 'none';
			activeSectionData = {};
		}
	});
	
	// Derived values for second section
	let valueForSlider = $derived.by(() => {
		if (activeSection !== 'second') return 1;
		const index = activeSectionData.index ?? 0;
		
		switch (index) {
			case 0:
			case 1:
				return 1;
			case 2:
				return 5;
			case 3:
				return 1;
			default:
				return 7;
		}
	});

	let modeForSlider = $derived.by(() => {
		if (activeSection !== 'second') return "words";
		const index = activeSectionData.index ?? 0;
		return index <= 2 ? "words" : "chars";
	});
</script>

<!-- Story wrapper with parchment theme -->
<div class="story-theme">
	<Hero />
	
	<!-- Global sticky chart container -->
	<div class="global-chart-container">
		{#if activeSection === 'first'}
			<div class="chart-content" key="first">
				<TextInterpolator 
					progress={activeSectionData.progress ?? 0} 
					currentStep={activeSectionData.index ?? 0} 
				/>
			</div>
		{:else if activeSection === 'second'}
			<div class="chart-content" key="second">
				<StackedSlider 
					bind:sliderValue={valueForSlider} 
					renderMode={modeForSlider} 
					scrollyIndex={activeSectionData.index ?? 0}
				/>
			</div>
		{:else if activeSection === 'third'}
			<div class="chart-content" key="third">
				<Scatter 
					value={activeSectionData.index ?? 0} 
					steps={thirdSectionSteps} 
				/>
			</div>
		{/if}
	</div>
	
	<!-- First Section -->
	<section class="story-section" id="first-section">
		<div class="spacer"></div>
		<Scrolly 
			bind:value={firstSectionIndex} 
			bind:scrollProgress={firstSectionProgress} 
			offset={scrollyOffset}
		>
			{#each firstSectionSteps as text, i}
				{@const active = firstSectionIndex === i}
				<div class="step" class:active>
					<div class="step-content">
						<Md text={text.value}/>
					</div>
				</div>
			{/each}
		</Scrolly>
		<div class="spacer"></div>
	</section>
	
	<!-- Section Break -->
	<div class="story-section-break">
		<h2>What is a token?</h2>
		<p>Let's explore how language models break down text into manageable pieces.</p>
	</div>
	
	<!-- Second Section -->
	<section class="story-section" id="second-section">
		<div class="spacer"></div>
		<Scrolly 
			bind:value={secondSectionIndex} 
			bind:scrollProgress={secondSectionProgress} 
			offset={scrollyOffset}
		>
			{#each secondSectionSteps as text, i}
				{@const active = secondSectionIndex === i}
				<div class="step" class:active>
					<div class="step-content">
						<Md text={text.value}/>
					</div>
				</div>
			{/each}
		</Scrolly>
		<div class="spacer"></div>
	</section>
	
	<!-- Section Break -->
	<div class="story-section-break">
		<h2>The Distributional Hypothesis</h2>
		<p>The Distributional Hypothesis states that words that occur in the same contexts tend to have similar meanings. So how does an LLM group different words?</p>
	</div>
	
	<!-- Third Section -->
	<section class="story-section" id="third-section">
		<div class="spacer"></div>
		<Scrolly 
			bind:value={thirdSectionIndex} 
			bind:scrollProgress={thirdSectionProgress} 
			offset={scrollyOffset}
		>
			{#each thirdSectionSteps as text, i}
				{@const active = thirdSectionIndex === i}
				<div class="step" class:active>
					<div class="step-content">
						<Md text={text.value}/>
					</div>
				</div>
			{/each}
		</Scrolly>
		<div class="spacer"></div>
	</section>
</div>

<style>
	/* =============================================================================
	   STORY THEME SCOPE
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
	   GLOBAL CHART CONTAINER
	   ============================================================================= */
	
	.global-chart-container {
		position: fixed;
		top: calc(50vh - 375px);
		right: 5%;
		width: 45%;
		height: 750px;
		z-index: var(--z-middle);
		pointer-events: none; /* Allow scrolling through it */
	}

	/* need to add this so user can click on slider in third section */
	.story-section {
		pointer-events: none;
	}
	
	.chart-content {
		width: 100%;
		height: 100%;
		align-items: center;
		justify-content: center;
		pointer-events: auto; /* Re-enable for chart interactions */
		
		/* Smooth transitions when switching between charts */
		animation: fadeIn 0.6s ease-in-out;
	}
	
	@keyframes fadeIn {
		from { opacity: 0; transform: translateY(20px); }
		to { opacity: 1; transform: translateY(0); }
	}
	
	/* =============================================================================
	   STORY SECTIONS
	   ============================================================================= */
	
	.story-section {
		position: relative;
		margin: 0;
		padding: 0 1rem;
		min-height: 100vh; /* Ensure each section takes full viewport */
	}
	
	.story-section-break {
		max-width: var(--width-column-wide);
		margin: 6rem auto;
		padding: 3rem 2rem;
		text-align: center;
		
		/* Parchment-themed styling */
		background: rgba(255, 255, 255, 0.95);
		backdrop-filter: blur(8px);
		border: 2px solid var(--color-border);
		border-radius: var(--border-radius);
		box-shadow: 
			0 8px 30px rgba(59, 47, 30, 0.15),
			0 2px 6px rgba(59, 47, 30, 0.25);
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
		opacity: 0.7;
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
		.global-chart-container {
			width: 55%;
			height: 600px;
		}
		
		.step-content {
			width: 50%;
			font-size: var(--font-size-smallish);
			padding: 1.25rem 1.75rem;
		}
	}
	
	@media (max-width: 768px) {
		.global-chart-container {
			position: relative;
			top: auto;
			right: auto;
			width: 100%;
			height: 400px;
			margin: 2rem auto;
		}
		
		.story-section {
			min-height: auto;
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
		
		.story-section-break {
			margin: 4rem auto;
			padding: 2rem 1rem;
		}
		
		.story-section-break h2 {
			font-size: var(--font-size-large);
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