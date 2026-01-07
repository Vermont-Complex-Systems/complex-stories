<script>
	import RatingBarChart from './RatingBarChart.svelte'
	import AgreementMatrix from './AgreementMatrix.svelte'
	import SearchInput from './SearchInput.svelte'
	import { getAgreementData } from '../data/data.remote'
	import { onMount } from 'svelte'

	let {
		stats = {},
		myAnnotations = [],
		myPapers = [],
		paperIds = [],
		generalPapers = []
	} = $props()

	let agreementData = $state(null)
	let searchQuery = $state('')
	let showCount = $state(10) // Number of matrices to show

	const ratingLabels = {
		1: 'Very much interdisciplinary',
		2: 'Somewhat interdisciplinary',
		3: 'Undecided',
		4: 'Not really interdisciplinary',
		5: 'Not at all interdisciplinary'
	}

	const totalAnnotations = $derived(stats.total_annotations || 0)
	const distribution = $derived(stats.rating_distribution || {})
	const avgRating = $derived(stats.average_rating || 0)
	const loggedInCount = $derived(stats.logged_in_annotations || 0)
	const anonymousCount = $derived(stats.anonymous_annotations || 0)

	// Calculate percentages for each rating
	const ratingPercentages = $derived(
		Object.fromEntries(
			Object.entries(distribution).map(([rating, count]) => [
				rating,
				totalAnnotations > 0 ? (count / totalAnnotations) * 100 : 0
			])
		)
	)

	// Get max count for scaling bars
	const maxCount = $derived(
		Math.max(...Object.values(distribution), 1)
	)

	// Global distribution data for svelteplot
	const globalDistributionData = $derived(
		[1, 2, 3, 4, 5].map(rating => ({
			rating: ratingLabels[rating],
			count: distribution[rating] || 0,
			ratingNum: rating
		}))
	)

	// Only annotations from current queues (excluding migrated "other" papers)
	const currentQueueAnnotations = $derived(
		[...generalPapersAnnotations, ...myOwnPapersAnnotations]
	)

	// User's rating distribution (only for current queue papers)
	const userDistribution = $derived.by(() => {
		const dist = {}
		currentQueueAnnotations.forEach(annotation => {
			const rating = annotation.interdisciplinarity_rating
			dist[rating] = (dist[rating] || 0) + 1
		})
		return dist
	})

	// Convert to array format for svelteplot
	const userDistributionData = $derived(
		[1, 2, 3, 4, 5].map(rating => ({
			rating: ratingLabels[rating],
			count: userDistribution[rating] || 0,
			ratingNum: rating
		}))
	)

	const userMaxCount = $derived(
		Math.max(...Object.values(userDistribution), 1)
	)

	const userAvgRating = $derived.by(() => {
		if (currentQueueAnnotations.length === 0) return 0
		const sum = currentQueueAnnotations.reduce((acc, a) => acc + a.interdisciplinarity_rating, 0)
		return sum / currentQueueAnnotations.length
	})

	// Separate user's annotations by paper source
	const myPaperIds = $derived(myPapers.map(p => p.id))
	const myOwnPapersAnnotations = $derived(
		myAnnotations.filter(a => myPaperIds.includes(a.paper_id))
	)
	const generalPaperIds = $derived([...paperIds, ...generalPapers.map(p => p.id)])
	const generalPapersAnnotations = $derived(
		myAnnotations.filter(a => generalPaperIds.includes(a.paper_id))
	)
	// Papers not in either queue (e.g., from migrated data)
	const otherPapersAnnotations = $derived(
		myAnnotations.filter(a => !myPaperIds.includes(a.paper_id) && !generalPaperIds.includes(a.paper_id))
	)

	// Load agreement data
	onMount(async () => {
		try {
			agreementData = await getAgreementData()
		} catch (err) {
			console.error('Failed to load agreement data:', err)
		}
	})

	// Filter papers based on search query, or show top N by disagreement
	const filteredPapers = $derived.by(() => {
		if (!agreementData?.papers) return []

		const query = searchQuery.trim().toLowerCase()
		if (!query) {
			// Default to top N most contentious papers (lowest agreement = most disagreement)
			// Papers are already sorted by agreement (ascending) from the API
			return agreementData.papers.slice(0, showCount)
		}

		const filtered = agreementData.papers.filter(paper =>
			paper.title?.toLowerCase().includes(query) ||
			paper.paper_id?.toLowerCase().includes(query)
		)

		// Return top N matches
		return filtered.slice(0, showCount)
	})
