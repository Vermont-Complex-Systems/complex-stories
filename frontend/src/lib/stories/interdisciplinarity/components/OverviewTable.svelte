<script>
	import { getPaperById } from '../data/data.remote'

	let {
		paperIds = [],
		myPapers = [],
		myAnnotations = [],
		myPapersQueueIds = [],
		generalQueuePaperIds = [],
		annotationCounts = {},
		onJumpToPaper = (mode, index) => {}
	} = $props()

	const totalPapers = $derived(paperIds.length + myPapers.length)
	const allPapersList = $derived([
		...paperIds.map(id => ({ id, source: 'general' })),
		...myPapers.map(p => ({ id: p.id, source: 'my-papers', paper: p }))
	])

	const ratingLabels = ['Not at all', 'Not really', 'Undecided', 'Somewhat', 'Very much']
</script>

<header>
	<h1>Your Annotation Progress</h1>
	<p class="subtitle">
		{myAnnotations.length} of {totalPapers} papers annotated
		({paperIds.length} general + {myPapers.length} your papers)
	</p>
</header>

<div class="overview-table">
	<table>
		<thead>
			<tr>
				<th>#</th>
				<th>Source</th>
				<th>Title</th>
				<th>Authors</th>
				<th>Year</th>
				<th>Annotations</th>
				<th>Status</th>
				<th>Rating</th>
				<th>Action</th>
			</tr>
		</thead>
		<tbody>
			{#each allPapersList as item, index}
				{@const annotation = myAnnotations.find(a => a.paper_id === item.id)}
				{#if item.source === 'my-papers'}
					<!-- User's own paper - already have data -->
					<tr class:annotated={annotation} class="my-paper">
						<td class="number-col">{index + 1}</td>
						<td class="source-col"><span class="source-badge my">Mine</span></td>
						<td class="title-col">{item.paper.title}</td>
						<td class="authors-col">
							{item.paper.authors?.slice(0, 3).join(', ') || '—'}
							{#if item.paper.authors?.length > 3}
								<span class="et-al">et al.</span>
							{/if}
						</td>
						<td class="year-col">{item.paper.year || '—'}</td>
						<td class="count-col">{annotationCounts[item.id] || 0}</td>
						<td class="status-col">
							{#if annotation}
								<span class="status-badge completed">✓</span>
							{:else}
								<span class="status-badge pending">○</span>
							{/if}
						</td>
						<td class="rating-col">
							{#if annotation}
								<span class="rating-display">
									{ratingLabels[annotation.interdisciplinarity_rating - 1]}
								</span>
							{:else}
								—
							{/if}
						</td>
						<td class="action-col">
							<button class="jump-btn" onclick={() => {
								const myPaperIndex = myPapersQueueIds.indexOf(item.id)
								if (myPaperIndex >= 0) {
									onJumpToPaper('my-papers-queue', myPaperIndex)
								} else if (annotation) {
									onJumpToPaper('my-papers-queue', 0)
									alert('This paper is already annotated. You can re-annotate it from the My Papers queue.')
								}
							}}>
								{annotation ? 'Re-annotate' : 'Annotate'}
							</button>
						</td>
					</tr>
				{:else}
					<!-- General dataset paper - need to fetch -->
					{#await getPaperById(item.id) then paperData}
						<tr class:annotated={annotation}>
							<td class="number-col">{index + 1}</td>
							<td class="source-col"><span class="source-badge general">General</span></td>
							<td class="title-col">{paperData?.title || 'Loading...'}</td>
							<td class="authors-col">
								{paperData?.authors?.slice(0, 3).join(', ') || '—'}
								{#if paperData?.authors?.length > 3}
									<span class="et-al">et al.</span>
								{/if}
							</td>
							<td class="year-col">{paperData?.year || '—'}</td>
							<td class="count-col">{annotationCounts[item.id] || 0}</td>
							<td class="status-col">
								{#if annotation}
									<span class="status-badge completed">✓</span>
								{:else}
									<span class="status-badge pending">○</span>
								{/if}
							</td>
							<td class="rating-col">
								{#if annotation}
									<span class="rating-display">
										{ratingLabels[annotation.interdisciplinarity_rating - 1]}
									</span>
								{:else}
									—
								{/if}
							</td>
							<td class="action-col">
								<button class="jump-btn" onclick={() => {
									const generalIndex = generalQueuePaperIds.indexOf(item.id)
									onJumpToPaper('queue', generalIndex >= 0 ? generalIndex : 0)
								}}>
									{annotation ? 'Re-annotate' : 'Annotate'}
								</button>
							</td>
						</tr>
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
		padding: 0.75rem;
		text-align: left;
		font-weight: 600;
		font-size: 0.875rem;
		color: #666;
		border-bottom: 2px solid #e0e0e0;
	}

	td {
		padding: 0.75rem;
		border-bottom: 1px solid #f0f0f0;
		font-size: 0.875rem;
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

	.action-col {
		width: 8rem;
		text-align: center;
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

	.source-badge.my {
		background: #dcfce7;
		color: #166534;
	}

	.jump-btn {
		padding: 0.375rem 0.75rem;
		font-size: 0.75rem;
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 4px;
		cursor: pointer;
		transition: all 0.2s;
		font-weight: 500;
	}

	.jump-btn:hover {
		background: #2563eb;
		color: white;
		border-color: #2563eb;
	}
</style>
