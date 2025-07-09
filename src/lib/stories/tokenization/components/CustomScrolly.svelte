<script>
	import Scrolly from "$lib/components/helpers/Scrolly.svelte";
	import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
	import TextInterpolator from "./TextInterpolator.svelte";
	import Hero from './Hero.svelte';
	import StackedSlider from "./StackedSlider.svelte";
	import Scatter from "./Scatter.svelte";
	import { browser } from '$app/environment';
	
	let { story, data } = $props();
	
	// Single scroll index for the entire story
	let globalScrollIndex = $state(undefined);
	let globalProgress = $state(0);
	
	const intro = data.intro;
	const firstSectionSteps = data.firstSection;
	const secondSectionSteps = data.secondSection;
	
	// Combine all steps into one array for simpler management
	const allSteps = [
		...firstSectionSteps,
		...secondSectionSteps,
		...secondSectionSteps // Using second section steps for third section too
	];
	
	// Define section boundaries
	const firstSectionEnd = firstSectionSteps.length - 1;
	const secondSectionStart = firstSectionSteps.length;
	const secondSectionEnd = firstSectionSteps.length + secondSectionSteps.length - 1;
	const thirdSectionStart = firstSectionSteps.length + secondSectionSteps.length;
	
	// Determine which section is active and local indices
	let currentSection = $derived.by(() => {
		if (globalScrollIndex === undefined) return 'none';
		if (globalScrollIndex <= firstSectionEnd) return 'first';
		if (globalScrollIndex <= secondSectionEnd) return 'second';
		return 'third';
	});
	
	let firstScrollyIndex = $derived.by(() => {
		if (currentSection !== 'first') return undefined;
		return globalScrollIndex;
	});
	
	let secondScrollyIndex = $derived.by(() => {
		if (currentSection !== 'second') return undefined;
		return globalScrollIndex - secondSectionStart;
	});
	
	let thirdScrollyIndex = $derived.by(() => {
		if (currentSection !== 'third') return undefined;
		return globalScrollIndex - thirdSectionStart;
	});
	
	// Derived values for components
	let valueForSlider = $derived.by(() => {
		if (currentSection !== 'second') return 1;
		const localIndex = secondScrollyIndex ?? 0;
		
		switch (localIndex) {
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
		if (currentSection !== 'second') return "words";
		const localIndex = secondScrollyIndex ?? 0;
		return localIndex <= 2 ? "words" : "chars";
	});

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
</script>

<!-- Story wrapper with parchment theme -->
<div class="story-theme">
	<Hero />
	
	<!-- Single scrolly section with all content -->
	<section class="unified-scrolly-section">
		<!-- Single sticky chart container that switches content -->
		<div class="unified-chart-container">
			{#if currentSection === 'first'}
				<div class="chart-content" key="first">
					<TextInterpolator 
						progress={globalProgress} 
						currentStep={firstScrollyIndex ?? 0} 
					/>
				</div>
			{:else if currentSection === 'second'}
				<div class="chart-content" key="second">
					<StackedSlider 
						bind:sliderValue={valueForSlider} 
						renderMode={modeForSlider} 
						scrollyIndex={secondScrollyIndex ?? 0}
					/>
				</div>
			{:else if currentSection === 'third'}
				<div class="chart-content" key="third">
					<Scatter 
						value={thirdScrollyIndex ?? 0} 
						steps={secondSectionSteps} 
					/>
				</div>
			{/if}
		</div>
		
		<div class="spacer"></div>
		
		<!-- Single Scrolly component handling all steps -->
		<Scrolly 
			bind:value={globalScrollIndex} 
			bind:scrollProgress={globalProgress} 
			offset={scrollyOffset}
		>
			<!-- First section steps -->
			{#each firstSectionSteps as text, i}
				{@const active = globalScrollIndex === i}
				<div class="step" class:active>
					<div class="step-content">
						<Md text={text.value}/>
					</div>
				</div>
			{/each}
			
			<!-- Section break for "What is a token?" -->
			<div class="step">
				<div class="step-content section-break">
					<h2>What is a token?</h2>
					<p>Let's explore how language models break down text into manageable pieces.</p>
				</div>
			</div>
			
			<!-- Second section steps -->
			{#each secondSectionSteps as text, i}
				{@const globalIndex = secondSectionStart + i}
				{@const active = globalScrollIndex === globalIndex}
				<div class="step" class:active>
					<div class="step-content">
						<Md text={text.value}/>
					</div>
				</div>
			{/each}
			
			<!-- Section break for "The Distributional Hypothesis" -->
			<div class="step">
				<div class="step-content section-break">
					<h2>The Distributional Hypothesis</h2>
					<p>The Distributional Hypothesis states that words that occur in the same contexts tend to have similar meanings. So how does an LLM group different words?</p>
				</div>
			</div>
			
			<!-- Third section steps -->
			{#each secondSectionSteps as text, i}
				{@const globalIndex = thirdSectionStart + i}
				{@const active = globalScrollIndex === globalIndex}
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
	   UNIFIED SCROLLYTELLING LAYOUT
	   ============================================================================= */
	
	.unified-scrolly-section {
		position: relative;
		margin: 2rem auto;
		max-width: none;
		padding: 0 1rem;
	}
	
	.unified-chart-container {
		width: 50%;
		height: 750px;
		position: sticky;
		top: calc(50vh - 375px);
		right: 5%;
		margin-left: auto;
		z-index: var(--z-middle);
	}
	
	.chart-content {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		
		/* Smooth transitions when switching between charts */
		animation: fadeIn 0.5s ease-in-out;
	}
	
	@keyframes fadeIn {
		from { opacity: 0; transform: translateY(20px); }
		to { opacity: 1; transform: translateY(0); }
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
	
	/* Special styling for section breaks */
	.step-content.section-break {
		background: rgba(248, 236, 212, 0.95);
		border: 2px solid var(--color-border);
		text-align: center;
	}
	
	.step-content.section-break h2 {
		font-size: var(--font-size-large);
		font-family: var(--sans);
		font-weight: var(--font-weight-bold);
		color: var(--color-fg);
		margin-bottom: 0.5rem;
	}
	
	.step-content.section-break p {
		color: var(--color-secondary-gray);
		margin: 0;
	}
	
	/* =============================================================================
	   RESPONSIVE DESIGN
	   ============================================================================= */
	
	@media (max-width: 1200px) {
		.unified-chart-container {
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
		.unified-chart-container {
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
	}
	
	@media (max-width: 480px) {
		.step-content {
			padding: 1rem;
			font-size: var(--font-size-xsmall);
		}
	}
</style>