<script>
	let {
		mode = 'queue',
		totalAnnotated = 0,
		totalPapers = 0,
		remainingInQueue = 0,
		error = null
	} = $props()

	const title = $derived(mode === 'my-papers-queue' ? 'My Papers Queue' : 'General Annotation Queue')
	const subtitle = $derived(
		mode === 'my-papers-queue'
			? 'Annotate your own papers for interdisciplinarity'
			: 'Help us understand what makes research interdisciplinary'
	)
	const progressPercent = $derived((totalAnnotated / totalPapers) * 100)
</script>

<header>
	<h1>{title}</h1>
	<p class="subtitle">{subtitle}</p>

	<div class="progress">
		<div class="progress-bar">
			<div class="progress-fill" style="width: {progressPercent}%"></div>
		</div>
		<span class="progress-text">
			{totalAnnotated} of {totalPapers} total annotated
			{#if remainingInQueue === 0}
				<span class="complete-badge">✅ Queue done!</span>
			{:else}
				<span class="queue-count">({remainingInQueue} remaining)</span>
			{/if}
		</span>
	</div>
</header>

{#if error}
	<div class="error-banner">
		{error}
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

	.complete-badge {
		margin-left: 0.5rem;
		font-weight: 600;
		color: #059669;
	}

	.queue-count {
		color: #2563eb;
		font-weight: 500;
	}

	.error-banner {
		background: #fee;
		border: 1px solid #fcc;
		color: #c33;
		padding: 1rem;
		border-radius: 4px;
		margin-bottom: 1rem;
	}
</style>
