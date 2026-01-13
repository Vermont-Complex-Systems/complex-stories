<script>
	import { getPaperById } from '../data/data.remote'
	import SearchInput from './SearchInput.svelte'
	import FilterButtons from './FilterButtons.svelte'
	import { untrack } from 'svelte'

	let {
		paperIds = [],
		generalPapers = [],
		myPapers = [],
		myAnnotations = [],
		myPapersQueueIds = [],
		csvQueuePaperIds = [],
		communityQueuePaperIds = [],
		annotationCounts = {},
		agreementData = null, // Agreement scores from API
		onJumpToPaper = (mode, index) => {},
		onSortedIdsChange = (csvIds, communityPapersList, myPapersList) => {}
	} = $props()

	let searchQuery = $state('')
	let statusFilter = $state('all')
	let sortBy = $state('default')

	const statusOptions = [
		{ value: 'all', label: 'All' },
		{ value: 'completed', label: 'Completed' },
		{ value: 'pending', label: 'Pending' }
	]

	const sortOptions = [
		{ value: 'default', label: 'Default' },
		{ value: 'time', label: 'Year' },
		{ value: 'random', label: 'Random' },
		{ value: 'disagreement', label: 'Disagreement' }
	]

	const totalPapers = $derived(paperIds.length + generalPapers.length + myPapers.length)

	const allPapersList = $derived.by(() => {
		let papers = [
			...paperIds.map(id => ({ id, source: 'csv' })),
			...generalPapers.map(p => ({ id: p.id, source: 'community', paper: p })),
			...myPapers.map(p => ({ id: p.id, source: 'my-papers', paper: p }))
		]

		// Apply sorting
		if (sortBy === 'time') {
			// Sort by publication year (newest first)
			// Papers with year go first, then papers without
			papers = papers.sort((a, b) => {
				const yearA = a.paper?.year || 0
				const yearB = b.paper?.year || 0
				return yearB - yearA
			})
		} else if (sortBy === 'random') {
			// Fisher-Yates shuffle
			papers = [...papers]
			for (let i = papers.length - 1; i > 0; i--) {
				const j = Math.floor(Math.random() * (i + 1));
				[papers[i], papers[j]] = [papers[j], papers[i]]
			}
		} else if (sortBy === 'disagreement' && agreementData?.papers) {
			// Create lookup for agreement scores
			const agreementMap = new Map(
				agreementData.papers.map(p => [p.paper_id, p.agreement_score])
			)

			// Sort by agreement score (lowest = most disagreement)
			// Papers with scores first, then papers without
			papers = papers.sort((a, b) => {
				const scoreA = agreementMap.get(a.id)
				const scoreB = agreementMap.get(b.id)

				// Papers without scores go to the end
				if (scoreA === undefined && scoreB === undefined) return 0
				if (scoreA === undefined) return 1
				if (scoreB === undefined) return -1

				// Lower agreement = more disagreement = should come first
				return scoreA - scoreB
			})
		}

		return papers
	})

	// Notify parent when sorting changes
	$effect(() => {
		const currentSort = sortBy

		untrack(() => {
			if (currentSort !== 'default') {
				const csvIds = allPapersList.filter(p => p.source === 'csv').map(p => p.id)
				const communityPapersList = allPapersList.filter(p => p.source === 'community').map(p => p.paper)
				const myPapersList = allPapersList.filter(p => p.source === 'my-papers').map(p => p.paper)
				onSortedIdsChange(csvIds, communityPapersList, myPapersList)
			}
		})
	})

	// Helper to check if paper matches search/filter
	function matchesFilters(item, paperData, annotation) {
		// Status filter
		if (statusFilter === 'completed' && !annotation) return false
		if (statusFilter === 'pending' && annotation) return false

		// Text search
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase()
			const title = (paperData?.title || item.paper?.title || '').toLowerCase()
			const authors = (paperData?.authors || item.paper?.authors || []).join(' ').toLowerCase()

			if (!title.includes(query) && !authors.includes(query)) {
				return false
			}
		}

		return true
	}

	const ratingLabels = ['Not at all', 'Not really', 'Undecided', 'Somewhat', 'Very much']
</script>

<header>
	<h2>Your Annotation Progress</h2>
	<p class="subtitle">
		{myAnnotations.length} of {totalPapers} papers annotated
		({paperIds.length} CSV + {generalPapers.length} community + {myPapers.length} your papers)
	</p>
</header>

