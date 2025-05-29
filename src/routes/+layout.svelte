<script lang="ts">
	import { base } from '$app/paths';
	import "$styles/app.css";
	import { page } from '$app/state';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	
	let { children } = $props();
	
	// Check if we're on a story page (individual story route)
	let isStoryPage = $derived(page.route.id === '/[slug]');
</script>

<!-- Only show header if NOT on a story page -->
{#if !isStoryPage}
	<Header />
{/if}

<main id="content">
	{@render children?.()}
</main>

<Footer />

<style>
	#content {
		flex: 1;
		padding: 1rem 2rem 2rem;
	}
	
	@media (max-width: 768px) {
		#content {
			padding: 0.5rem 1rem 1rem;
		}
	}
</style>