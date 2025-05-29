<script lang="ts">
	import { base } from '$app/paths';
	import "$styles/app.css";
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	
	let { children } = $props();
</script>

<Header />

<main id="content">
	{@render children?.()}
</main>

<Footer />

<style>
	:global(body) {
		margin: 0;
		transition: background-color 0.2s, color 0.2s;
		background-color: #fefefe;
		color: #2d3748;
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		line-height: 1.6;
	}
	
	:global(.dark body) {
		background-color: #1a202c;
		color: #e2e8f0;
	}
	
	#content {
		flex: 1;
		padding: 0rem 2rem 2rem; /* Reduced top padding from 2rem to 1rem */
	}
	
	/* Responsive adjustments */
	@media (max-width: 768px) {
		#content {
			padding: 0.5rem 1rem 1rem; /* Reduced top padding from 1rem to 0.5rem */
		}
	}
</style>