</script>

<header>
	<h1>Annotation Statistics</h1>
	<p class="subtitle">
		Aggregated data from {totalAnnotations} annotations
	</p>
</header>

<div class="stats-grid">
	<!-- Summary Cards -->
	<div class="stat-card">
		<div class="stat-value">{totalAnnotations}</div>
		<div class="stat-label">Total Annotations</div>
	</div>

	<div class="stat-card">
		<div class="stat-value">{avgRating.toFixed(2)}</div>
		<div class="stat-label">Average Rating</div>
		<div class="stat-sublabel">1 = Very interdisciplinary, 5 = Not at all</div>
	</div>

	{#if myAnnotations.length > 0}
		<div class="stat-card">
			<div class="stat-value">{myAnnotations.length}</div>
			<div class="stat-label">Your Total Annotations</div>
			<div class="stat-sublabel">
				{generalPapersAnnotations.length} general queue ·
				{myOwnPapersAnnotations.length} your papers
				{#if otherPapersAnnotations.length > 0}
					· {otherPapersAnnotations.length} other
				{/if}
			</div>
		</div>
		<div class="stat-card">
			<div class="stat-value">{generalPapersAnnotations.length}</div>
			<div class="stat-label">General Queue Progress</div>
			<div class="stat-progress">
				<div class="stat-progress-bar" style="width: {generalPaperIds.length > 0 ? (generalPapersAnnotations.length / generalPaperIds.length) * 100 : 0}%"></div>
			</div>
			<div class="stat-sublabel">{generalPapersAnnotations.length} of {generalPaperIds.length} papers</div>
		</div>
		{#if myPapers.length > 0}
			<div class="stat-card">
				<div class="stat-value">{myOwnPapersAnnotations.length}</div>
				<div class="stat-label">Your Papers Progress</div>
				<div class="stat-progress">
					<div class="stat-progress-bar" style="width: {myPapers.length > 0 ? (myOwnPapersAnnotations.length / myPapers.length) * 100 : 0}%"></div>
				</div>
				<div class="stat-sublabel">{myOwnPapersAnnotations.length} of {myPapers.length} papers</div>
			</div>
		{/if}
	{/if}

</div>


{#if myAnnotations.length > 0}
	<!-- User's Personal Rating Distribution -->
	<div class="distribution-section user-section">
		<h2>Your Rating Distribution</h2>
		<p class="section-subtitle">
			{currentQueueAnnotations.length} annotations on current queue papers · Average: {userAvgRating.toFixed(2)}
			{#if otherPapersAnnotations.length > 0}
				<span class="note">(excluding {otherPapersAnnotations.length} annotations on other papers)</span>
			{/if}
		</p>

		<div class="user-chart">
			<RatingBarChart
				data={userDistributionData}
				fill="#6b7280"
				stroke="#374151"
			/>
		</div>
	</div>
{/if}

<!-- Rating Distribution -->
<div class="distribution-section">
	<h2>Global Rating Distribution</h2>
	<p class="section-subtitle">How all users rated papers for interdisciplinarity ({totalAnnotations} total annotations)</p>

	<div class="global-chart">
		<RatingBarChart
			data={globalDistributionData}
			fill="#9ca3af"
			stroke="#6b7280"
		/>
	</div>
</div>

<!-- Inter-Annotator Agreement -->
{#if agreementData && agreementData.papers?.length > 0}
	<div class="distribution-section">
		<h2>Inter-Annotator Agreement</h2>
		<p class="section-subtitle">
			{agreementData.total_papers_analyzed} papers with multiple annotations ·
			{agreementData.papers_with_high_disagreement} with high disagreement (&lt;60% agreement)
			{#if !searchQuery}
				· Showing top {Math.min(showCount, agreementData.papers.length)} most contentious
			{/if}
		</p>

		<div class="search-controls">
			<SearchInput bind:value={searchQuery} placeholder="Search by paper title or ID..." />
			{#if searchQuery}
				<button onclick={() => searchQuery = ''} class="clear-btn">
					Clear
				</button>
			{/if}
			{#if !searchQuery && agreementData.papers.length > showCount}
				<button onclick={() => showCount += 10} class="load-more-btn">
					Show 10 more
				</button>
			{/if}
		</div>

		{#if filteredPapers.length > 0}
			<div class="agreement-matrices">
				{#each filteredPapers as paper (paper.paper_id)}
					<AgreementMatrix {paper} />
				{/each}
			</div>
		{:else}
			<div class="no-results">
				<p>No papers found matching "{searchQuery}"</p>
			</div>
		{/if}
	</div>
{/if}

<style>
	header {
		margin-bottom: 2rem;
	}

	h1 {
		font-size: 2rem;
		margin: 0 0 0.5rem 0;
		color: #1a1a1a;
	}

	h2 {
		font-size: 1.5rem;
		margin: 0 0 0.5rem 0;
		color: #1a1a1a;
	}

	.subtitle {
		color: #666;
		margin: 0;
	}

	.section-subtitle {
		color: #666;
		margin: 0 0 1.5rem 0;
		font-size: 0.875rem;
	}

	.section-subtitle .note {
		color: #999;
		font-size: 0.75rem;
		font-style: italic;
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
		margin-bottom: 2rem;
	}

	.stat-card {
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		padding: 1.5rem;
		text-align: center;
	}

	.stat-value {
		font-size: 2.5rem;
		font-weight: 700;
		color: #1a1a1a;
		margin-bottom: 0.5rem;
	}

	.stat-label {
		font-size: 0.875rem;
		font-weight: 600;
		color: #666;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.stat-sublabel {
		font-size: 0.75rem;
		color: #999;
		margin-top: 0.25rem;
	}

	.stat-progress {
		margin-top: 0.75rem;
		height: 6px;
		background: #e0e0e0;
		border-radius: 3px;
		overflow: hidden;
	}

	.stat-progress-bar {
		height: 100%;
		background: #4b5563;
		transition: width 0.3s ease;
	}

	.distribution-section {
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		padding: 2rem;
		margin-bottom: 2rem;
	}

	.distribution-section.user-section {
		background: #f9fafb;
		border-color: #d1d5db;
	}

	.user-section h2 {
		color: #1a1a1a;
	}

	.user-chart {
		margin-top: 1rem;
	}

	.global-chart {
		margin-top: 1rem;
	}

	.agreement-matrices {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
	}

	.agreement-matrices > :global(*) {
		flex: 1 1 calc(50% - 0.5rem);
		min-width: 400px;
	}

	@media (max-width: 900px) {
		.agreement-matrices > :global(*) {
			flex: 1 1 100%;
		}
	}

	.search-controls {
		display: flex;
		gap: 0.5rem;
		margin-bottom: 1.5rem;
	}

	.clear-btn {
		padding: 0.75rem 1.5rem;
		background: #f3f4f6;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.875rem;
		color: #374151;
		transition: all 0.2s;
	}

	.clear-btn:hover {
		background: #e5e7eb;
	}

	.load-more-btn {
		padding: 0.75rem 1.5rem;
		background: #4b5563;
		border: 1px solid #374151;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.875rem;
		color: white;
		transition: all 0.2s;
	}

	.load-more-btn:hover {
		background: #374151;
	}

	.no-results {
		text-align: center;
		padding: 2rem;
		color: #6b7280;
		font-size: 0.875rem;
	}
</style>
