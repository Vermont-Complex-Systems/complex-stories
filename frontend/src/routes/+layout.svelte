<script lang="ts">
	import { base } from '$app/paths';
	import "$styles/app.css";
	import { page } from '$app/state';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query'

	const queryClient = new QueryClient({
		defaultOptions: {
			queries: {
				staleTime: 1000 * 60 * 5 // 5 minutes
			}
		}
	});

	let { children } = $props();
	
	let isStoryPage = $derived(page.route.id === '/[slug]');
	let isBlogPost = $derived(page.route.id === '/blog/[slug]');
	let showHeader = $derived(!isStoryPage && !isBlogPost);
</script>

<svelte:head>
	<script async defer src="https://cloud.umami.is/script.js" data-website-id="9748947b-5af8-4053-b1a5-8e74f48eb7e2"></script>
</svelte:head>

{#if showHeader}
	<Header />
{/if}

<main id="content">
<QueryClientProvider client={queryClient}>
	{@render children?.()}
</QueryClientProvider>
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