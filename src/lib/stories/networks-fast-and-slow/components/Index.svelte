<script lang="ts">
	import { innerWidth } from 'svelte/reactivity/window';
	import { base } from '$app/paths';
	
	// Responsive breakpoints
	let isMobile = $derived(innerWidth.current <= 768);
	let isTablet = $derived(innerWidth.current <= 1200 && innerWidth.current > 768);
	
	import Network from './Network.svelte';
	import Quench from './Quench.svelte';
	import Manylinks from '../data/edges.json';
	import nodes from '../data/nodes.csv';
	import Scrolly from '$lib/components/helpers/Scrolly.svelte';
	import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
	import Hero from './Hero.svelte';
	import ThemeToggle from '$lib/stories/allotax-scrolly/components/ThemeToggle.svelte';

	let { story, data } = $props();

	let isDark = $state(false);
	let links = Manylinks[0];
	
	let scrollyIndex = $state();
	
	const steps = data.steps;
	const postIntro = data.postIntro;

	let width = $state(innerWidth.current > 1200 ? 450 : 350);
	let height = 600;
	const padding = { top: 20, right: 40, bottom: 20, left: 60 };
</script>

<!-- Navigation header -->
<header class="header">
    <div class="header-left">
        <div class="logo-container">
            <a href="{base}/" class="logo-link">
                <img src="{base}/octopus-swim-right.png" alt="Home" class="logo" />
            </a>
        </div>
    </div>
    
    <div class="header-center">
        <!-- Empty for now -->
    </div>
    
    <div class="header-right">
        <div class="toggles-container">
            <ThemeToggle bind:isDark hideOnMobile={false} />
        </div>
    </div>
</header>

<Hero />

