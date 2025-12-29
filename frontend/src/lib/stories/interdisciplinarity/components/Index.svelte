<script>
	import { getUniquePaperIds } from '../data/loader.js'
	import { getPaperById, annotatePaper, getCurrentUser, logoutUser, getMyAnnotations, getWorksByAuthor } from '../data/data.remote'
	import FingerprintJS from '@fingerprintjs/fingerprintjs'
	import { onMount } from 'svelte'
	import { Avatar } from 'bits-ui'
	import { base } from '$app/paths'

	// Get user initials helper
	function getUserInitials(username) {
		if (!username) return 'U'
		const parts = username.split('_')
		if (parts.length >= 2) {
			return (parts[1][0] + parts[0][0]).toUpperCase()
		}
		return username.slice(0, 2).toUpperCase()
	}

	// Get list of paper IDs to annotate
	const paperIds = getUniquePaperIds()

	// Current paper index
	let currentIndex = $state(0)
	let fingerprint = $state(null)
	let selectedRating = $state(null)
	let isSubmitting = $state(false)
	let error = $state(null)
	let mode = $state('overview') // 'queue', 'my-papers-queue', 'overview'
	let myAnnotations = $state([])
	let myPapers = $state([]) // User's own papers from ORCID/OpenAlex

	// Filter to only show uncompleted papers in queue modes
	const generalQueuePaperIds = $derived(
		paperIds.filter(paperId =>
			!myAnnotations.find(a => a.paper_id === paperId)
		)
	)

	const myPapersQueueIds = $derived(
		myPapers
			.filter(paper => !myAnnotations.find(a => a.paper_id === paper.id))
			.map(paper => paper.id)
	)

	// Get current paper ID based on mode
	const activePaperIds = $derived(
		mode === 'queue' ? generalQueuePaperIds :
		mode === 'my-papers-queue' ? myPapersQueueIds :
		paperIds
	)

	// Initialize fingerprint and load annotations on mount
	onMount(async () => {
		// Get fingerprint
		const fp = await FingerprintJS.load()
		const result = await fp.get()
		fingerprint = result.visitorId
		console.log('Fingerprint loaded:', fingerprint)

		// Load annotations for queue filtering
		await loadAnnotations()

		// Load user's papers if they have ORCID/OpenAlex ID
		try {
			const user = await getCurrentUser()
			if (user?.orcid_id || user?.openalex_id) {
				const authorId = user.orcid_id || user.openalex_id
				const worksData = await getWorksByAuthor(authorId)
				myPapers = worksData.results || []
			}
		} catch (err) {
			// User not logged in or no identifier
		}
	})

	// Current paper ID
	const currentPaperId = $derived(activePaperIds[currentIndex])

	// Fetch current paper (reactive)
	const paper = $derived.by(async () => {
		if (!currentPaperId) return null
		try {
			return await getPaperById(currentPaperId)
		} catch (err) {
			error = err.message
			return null
		}
	})

	// Load annotations
	async function loadAnnotations() {
		try {
			// Check if user is logged in
			let user = null
			try {
				user = await getCurrentUser()
			} catch (err) {
				// User not logged in
			}

			const params = user ? {} : { fingerprint }
			const result = await getMyAnnotations(params)
			myAnnotations = result.annotations || []
		} catch (err) {
			console.error('Failed to load annotations:', err)
		}
	}

	// Switch modes
	async function setMode(newMode) {
		mode = newMode
		currentIndex = 0
		selectedRating = null
		// Reload annotations when switching to overview
		if (mode === 'overview') {
			await loadAnnotations()
		}
	}

	// Jump to specific paper from overview
	function jumpToPaper(index) {
		currentIndex = index
		selectedRating = null
		mode = 'queue'
	}

	// Handle rating submission
	async function handleSubmit() {
		if (!selectedRating) return

		// Check if user is logged in
		let user = null
		try {
			user = await getCurrentUser()
		} catch (err) {
			// User not logged in
		}

		// Require fingerprint only if not logged in
		if (!user && !fingerprint) {
			error = 'Waiting for fingerprint initialization...'
			return
		}

		isSubmitting = true
		error = null

		try {
			const payload = {
				paper_id: currentPaperId,
				interdisciplinarity_rating: selectedRating
			}

			// Add fingerprint only if not logged in (backend prefers user_id over fingerprint)
			if (!user && fingerprint) {
				payload.fingerprint = fingerprint
			}

			await annotatePaper(payload)

			// Reload annotations
			await loadAnnotations()

			// Move to next paper
			selectedRating = null
			currentIndex++
		} catch (err) {
			error = err.message
		} finally {
			isSubmitting = false
		}
	}

	// Navigate to previous paper
	function previousPaper() {
		if (currentIndex > 0) {
			currentIndex--
			selectedRating = null
			error = null
		}
	}

	// Navigate to next paper (skip without rating)
	function nextPaper() {
		if (currentIndex < activePaperIds.length - 1) {
			currentIndex++
			selectedRating = null
			error = null
		}
	}
