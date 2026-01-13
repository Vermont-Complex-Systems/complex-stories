<script>
	import { getUniquePaperIds } from '../data/loader.js'
	import { getPaperById, annotatePaper, getCurrentUser, getMyAnnotations, getWorksByAuthor, getAnnotationStats, getAgreementData, getCommunityQueuePapers } from '../data/data.remote'
	import FingerprintJS from '@fingerprintjs/fingerprintjs'
	import { onMount } from 'svelte'
	import TopBar from './TopBar.svelte'
	import OverviewTable from './OverviewTable.svelte'
	import QueueHeader from './QueueHeader.svelte'
	import PaperAnnotationCard from './PaperAnnotationCard.svelte'
	import StatsView from './StatsView.svelte'
	import Story from './Story.svelte'

	// State
	let currentIndex = $state(0)
	let fingerprint = $state(null)
	let selectedRating = $state(null)
	let isSubmitting = $state(false)
	let error = $state(null)
	let mode = $state('story') // 'csv-queue', 'community-queue', 'my-papers-queue', 'overview', 'stats'
	let myAnnotations = $state([])
	let myPapers = $state([]) // User's own papers from ORCID/OpenAlex
	let annotationCounts = $state({}) // Per-paper annotation counts
	let stats = $state({}) // Full stats object
	let agreementData = $state(null) // Agreement data for sorting by disagreement
	let paperIds = $state([]) // CSV paper IDs only
	let generalPapers = $state([]) // Community papers with full objects

	// Filter to only show uncompleted papers in queue modes
	const csvQueuePaperIds = $derived(
		paperIds.filter(paperId =>
			!myAnnotations.find(a => a.paper_id === paperId)
		)
	)

	const communityQueuePaperIds = $derived(
		generalPapers
			.filter(paper => !myAnnotations.find(a => a.paper_id === paper.id))
			.map(paper => paper.id)
	)

	const myPapersQueueIds = $derived(
		myPapers
			.filter(paper => !myAnnotations.find(a => a.paper_id === paper.id))
			.map(paper => paper.id)
	)

	// Get current paper ID based on mode
	const activePaperIds = $derived.by(() => {
		if (mode === 'csv-queue') return csvQueuePaperIds
		if (mode === 'community-queue') return communityQueuePaperIds
		if (mode === 'my-papers-queue') return myPapersQueueIds
		// Overview mode - combine all
		return [...paperIds, ...generalPapers.map(p => p.id)]
	})

	// Initialize fingerprint and load annotations on mount
	onMount(async () => {
		// Get fingerprint
		const fp = await FingerprintJS.load()
		const result = await fp.get()
		fingerprint = result.visitorId

		// Load general queue papers (CSV + community)
		await loadPaperQueue()

		// Load annotations for queue filtering
		await loadAnnotations()

		// Load annotation stats (includes per-paper counts)
		await loadStats()

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

	// Load paper queue (CSV IDs + community paper objects)
	async function loadPaperQueue() {
		try {
			// Get CSV papers (just IDs)
			paperIds = getUniquePaperIds()

			// Get community-contributed papers (full objects)
			const communityData = await getCommunityQueuePapers()
			generalPapers = communityData.community_papers || []

			// Remove duplicates: if a paper is in both CSV and community, keep community version
			const communityIds = new Set(generalPapers.map(p => p.id))
			paperIds = paperIds.filter(id => !communityIds.has(id))
		} catch (err) {
			console.error('Failed to load community queue:', err)
			// Fall back to just CSV papers
			paperIds = getUniquePaperIds()
			generalPapers = []
		}
	}

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

	// Load stats including per-paper counts
	async function loadStats() {
		try {
			const statsData = await getAnnotationStats()
			stats = statsData
			annotationCounts = statsData.per_paper_counts || {}
		} catch (err) {
			console.error('Failed to load stats:', err)
		}
	}

	// Load agreement data for sorting
	async function loadAgreementData() {
		try {
			agreementData = await getAgreementData()
		} catch (err) {
			console.error('Failed to load agreement data:', err)
		}
	}

	// Switch modes
	async function setMode(newMode) {
		mode = newMode
		currentIndex = 0
		selectedRating = null
		// Reload annotations and stats when switching to overview or stats
		if (mode === 'overview' || mode === 'stats') {
			await loadAnnotations()
			await loadStats()
			await loadAgreementData()
		}
	}

	// Jump to specific paper from overview
	function handleJumpToPaper(targetMode, index) {
		mode = targetMode
		currentIndex = index
		selectedRating = null
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

<TopBar
	{mode}
	generalQueueCount={csvQueuePaperIds.length}
	communityQueueCount={communityQueuePaperIds.length}
	myPapersCount={myPapers.length}
	myPapersQueueCount={myPapersQueueIds.length}
	onModeChange={setMode}
/>

<div class="dataset-preview-container">
	<div class="container">
		{#if mode === 'stats'}
			<StatsView {stats} {myAnnotations} {myPapers} {paperIds} {generalPapers} />
		{:else if mode === 'story'}
			<Story />
		{:else if mode === 'overview'}
			<OverviewTable
				{paperIds}
				{generalPapers}
				{myPapers}
				{myAnnotations}
				{myPapersQueueIds}
				{annotationCounts}
				{agreementData}
				csvQueuePaperIds={csvQueuePaperIds}
				communityQueuePaperIds={communityQueuePaperIds}
				onJumpToPaper={handleJumpToPaper}
				onSortedIdsChange={(csvIds, communityPapersList, myPapersList) => {
					paperIds = csvIds
					generalPapers = communityPapersList
					myPapers = myPapersList
				}}
			/>
		{:else if mode === 'csv-queue' || mode === 'community-queue' || mode === 'my-papers-queue'}
			<QueueHeader
				{mode}
				totalAnnotated={myAnnotations.length}
				totalPapers={paperIds.length + generalPapers.length + myPapers.length}
				remainingInQueue={activePaperIds.length}
				{error}
			/>

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
					<PaperAnnotationCard
						paper={paperData}
						bind:selectedRating
						{isSubmitting}
						onSubmit={handleSubmit}
						onPrevious={previousPaper}
						onNext={nextPaper}
						canGoPrevious={currentIndex > 0}
						canGoNext={currentIndex < activePaperIds.length - 1}
					/>
				{:catch err}
					<div class="error">Error loading paper: {err.message}</div>
				{/await}
			{/if}
		{/if}
	</div>
</div>

<style>
	:global(main:has(.dataset-preview-container)) {
		max-width: none;
		padding: 1.5rem var(--margin-left) 0.5rem var(--margin-left);
	}

	.container {
		max-width: 1200px !important;
		margin: 0 auto;
		padding: 2rem;
		font-family: system-ui, -apple-system, sans-serif;
	}

	/* Mobile styles */
	@media (max-width: 768px) {
		:global(main:has(.dataset-preview-container)) {
			padding: 1rem var(--margin-left-mobile) 0.5rem var(--margin-left-mobile);
		}

		.container {
			padding: 1rem;
		}
	}

	.loading {
		text-align: center;
		padding: 3rem;
		color: #666;
	}

	.error {
		padding: 2rem;
		text-align: center;
		color: #c33;
		background: #fee;
		border: 1px solid #fcc;
		border-radius: 8px;
	}

	.queue-empty {
		text-align: center;
		padding: 3rem;
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
	}

	.queue-empty h2 {
		font-size: 1.5rem;
		margin: 0 0 1rem 0;
		color: #059669;
	}

	.queue-empty p {
		color: #666;
		margin: 0.5rem 0;
	}
</style>
