<script>
	import { getUniquePaperIds } from '../data/loader.js'
	import { getPaperById, annotatePaper, getCurrentUser, logoutUser, getMyAnnotations } from '../data/data.remote'
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
	let currentUser = $state(null)
	let selectedRating = $state(null)
	let isSubmitting = $state(false)
	let error = $state(null)
	let isLoggingOut = $state(false)
	let showOverview = $state(false)
	let myAnnotations = $state([])

	// Initialize fingerprint and user on mount
	onMount(async () => {
		// Get fingerprint
		const fp = await FingerprintJS.load()
		const result = await fp.get()
		fingerprint = result.visitorId
		console.log('Fingerprint loaded:', fingerprint)

		// Check if user is logged in
		try {
			currentUser = await getCurrentUser()
			console.log('Current user:', currentUser)
		} catch (err) {
			console.log('No user logged in')
		}
	})

	// Current paper ID
	const currentPaperId = $derived(paperIds[currentIndex])

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

	// Handle logout
	async function handleLogout() {
		isLoggingOut = true
		try {
			await logoutUser()
			currentUser = null
		} catch (err) {
			error = err.message
		} finally {
			isLoggingOut = false
		}
	}

	// Load annotations
	async function loadAnnotations() {
		try {
			const params = currentUser ? {} : { fingerprint }
			const result = await getMyAnnotations(params)
			myAnnotations = result.annotations || []
		} catch (err) {
			console.error('Failed to load annotations:', err)
		}
	}

	// Toggle overview
	async function toggleOverview() {
		showOverview = !showOverview
		if (showOverview) {
			await loadAnnotations()
		}
	}

	// Jump to specific paper
	function jumpToPaper(index) {
		currentIndex = index
		selectedRating = null
		showOverview = false
	}

	// Handle rating submission
	async function handleSubmit() {
		if (!selectedRating) return

		// Require fingerprint only if not logged in
		if (!currentUser && !fingerprint) {
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
			if (!currentUser && fingerprint) {
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
		if (currentIndex < paperIds.length - 1) {
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
		<button class="overview-btn" onclick={toggleOverview}>
			{showOverview ? '← Back to Annotation' : '📊 View Progress'}
		</button>
		{#if currentUser}
			<a href="{base}/auth" class="avatar-button">
				<Avatar.Root class="avatar-root">
					<Avatar.Fallback class="avatar-fallback">
						{getUserInitials(currentUser.username)}
					</Avatar.Fallback>
				</Avatar.Root>
			</a>
		{:else if fingerprint}
			<span class="anonymous-badge">🕵️ Anonymous</span>
		{:else}
			<span class="loading-badge">⏳ Loading...</span>
		{/if}
	</div>
</div>

<div class="interdisciplinarity-container">
	{#if showOverview}
		<!-- Overview / Progress Table -->
		<header>
			<h1>Your Annotation Progress</h1>
			<p class="subtitle">{myAnnotations.length} of {paperIds.length} papers annotated</p>
		</header>

		<div class="overview-table">
			<table>
				<thead>
					<tr>
						<th>#</th>
						<th>Title</th>
						<th>Authors</th>
						<th>Year</th>
						<th>Status</th>
						<th>Rating</th>
						<th>Action</th>
					</tr>
				</thead>
				<tbody>
					{#each paperIds as paperId, index}
						{@const annotation = myAnnotations.find(a => a.paper_id === paperId)}
						{#await getPaperById(paperId) then paperData}
							<tr class:annotated={annotation}>
								<td class="number-col">{index + 1}</td>
								<td class="title-col">{paperData?.title || 'Loading...'}</td>
								<td class="authors-col">
									{paperData?.authors?.slice(0, 3).join(', ') || '—'}
									{#if paperData?.authors?.length > 3}
									<span class="et-al">et al.</span>
									{/if}
								</td>
								<td class="year-col">{paperData?.year || 'Loading...'}</td>
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
									<button class="jump-btn" onclick={() => jumpToPaper(index)}>
										{annotation ? 'Re-annotate' : 'Annotate'}
									</button>
								</td>
							</tr>
						{/await}
					{/each}
				</tbody>
			</table>
		</div>
	{:else}
		<!-- Annotation Mode -->
		<header>
			<h1>Interdisciplinarity Annotation</h1>
			<p class="subtitle">Help us understand what makes research interdisciplinary</p>

			<div class="progress">
				<div class="progress-bar">
					<div class="progress-fill" style="width: {(myAnnotations.length / paperIds.length) * 100}%"></div>
				</div>
				<span class="progress-text">{myAnnotations.length} of {paperIds.length} annotated</span>
			</div>
		</header>

		{#if error}
			<div class="error-banner">
				{error}
			</div>
		{/if}

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
					<button onclick={nextPaper} disabled={currentIndex === paperIds.length - 1}>
						Skip →
					</button>
				</div>
			</article>
		{:else}
			<div class="error">Failed to load paper</div>
		{/if}
	{:catch err}
		<div class="error">Error: {err.message}</div>
	{/await}

		{#if currentIndex >= paperIds.length}
			<div class="completion">
				<h2>🎉 All papers annotated!</h2>
				<p>Thank you for your contributions to understanding interdisciplinarity in research.</p>
			</div>
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

	.avatar-button {
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

	.avatar-button:hover {
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

	:global(main:has(.interdisciplinarity-container)) {
		max-width: none;
		padding: 1.5rem 1.5rem 0.5rem 9.5rem;
		margin: 0 auto;
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

	.completion {
		text-align: center;
		padding: 4rem 2rem;
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
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
