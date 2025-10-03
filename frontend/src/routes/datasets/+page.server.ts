import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	try {
		// Try to fetch from API first, fall back to local for development
		const apiUrl = 'https://api.complexstories.uvm.edu';

		// Fetch datasets list and stats in parallel
		const [datasetsResponse, statsResponse] = await Promise.all([
			fetch(`${apiUrl}/datasets/`).catch(() => null),
			fetch(`${apiUrl}/datasets/stats`).catch(() => null)
		]);

		let datasets = [];
		let stats = {};

		if (datasetsResponse?.ok) {
			const datasetsData = await datasetsResponse.json();
			datasets = datasetsData.datasets || [];
		}

		if (statsResponse?.ok) {
			stats = await statsResponse.json();
		}

		// Combine datasets with their stats
		const datasetsWithStats = datasets.map(dataset => ({
			...dataset,
			stats: stats.stats?.[dataset.name] || null,
			status: stats.stats?.[dataset.name]?.error ? 'error' : 'available'
		}));

		return {
			datasets: datasetsWithStats,
			apiConnected: !!(datasetsResponse?.ok || statsResponse?.ok)
		};
	} catch (error) {
		console.error('Failed to load datasets:', error);
		return {
			datasets: [],
			apiConnected: false,
			error: 'Failed to connect to API'
		};
	}
};