<div class="story-container" id="networks-fast-and-slow">
	<section id="mean-field">
		<div class="text-content">
			<h2>Part I: Annealing</h2>
			<p>But doing math on exact networks can get… messy. It's often unwieldy to carry full structure through the equations. So instead, people often model the average effect of the dynamics — smoothing over the specific network in favor of general trends. To preserve some notion of structure without going fully detailed, modelers sometimes use what's called an <u>annealed approximation</u>.</p>
			<p>Borrowed from metallurgy, annealing refers to the process of slowly cooling a metal so that its atomic structure settles into a stable — though not static — configuration. In network modeling, annealed networks refer to a similar idea: connections between nodes are not fixed, but constantly reshuffling, like social ties in a fast-moving crowd.</p> 
			<p>But why does that make sense? Think back to the bouncing balls. On average, the more infected balls there were, the more likely you were to bump into one. That's the essence of a <u>mean-field approximation</u> — we ignore the specific bump and just look at average exposure.</p>
		</div>

		<div class="chart-container-scrolly">
			<Network {scrollyIndex} {nodes} {links} {width} {height} {padding} isRadial={true}/>
		</div>

		<div class="spacer"></div>
		<Scrolly bind:value={scrollyIndex}>
			{#each steps as text, i}
				{@const active = scrollyIndex === i}
				<div class="scrolly-step" class:active class:mobile={isMobile} class:tablet={isTablet}>
					<p> 
						<Md text={text.value}/>
					</p>
				</div>
			{/each}
		</Scrolly>
		<div class="spacer"></div>
	</section>

	<section id="mean-field-versus-quench">
		<div class="text-content">
			<h2>Part II: Quenching</h2>
			<p>The annealed assumption is a powerful one, but it also has a fundamental drawback; it washes away persistent group interactions. In that sense, this is terrible (but still slightly better than the bouncing ball world). It can somewhat ephemeral group interactions, which can be fairly inclusive as a process. For instance, many models of <u>higher-order interactions</u> (or complex contagion) are about paper coauthorships, where the ephemerality of the interactions is the span it takes to publish a paper. It might be good enough.</p>
			<p>But workplace and households are both great example of group behaviors that are so persistent that it influences the dynamics in ways that mean-field just cannot. If your kid get sick, the chances are that the rest of the household will get sick too. There is <em>dynamical correlation</em> between the states of individuals within the household.</p>
		</div>
		
    
		<div class="chart-container-scrolly">
			<Quench {scrollyIndex} {nodes} {links} {width} {height} {padding}/>
		</div>

		<div class="spacer"></div>
		<Scrolly bind:value={scrollyIndex} offset={innerWidth.current > 1200 ? '50vh' : '20vh'}>
			{#each postIntro as text, i}
				{@const active = scrollyIndex === i}
				<div class="scrolly-step" class:active class:mobile={isMobile} class:tablet={isTablet}>
					<p> 
						<Md text={text.value}/>
					</p>
				</div>
			{/each}
		</Scrolly>
		<div class="spacer"></div>
		
	</section>
	
	<div class="text-content">
		<p>You should now have a better idea what physicists mean when they say that annealed networks are thought to be reshuffled constantly, leading to the system the relax faster than the dynamics. In contrast, quench changes slowly compared to the dynamics, meaning that local structures can strongly influence the dynamics.</p>
	</div>
</div>

<style>
	/* Main story container - matches Hero layout */
	:global(body:has(#networks-fast-and-slow) main#content) {
		max-width: var(--width-column-wide);
		margin: 0 auto;
		padding: 0 2rem;
	}

	/* Text content sections - matches main element width */
	.text-content {
		max-width: var(--width-column-wide);
		text-align: left;
		margin: 2rem auto;
		padding: 0 1rem;
	}
   .text-content h2 {
		color: var(--color-fg);
		font-size: var(--font-size-large);
		margin: 2rem 0 1.5rem 0;
		text-align: left;
		font-family: var(--serif);
	}

	.text-content p {
		font-size: 1.375rem; /* Match global section p styling */
		line-height: 1.3;
		margin-top: 1rem;
		color: var(--color-fg);
	}

	/* Sections - remove centering and max-width constraints for viz sections */
	section {
		margin: 2rem 0;
		position: relative;
	}

	/* Chart container positioning */
	.chart-container-scrolly {
		width: 40%;
		height: 550px;
		position: sticky;
		top: calc(50vh - 275px);
		right: 5%;
		margin-left: auto;
		float: right;
		clear: both;
    overflow: visible;
	}

	/* Scrolly steps styling */
	.spacer {
		height: 75vh;
	}

	/* Local scrolly step overrides for this story - now handled globally */

	/* Mobile responsive */
	@media (max-width: 1200px) {
		.story-container {
			padding: 0 1rem;
		}

		.text-content {
			max-width: none;
			text-align: left; /* Keep left alignment on mobile */
		}

		.text-content p {
			font-size: 1.1rem;
		}

		.chart-container-scrolly {
			position: sticky;
			top: calc(50vh - 275px);
			width: 100%;
			max-width: 600px;
			margin: 2rem auto;
			display: flex;
			justify-content: center;
			align-items: center;
			float: none;
		}

		/* Mobile styles now handled by global framework */
	}

	/* Dark mode adjustments - now handled by global styles */

	/* Header styles - simplified version of allotax-scrolly Nav */
	header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0 2rem;
		position: sticky;
		top: 0;
		background: rgba(255, 255, 255, 0.7);
		backdrop-filter: blur(15px);
		border-bottom: 1px solid rgba(0, 0, 0, 0.03);
		z-index: 1000;
		transition: all 300ms ease;
		min-height: 1rem;
		width: 100vw;
		margin-left: calc(-50vw + 50%);
		box-sizing: border-box;
		overflow: visible;
	}

	:global(.dark) header {
		background: rgba(30, 30, 30, 0.7);
		border-bottom: 1px solid rgba(255, 255, 255, 0.03);
	}

	header:hover {
		background: rgba(255, 255, 255, 0.8);
	}

	:global(.dark) header:hover {
		background: rgba(30, 30, 30, 0.8);
	}

	.header-left, .header-right {
		display: flex;
		align-items: center;
		flex: 0 0 auto;
	}

	.header-center {
		display: flex;
		align-items: center;
		justify-content: center;
		flex: 1;
	}

	.logo-container {
		max-width: 12rem;
		transition: transform var(--transition-medium) ease;
		margin: 0;
		position: relative;
		z-index: 10;
	}

	.logo-container:hover {
		transform: rotate(var(--left-tilt)) scale(1.05);
	}

	.logo-link {
		display: block;
		border: none;
	}

	.logo {
		width: 100%;
		height: auto;
		border-radius: var(--border-radius);
		max-height: 4.5rem;
		object-fit: contain;
		transform: translateY(0.6rem);
	}

	.toggles-container {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	@media (max-width: 768px) {
		header {
			padding: 0.5rem 1rem;
			min-height: 3rem;
			background: rgba(255, 255, 255, 0.8);
		}

		:global(.dark) header {
			background: rgba(30, 30, 30, 0.8);
		}

		.logo {
			max-height: 2rem;
		}

		.text-content p {
			font-size: 1.6rem; /* Match global mobile section p styling */
		}
	}

	@media (max-width: 480px) {
		.logo-container {
			max-width: 5rem;
		}

		.author-name {
			font-size: var(--font-size-xsmall);
		}
	}
</style>