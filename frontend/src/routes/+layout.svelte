<script lang="ts">
	import { base } from '$app/paths';
	import "$styles/app.css";
	import { page } from '$app/state';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	
	let { children } = $props();
	
	let isStoryPage = $derived(page.route.id === '/[slug]');
	let isBlogPost = $derived(page.route.id === '/blog/[slug]');
	let showHeader = $derived(!isStoryPage && !isBlogPost);
</script>

<svelte:head>
	<script async defer src="https://cloud.umami.is/script.js" data-website-id="44b340b0-d307-4438-8fb4-4e17f1767354"></script>
</svelte:head>

{#if showHeader}
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
			padding: 0 1rem 1rem; /* Reduced top padding from 0.5rem to 0.25rem */
			margin-top: -0.5rem; /* Pull content up slightly */
		}
	}
</style>