<div class="filters">
	<SearchInput bind:value={searchQuery} placeholder="Filter by title or author..." />
	<FilterButtons bind:value={statusFilter} options={statusOptions} />
	<div class="sort-group">
		<label for="sort-select">Sort by:</label>
		<select id="sort-select" bind:value={sortBy} class="sort-select">
			{#each sortOptions as option}
				<option value={option.value}>{option.label}</option>
			{/each}
		</select>
	</div>
</div>

<div class="overview-table">
	<table>
		<thead>
			<tr>
				<th class="number-col">#</th>
				<th class="source-col">Source</th>
				<th>Title</th>
				<th class="desktop-only">Authors</th>
				<th class="desktop-only">Year</th>
				<th class="desktop-only">Annotations</th>
				<th class="desktop-only">Status</th>
				<th class="desktop-only">Rating</th>
			</tr>
		</thead>
		<tbody>
			{#each allPapersList as item, index}
				{@const annotation = myAnnotations.find(a => a.paper_id === item.id)}
				{#if (item.source === 'my-papers' || item.source === 'community') && matchesFilters(item, item.paper, annotation)}
					<!-- Papers with full metadata (user's papers or community papers) -->
					<tr
						class:annotated={annotation}
						class:my-paper={item.source === 'my-papers'}
						class="clickable-row"
						onclick={() => {
							if (item.source === 'my-papers') {
								const myPaperIndex = myPapersQueueIds.indexOf(item.id)
								if (myPaperIndex >= 0) {
									onJumpToPaper('my-papers-queue', myPaperIndex)
								} else if (annotation) {
									onJumpToPaper('my-papers-queue', 0)
									alert('This paper is already annotated. You can re-annotate it from the My Papers queue.')
								}
							} else {
								const communityIndex = communityQueuePaperIds.indexOf(item.id)
								onJumpToPaper('community-queue', communityIndex >= 0 ? communityIndex : 0)
							}
						}}
					>
						<td class="number-col">{index + 1}</td>
						<td class="source-col">
							{#if item.source === 'my-papers'}
								<span class="source-badge my" title="Mine">
									<span class="desktop-only">Mine</span>
									<span class="mobile-only">M</span>
								</span>
							{:else}
								<span class="source-badge community" title="Community">
									<span class="desktop-only">Community</span>
									<span class="mobile-only">C</span>
								</span>
							{/if}
						</td>
						<td class="title-col">
							<div class="title-wrapper">
								<span class="title-text">{item.paper.title}</span>
								{#if annotation}
									<span class="mobile-status completed" title="Completed">✓</span>
								{:else}
									<span class="mobile-status pending" title="Pending">○</span>
								{/if}
							</div>
						</td>
						<td class="authors-col desktop-only">
							{item.paper.authors?.slice(0, 3).join(', ') || '—'}
							{#if item.paper.authors?.length > 3}
								<span class="et-al">et al.</span>
							{/if}
						</td>
						<td class="year-col desktop-only">{item.paper.year || '—'}</td>
						<td class="count-col desktop-only">{annotationCounts[item.id] || 0}</td>
						<td class="status-col desktop-only">
							{#if annotation}
								<span class="status-badge completed">✓</span>
							{:else}
								<span class="status-badge pending">○</span>
							{/if}
						</td>
						<td class="rating-col desktop-only">
							{#if annotation}
								<span class="rating-display">
									{ratingLabels[annotation.interdisciplinarity_rating - 1]}
								</span>
							{:else}
								—
							{/if}
						</td>
					</tr>
				{:else if item.source === 'csv'}
					<!-- General dataset paper - need to fetch -->
					{#await getPaperById(item.id) then paperData}
						{#if matchesFilters(item, paperData, annotation)}
							<tr
								class:annotated={annotation}
								class="clickable-row"
								onclick={() => {
									const csvIndex = csvQueuePaperIds.indexOf(item.id)
									onJumpToPaper('csv-queue', csvIndex >= 0 ? csvIndex : 0)
								}}
							>
							<td class="number-col">{index + 1}</td>
							<td class="source-col">
								<span class="source-badge general" title="General">
									<span class="desktop-only">General</span>
									<span class="mobile-only">G</span>
								</span>
							</td>
							<td class="title-col">
								<div class="title-wrapper">
									<span class="title-text">{paperData?.title || 'Loading...'}</span>
									{#if annotation}
										<span class="mobile-status completed" title="Completed">✓</span>
									{:else}
										<span class="mobile-status pending" title="Pending">○</span>
									{/if}
								</div>
							</td>
							<td class="authors-col desktop-only">
								{paperData?.authors?.slice(0, 3).join(', ') || '—'}
								{#if paperData?.authors?.length > 3}
									<span class="et-al">et al.</span>
								{/if}
							</td>
							<td class="year-col desktop-only">{paperData?.year || '—'}</td>
							<td class="count-col desktop-only">{annotationCounts[item.id] || 0}</td>
							<td class="status-col desktop-only">
								{#if annotation}
									<span class="status-badge completed">✓</span>
								{:else}
									<span class="status-badge pending">○</span>
								{/if}
							</td>
							<td class="rating-col desktop-only">
								{#if annotation}
									<span class="rating-display">
										{ratingLabels[annotation.interdisciplinarity_rating - 1]}
									</span>
								{:else}
									—
								{/if}
							</td>
						</tr>
						{/if}
					{/await}
				{/if}
			{/each}
		</tbody>
	</table>
</div>

<style>
	header {
		margin-bottom: 2rem;
	}

	h1 {
		font-size: 2rem;
		margin: 0 0 0.5rem 0;
		color: #1a1a1a;
	}

	.subtitle {
		color: #666;
		margin: 0 0 1.5rem 0;
	}

	.filters {
		display: flex;
		gap: 0.75rem;
		margin-bottom: 1rem;
		align-items: center;
	}

	.sort-group {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.sort-group label {
		font-size: 0.875rem;
		color: #666;
		font-weight: 500;
		white-space: nowrap;
	}

	.sort-select {
		padding: 0.5rem 0.75rem;
		border: 1px solid #e0e0e0;
		border-radius: 4px;
		font-size: 0.875rem;
		background: white;
		cursor: pointer;
		font-weight: 500;
		color: #666;
		min-width: 0;
		width: auto;
	}

	.sort-select:hover {
		border-color: #2563eb;
	}

	.sort-select:focus {
		outline: none;
		border-color: #2563eb;
	}

	.overview-table {
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		overflow: hidden;
		margin-bottom: 2rem;
	}

	table {
		width: 100%;
		border-collapse: collapse;
	}

	th {
		background: #f5f5f5;
		padding: 0.5rem 0.75rem;
		text-align: left;
		font-weight: 600;
		font-size: 0.875rem;
		color: #666;
		border-bottom: 2px solid #e0e0e0;
		line-height: 1.2;
	}

	td {
		padding: 0.5rem 0.75rem;
		border-bottom: 1px solid #f0f0f0;
		font-size: 0.875rem;
		line-height: 1.3;
	}

	tr:last-child td {
		border-bottom: none;
	}

	tr:hover {
		background: #fafafa;
	}

	tr.annotated {
		background: #f0fdf4;
	}

	tr.annotated:hover {
		background: #dcfce7;
	}

	.number-col {
		width: 3rem;
		text-align: center;
		color: #999;
		font-weight: 500;
	}

	.source-col {
		width: 6rem;
		text-align: center;
	}

	.title-col {
		font-weight: 500;
		color: #1a1a1a;
	}

	.authors-col {
		color: #666;
		max-width: 15rem;
	}

	.et-al {
		font-style: italic;
		color: #999;
	}

	.year-col {
		width: 4rem;
		color: #666;
	}

	.count-col {
		width: 6rem;
		text-align: center;
		color: #2563eb;
		font-weight: 500;
	}

	.status-col {
		width: 4rem;
		text-align: center;
	}

	.rating-col {
		width: 8rem;
	}

	.status-badge {
		display: inline-block;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 0.75rem;
		font-weight: 600;
	}

	.status-badge.completed {
		background: #d1fae5;
		color: #065f46;
	}

	.status-badge.pending {
		background: #fef3c7;
		color: #92400e;
	}

	.rating-display {
		color: #2563eb;
		font-weight: 500;
	}

	.source-badge {
		display: inline-block;
		padding: 0.25rem 0.5rem;
		font-size: 0.75rem;
		font-weight: 600;
		border-radius: 4px;
		text-transform: uppercase;
		letter-spacing: 0.025em;
	}

	.source-badge.general {
		background: #dbeafe;
		color: #1e40af;
	}

	.source-badge.community {
		background: #fef3c7;
		color: #92400e;
	}

	.source-badge.my {
		background: #dcfce7;
		color: #166534;
	}

	/* Clickable row styles */
	.clickable-row {
		cursor: pointer;
		transition: transform 0.1s;
	}

	.clickable-row:active {
		transform: scale(0.995);
	}

	/* Title wrapper for mobile status indicator */
	.title-wrapper {
		display: block;
	}

	.title-text {
		display: inline;
	}

	.mobile-status {
		display: none;
	}

	.mobile-status.completed {
		color: #065f46;
	}

	.mobile-status.pending {
		color: #92400e;
	}

	/* Mobile-specific styles */
	.mobile-only {
		display: none;
	}

	@media (max-width: 768px) {

		.filters {
			flex-direction: column;
			align-items: stretch;
			gap: 0.5rem;
		}

		.sort-group {
			justify-content: space-between;
		}

		th.desktop-only,
		td.desktop-only {
			display: none !important;
		}

		span.desktop-only {
			display: none !important;
		}

		.mobile-only {
			display: inline !important;
		}

		.mobile-status {
			display: inline-block;
			font-size: 1rem;
			flex-shrink: 0;
		}

		.title-wrapper {
			display: flex;
			align-items: center;
			gap: 0.5rem;
			justify-content: space-between;
		}

		.title-text {
			flex: 1;
		}

		.overview-table {
			overflow-x: auto;
			-webkit-overflow-scrolling: touch;
		}

		table {
			min-width: 100%;
		}

		.number-col {
			width: 2rem;
			padding: 0.5rem 0.25rem;
		}

		.source-col {
			width: 2.5rem;
			padding: 0.5rem 0.25rem;
		}

		.source-badge {
			padding: 0.25rem 0.4rem;
			min-width: 1.75rem;
			text-align: center;
		}

		.title-col {
			min-width: 60vw;
		}

		th {
			padding: 0.5rem 0.5rem;
			font-size: 0.8rem;
		}

		td {
			padding: 0.5rem 0.5rem;
			font-size: 0.875rem;
		}

		.subtitle {
			font-size: 0.875rem;
		}
	}
</style>