</script>

<!-- Simple top bar with logo and auth -->
<div class="top-bar">
	<a href="{base}/" class="logo-link">
		<img src="{base}/octopus-swim-right.png" alt="Home" class="octopus-icon" />
	</a>
	<div class="auth-section">
		<div class="mode-switcher">
			<button
				class="mode-btn"
				class:active={mode === 'overview'}
				onclick={() => setMode('overview')}
			>
				📊 Overview
			</button>
			<button
				class="mode-btn"
				class:active={mode === 'queue'}
				onclick={() => setMode('queue')}
				disabled={generalQueuePaperIds.length === 0}
			>
				📝 General Queue ({generalQueuePaperIds.length})
			</button>
			{#if myPapers.length > 0}
				<button
					class="mode-btn"
					class:active={mode === 'my-papers-queue'}
					onclick={() => setMode('my-papers-queue')}
					disabled={myPapersQueueIds.length === 0}
				>
					📄 My Papers ({myPapersQueueIds.length})
				</button>
			{/if}
		</div>
		{#await getCurrentUser()}
			<!-- Loading auth state -->
		{:then user}
			{#if user}
				<a href="{base}/auth" class="avatar-button">
					<Avatar.Root class="avatar-root">
						<Avatar.Fallback class="avatar-fallback">
							{getUserInitials(user.username)}
						</Avatar.Fallback>
					</Avatar.Root>
				</a>
			{:else}
				<a href="{base}/auth" class="login-button">
					Log in
				</a>
			{/if}
		{:catch}
			<a href="{base}/auth" class="login-button">
				Log in
			</a>
		{/await}
	</div>
</div>

<div class="dataset-preview-container">
<div class="container"></div>
	{#if mode === 'overview'}
		<!-- Progress Overview Table -->
		{@const totalPapers = paperIds.length + myPapers.length}
		{@const allPapersList = [
			...paperIds.map(id => ({ id, source: 'general' })),
			...myPapers.map(p => ({ id: p.id, source: 'my-papers', paper: p }))
		]}
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
											{['Not at all', 'Not really', 'Undecided', 'Somewhat', 'Very much'][annotation.interdisciplinarity_rating - 1]}
										</span>
									{:else}
										—
									{/if}
								</td>
								<td class="action-col">
									<button class="jump-btn" onclick={() => {
										// Switch to my-papers-queue and find this paper
										const myPaperIndex = myPapersQueueIds.indexOf(item.id)
										if (myPaperIndex >= 0) {
											mode = 'my-papers-queue'
											currentIndex = myPaperIndex
											selectedRating = null
										} else if (annotation) {
											// Paper already annotated, allow re-annotation
											mode = 'my-papers-queue'
											currentIndex = 0
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
												{['Not at all', 'Not really', 'Undecided', 'Somewhat', 'Very much'][annotation.interdisciplinarity_rating - 1]}
											</span>
										{:else}
											—
										{/if}
									</td>
									<td class="action-col">
										<button class="jump-btn" onclick={() => {
											const generalIndex = paperIds.indexOf(item.id)
											if (generalIndex >= 0) {
												mode = 'queue'
												currentIndex = generalQueuePaperIds.indexOf(item.id)
												if (currentIndex < 0) currentIndex = 0
												selectedRating = null
											}
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
	{:else if mode === 'my-papers-queue' || mode === 'queue'}
		<!-- Annotation Queue Mode (General or My Papers) -->
		<header>
			<h1>
				{mode === 'my-papers-queue' ? 'My Papers Queue' : 'General Annotation Queue'}
			</h1>
			<p class="subtitle">
				{mode === 'my-papers-queue'
					? 'Annotate your own papers for interdisciplinarity'
					: 'Help us understand what makes research interdisciplinary'}
			</p>

			<div class="progress">
				<div class="progress-bar">
					<div class="progress-fill" style="width: {(myAnnotations.length / paperIds.length) * 100}%"></div>
				</div>
				<span class="progress-text">
					{myAnnotations.length} of {paperIds.length} total annotated
					{#if activePaperIds.length === 0}
						<span class="complete-badge">✅ Queue done!</span>
					{:else}
						<span class="queue-count">({activePaperIds.length} remaining)</span>
					{/if}
				</span>
			</div>
		</header>

		{#if error}
			<div class="error-banner">
				{error}
			</div>
		{/if}

	{#if activePaperIds.length === 0}
		<div class="queue-empty">
			<h2>🎉 Queue Complete!</h2>
			<p>You've annotated all papers in this queue.</p>
			<p>Click "📊 Overview" to review your annotations or re-annotate any paper.</p>
		</div>
	{:else}
		{#await paper}
			<div class="loading">Loading paper...</div>
		{:then paperData}
			{#if paperData}
			<article class="paper">
				<h2>{paperData.title}</h2>

				<div class="metadata">
					<span class="year">{paperData.year || 'Year unknown'}</span>
					{#if paperData.authors?.length > 0}
						<span class="authors">
							{paperData.authors.join(', ')}
						</span>
					{/if}
					{#if paperData.doi}
						<a href="{paperData.doi}" target="_blank" rel="noopener noreferrer" class="doi-link">
							📄 View paper
						</a>
					{/if}
				</div>

				{#if paperData.topics?.length > 0}
					<div class="topics">
						{#each paperData.topics as topic}
							<span class="topic-tag">{topic.display_name}</span>
						{/each}
					</div>
				{/if}

				{#if paperData.abstract}
					<div class="abstract">
						<h3>Abstract</h3>
						<p>{paperData.abstract}</p>
					</div>
				{/if}

				<div class="rating-section">
					<h3>How interdisciplinary is this paper?</h3>
					<p class="rating-help">
						1 = Very much &nbsp;•&nbsp; 5 = Not at all
					</p>

					<div class="rating-buttons">
						{#each [1, 2, 3, 4, 5] as rating}
							<button
								class="rating-btn"
								class:selected={selectedRating === rating}
								onclick={() => selectedRating = rating}
								disabled={isSubmitting}
							>
								{rating}
							</button>
						{/each}
					</div>

					<button
						class="submit-btn"
						onclick={handleSubmit}
						disabled={!selectedRating || isSubmitting}
					>
						{isSubmitting ? 'Submitting...' : 'Submit & Next'}
					</button>
				</div>

				<div class="navigation">
					<button onclick={previousPaper} disabled={currentIndex === 0}>
						← Previous
					</button>
					<button onclick={nextPaper} disabled={currentIndex === activePaperIds.length - 1}>
						Skip →
					</button>
				</div>
			</article>
			{:else}
				<div class="error">Failed to load paper</div>
			{/if}
		{:catch err}
			<div class="error">Error loading paper: {err.message}</div>
		{/await}
	{/if}
{/if}
</div>

<style>
	.top-bar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem 2rem;
		background: white;
		border-bottom: 1px solid #e0e0e0;
		position: sticky;
		top: 0;
		z-index: 100;
	}

	.logo-link {
		display: flex;
		align-items: center;
		text-decoration: none;
		transition: transform 0.2s;
		transform: translateY(5px);
	}

	.logo-link:hover {
		transform: translateY(-2px);
	}

	.octopus-icon {
		height: 4rem;
		object-fit: contain;
	}

	.auth-section {
		display: flex;
		align-items: center;
		gap: 1rem;
		font-size: 0.875rem;
	}

	.mode-switcher {
		display: flex;
		gap: 0.5rem;
		margin-right: 1rem;
	}

	.mode-btn {
		padding: 0.5rem 1rem;
		border: 1px solid #e0e0e0;
		border-radius: 0.5rem;
		background: white;
		color: #666;
		font-size: 0.875rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	.mode-btn:hover {
		background: #f5f5f5;
		border-color: #ccc;
	}

	.mode-btn.active {
		background: #1a1a1a;
		color: white;
		border-color: #1a1a1a;
	}

	.mode-btn:disabled {
		opacity: 0.4;
		cursor: not-allowed;
		background: #f5f5f5;
	}

	.avatar-button,
	.login-button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		height: 2.5rem;
		padding: 0 0.75rem;
		border-radius: 0.5rem;
		background: transparent;
		color: #1a1a1a;
		text-decoration: none;
		font-weight: 500;
		font-size: 0.875rem;
		transition: all 0.2s;
		cursor: pointer;
	}

	.avatar-button:hover,
	.login-button:hover {
		background: rgba(0, 0, 0, 0.05);
		transform: scale(1.05);
	}

	:global(.avatar-root) {
		width: 2rem;
		height: 2rem;
		border-radius: 50%;
		overflow: hidden;
		flex-shrink: 0;
	}

	:global(.avatar-fallback) {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		background: #1a1a1a;
		color: white;
		font-weight: 700;
		font-size: 0.75rem;
		text-transform: uppercase;
	}

	.anonymous-badge {
		color: #e65100;
		font-weight: 500;
	}

	.loading-badge {
		color: #1565c0;
		font-weight: 500;
	}

	.overview-btn {
		padding: 0.5rem 1rem;
		font-size: 0.875rem;
		background: #2563eb;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		transition: all 0.2s;
		font-weight: 500;
	}

	.overview-btn:hover {
		background: #1d4ed8;
	}

	.overview-table {
		margin-top: 2rem;
		overflow-x: auto;
	}

	.overview-table table {
		width: 100%;
		border-collapse: collapse;
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		overflow: hidden;
	}

	.overview-table th {
		background: #f5f5f5;
		padding: 0.75rem 1rem;
		text-align: left;
		font-weight: 600;
		font-size: 0.875rem;
		color: #666;
		border-bottom: 2px solid #e0e0e0;
	}

	.overview-table td {
		padding: 0.75rem 1rem;
		border-bottom: 1px solid #f0f0f0;
		font-size: 0.875rem;
	}

	.overview-table tr.annotated {
		background: #f9fafb;
	}

	.overview-table tr:hover {
		background: #f5f7fa;
	}

	.paper-id {
		font-family: monospace;
		color: #666;
	}

	.status-badge {
		display: inline-block;
		padding: 0.25rem 0.75rem;
		border-radius: 12px;
		font-size: 0.75rem;
		font-weight: 500;
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

	.source-col {
		text-align: center;
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

	:global(main:has(.dataset-preview-container)) {
		max-width: none;
		padding: 1.5rem 1.5rem 0.5rem 9.5rem;
	}

	.container {
		max-width: 1200px !important;
		margin: 0 auto;
		padding: 2rem;
		font-family: system-ui, -apple-system, sans-serif;
	}

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

	.progress {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.progress-bar {
		flex: 1;
		height: 8px;
		background: #e0e0e0;
		border-radius: 4px;
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		background: #2563eb;
		transition: width 0.3s ease;
	}

	.progress-text {
		font-size: 0.875rem;
		color: #666;
		white-space: nowrap;
	}

	.error-banner {
		background: #fee;
		border: 1px solid #fcc;
		color: #c33;
		padding: 1rem;
		border-radius: 4px;
		margin-bottom: 1rem;
	}

	.loading {
		text-align: center;
		padding: 3rem;
		color: #666;
	}

	.paper {
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		padding: 2rem;
		box-shadow: 0 2px 4px rgba(0,0,0,0.05);
	}

	.paper h2 {
		font-size: 1.5rem;
		margin: 0 0 1rem 0;
		line-height: 1.4;
		color: #1a1a1a;
	}

	.metadata {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
		align-items: center;
		margin-bottom: 1rem;
		font-size: 0.875rem;
		color: #666;
	}

	.year {
		font-weight: 600;
	}

	.doi-link {
		color: #2563eb;
		text-decoration: none;
		font-weight: 500;
		display: inline-flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		transition: all 0.2s;
	}

	.doi-link:hover {
		background: #eff6ff;
		text-decoration: underline;
	}

	.topics {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 1.5rem;
	}

	.topic-tag {
		background: #e3f2fd;
		color: #1565c0;
		padding: 0.25rem 0.75rem;
		border-radius: 12px;
		font-size: 0.75rem;
		font-weight: 500;
	}

	.abstract {
		margin: 1.5rem 0;
		padding: 1.5rem;
		background: #f9f9f9;
		border-radius: 4px;
	}

	.abstract h3 {
		font-size: 1rem;
		margin: 0 0 0.75rem 0;
		color: #333;
	}

	.abstract p {
		margin: 0;
		line-height: 1.6;
		color: #444;
	}

	.rating-section {
		margin: 2rem 0;
		padding: 1.5rem;
		background: #fafafa;
		border-radius: 8px;
	}

	.rating-section h3 {
		font-size: 1.125rem;
		margin: 0 0 0.5rem 0;
		color: #1a1a1a;
	}

	.rating-help {
		font-size: 0.875rem;
		color: #666;
		margin: 0 0 1rem 0;
	}

	.rating-buttons {
		display: flex;
		gap: 0.75rem;
		margin-bottom: 1.5rem;
	}

	.rating-btn {
		flex: 1;
		padding: 1rem;
		font-size: 1.25rem;
		font-weight: 600;
		background: white;
		border: 2px solid #e0e0e0;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.2s;
	}

	.rating-btn:hover:not(:disabled) {
		border-color: #2563eb;
		background: #f0f7ff;
	}

	.rating-btn.selected {
		background: #2563eb;
		color: white;
		border-color: #2563eb;
	}

	.rating-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.submit-btn {
		width: 100%;
		padding: 1rem;
		font-size: 1rem;
		font-weight: 600;
		background: #2563eb;
		color: white;
		border: none;
		border-radius: 8px;
		cursor: pointer;
		transition: background 0.2s;
	}

	.submit-btn:hover:not(:disabled) {
		background: #1d4ed8;
	}

	.submit-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.navigation {
		display: flex;
		gap: 1rem;
		margin-top: 2rem;
		padding-top: 1.5rem;
		border-top: 1px solid #e0e0e0;
	}

	.navigation button {
		flex: 1;
		padding: 0.75rem;
		font-size: 0.875rem;
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 4px;
		cursor: pointer;
		transition: all 0.2s;
	}

	.navigation button:hover:not(:disabled) {
		background: #f5f5f5;
		border-color: #999;
	}

	.navigation button:disabled {
		opacity: 0.3;
		cursor: not-allowed;
	}

	.completion,
	.queue-empty,
	.my-papers-placeholder {
		text-align: center;
		padding: 4rem 2rem;
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
	}

	.queue-empty h2,
	.my-papers-placeholder h1 {
		margin-bottom: 1rem;
		color: #1a1a1a;
	}

	.queue-empty p,
	.my-papers-placeholder p {
		color: #666;
		margin-bottom: 0.5rem;
	}

	.complete-badge {
		color: #10b981;
		font-weight: 600;
		margin-left: 0.5rem;
	}

	.queue-count {
		color: #666;
		font-size: 0.9em;
	}

	.completion h2 {
		font-size: 2rem;
		margin: 0 0 1rem 0;
		color: #1a1a1a;
	}

	.completion p {
		font-size: 1.125rem;
		color: #666;
		margin: 0;
	}

	.error {
		text-align: center;
		padding: 3rem;
		color: #c33;
	}
</style>
