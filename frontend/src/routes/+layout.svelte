<script lang="ts">
	import { base } from '$app/paths';
	import "$styles/app.css";
	import { page } from '$app/state';
	import { afterNavigate } from '$app/navigation';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query';
	import { browser } from '$app/environment';

	// Manually track page views in Umami so it doesn't monkey-patch
	// history.pushState/replaceState (which breaks SvelteKit's router).
	afterNavigate(() => {
		// @ts-expect-error - umami is injected globally by the tracker script
		window.umami?.track();
	});

	const queryClient = new QueryClient({
		defaultOptions: {
			queries: {
				staleTime: 1000 * 60 * 5 // 5 minutes
			}
		}
	});

	// Expose queryClient for TanStack Query DevTools
	if (browser) {
		window.__TANSTACK_QUERY_CLIENT__ = queryClient;
	}

	let { children } = $props();

	let isStoryPage = $derived(page.route.id === '/[slug]');
	let isBlogPost = $derived(page.route.id === '/blog/[slug]');
	let showHeader = $derived(!isStoryPage && !isBlogPost);
</script>

<svelte:head>
	<script async defer src="https://cloud.umami.is/script.js" data-website-id="9748947b-5af8-4053-b1a5-8e74f48eb7e2" data-auto-track="false"></script>
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