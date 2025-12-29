<script>
	let {
		paper,
		selectedRating = $bindable(),
		isSubmitting = false,
		onSubmit = () => {},
		onPrevious = () => {},
		onNext = () => {},
		canGoPrevious = false,
		canGoNext = false
	} = $props()
</script>

{#if paper}
	<article class="paper">
		<h2>{paper.title}</h2>

		<div class="metadata">
			<span class="year">{paper.year || 'Year unknown'}</span>
			{#if paper.authors?.length > 0}
				<span class="authors">
					{paper.authors.join(', ')}
				</span>
			{/if}
			{#if paper.doi}
				<a href="{paper.doi}" target="_blank" rel="noopener noreferrer" class="doi-link">
					📄 View paper
				</a>
			{/if}
		</div>

		{#if paper.topics?.length > 0}
			<div class="topics">
				{#each paper.topics as topic}
					<span class="topic-tag">{topic.display_name}</span>
				{/each}
			</div>
		{/if}

		{#if paper.abstract}
			<div class="abstract">
				<h3>Abstract</h3>
				<p>{paper.abstract}</p>
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
				onclick={onSubmit}
				disabled={!selectedRating || isSubmitting}
			>
				{isSubmitting ? 'Submitting...' : 'Submit & Next'}
			</button>
		</div>

		<div class="navigation">
			<button onclick={onPrevious} disabled={!canGoPrevious}>
				← Previous
			</button>
			<button onclick={onNext} disabled={!canGoNext}>
				Skip →
			</button>
		</div>
	</article>
{:else}
	<div class="error">Failed to load paper</div>
{/if}

<style>
	.paper {
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		padding: 2rem;
		margin-bottom: 2rem;
	}

	h2 {
		font-size: 1.5rem;
		margin: 0 0 1rem 0;
		color: #1a1a1a;
		line-height: 1.3;
	}

	.metadata {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
		align-items: center;
		padding-bottom: 1rem;
		border-bottom: 1px solid #e0e0e0;
		margin-bottom: 1rem;
	}

	.year {
		font-weight: 600;
		color: #2563eb;
	}

	.authors {
		color: #666;
	}

	.doi-link {
		color: #2563eb;
		text-decoration: none;
		font-size: 0.875rem;
		transition: opacity 0.2s;
	}

	.doi-link:hover {
		opacity: 0.7;
	}

	.topics {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 1.5rem;
	}

	.topic-tag {
		background: #f0f0f0;
		padding: 0.25rem 0.75rem;
		border-radius: 16px;
		font-size: 0.75rem;
		color: #666;
	}

	.abstract {
		margin-bottom: 2rem;
	}

	.abstract h3 {
		font-size: 1rem;
		margin: 0 0 0.5rem 0;
		color: #1a1a1a;
	}

	.abstract p {
		color: #666;
		line-height: 1.6;
		margin: 0;
	}

	.rating-section {
		background: #f9fafb;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		padding: 1.5rem;
		margin-bottom: 1.5rem;
	}

	.rating-section h3 {
		margin: 0 0 0.5rem 0;
		font-size: 1.125rem;
		color: #1a1a1a;
	}

	.rating-help {
		color: #666;
		font-size: 0.875rem;
		margin: 0 0 1rem 0;
	}

	.rating-buttons {
		display: flex;
		gap: 0.75rem;
		margin-bottom: 1rem;
	}

	.rating-btn {
		flex: 1;
		padding: 1rem;
		border: 2px solid #e0e0e0;
		border-radius: 8px;
		background: white;
		font-size: 1.125rem;
		font-weight: 600;
		color: #666;
		cursor: pointer;
		transition: all 0.2s;
	}

	.rating-btn:hover:not(:disabled) {
		border-color: #2563eb;
		background: #f0f7ff;
	}

	.rating-btn.selected {
		border-color: #2563eb;
		background: #2563eb;
		color: white;
	}

	.rating-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.submit-btn {
		width: 100%;
		padding: 0.875rem;
		border: none;
		border-radius: 8px;
		background: #2563eb;
		color: white;
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		transition: background 0.2s;
	}

	.submit-btn:hover:not(:disabled) {
		background: #1e40af;
	}

	.submit-btn:disabled {
		background: #cbd5e1;
		cursor: not-allowed;
	}

	.navigation {
		display: flex;
		gap: 1rem;
	}

	.navigation button {
		flex: 1;
		padding: 0.75rem;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		background: white;
		color: #666;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
	}

	.navigation button:hover:not(:disabled) {
		border-color: #2563eb;
		color: #2563eb;
	}

	.navigation button:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	.error {
		padding: 2rem;
		text-align: center;
		color: #c33;
		background: #fee;
		border: 1px solid #fcc;
		border-radius: 8px;
	}
</style>
