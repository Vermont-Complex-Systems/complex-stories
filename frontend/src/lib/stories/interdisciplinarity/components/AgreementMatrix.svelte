<script>
	import { interpolateLab } from 'd3-interpolate'

	let {
		paper = {}
	} = $props()

	const { annotators = [], pairwise_matrix = [], paper_id, title, ratings = [] } = paper

	// Sort annotators by their ratings to cluster similar raters together
	const sortedIndices = $derived.by(() => {
		// Create array of [index, rating] pairs
		const indexed = ratings.map((rating, idx) => ({ idx, rating }))
		// Sort by rating (ascending)
		indexed.sort((a, b) => a.rating - b.rating)
		// Return just the indices
		return indexed.map(item => item.idx)
	})

	// Reorder annotators and matrix based on sorted indices
	const sortedAnnotators = $derived(sortedIndices.map(i => annotators[i]))
	const sortedRatings = $derived(sortedIndices.map(i => ratings[i]))
	const sortedMatrix = $derived(
		sortedIndices.map(i =>
			sortedIndices.map(j => pairwise_matrix[i][j])
		)
	)

	// Bivariate color scheme using D3 color interpolation
	// Map each rating to a color on the teal → neutral → magenta spectrum
	function ratingToColor(rating) {
		const colors = {
			1: '#0d9488', // Dark teal (very interdisciplinary)
			2: '#5eead4', // Light teal (somewhat interdisciplinary)
			3: '#e0e7ff', // Light purple/neutral (undecided)
			4: '#e879f9', // Light magenta (not really interdisciplinary)
			5: '#a21caf', // Dark magenta (not at all interdisciplinary)
		}
		return colors[rating] || '#e5e7eb'
	}

	// Blend two ratings using D3's perceptually uniform color interpolation
	function getCellColor(cell, rowRating, colRating) {
		const color1 = ratingToColor(rowRating)
		const color2 = ratingToColor(colRating)

		// Use D3's Lab color space interpolation for perceptually uniform blending
		const interpolate = interpolateLab(color1, color2)

		// Blend 50/50
		return interpolate(0.5)
	}

	// Get short annotator label
	function getAnnotatorLabel(annotator) {
		if (annotator.startsWith('user_')) {
			return annotator.replace('user_', 'U')
		} else if (annotator.startsWith('anon_')) {
			return annotator.replace('anon_', 'A')
		}
		return annotator
	}

	// Convert rating number to descriptive text
	function ratingToText(rating) {
		const labels = {
			1: 'Very interdisciplinary',
			2: 'Somewhat interdisciplinary',
			3: 'Undecided',
			4: 'Not really interdisciplinary',
			5: 'Not at all interdisciplinary'
		}
		return labels[rating] || rating
	}
</script>

<div class="matrix-container">
	<div class="header-row">
		<div class="paper-info">
			<h3>{title || 'Untitled'}</h3>
			<p class="paper-id-subtitle">{paper_id}</p>
		</div>

		<div class="legend">
			<p class="legend-title"></p>
			<div class="bivariate-grid-wrapper">
				<div class="vertical-axis-wrapper">
					<span class="axis-number vertical-number"></span>
					<span class="axis-label vertical-label">Not interdisciplinary</span>
				</div>
				<div class="bivariate-grid">
					<!-- Generate the full 5x5 grid dynamically using the blend function -->
					{#each [5, 4, 3, 2, 1] as rowRating}
						<div class="grid-row">
							{#each [1, 2, 3, 4, 5] as colRating}
								<div
									class="color-cell small"
									style="background-color: {getCellColor({}, rowRating, colRating)};"
									title="{rowRating}-{colRating}"
								></div>
							{/each}
						</div>
					{/each}
				</div>
				<div class="vertical-axis-wrapper">
					<span class="axis-label vertical-label bottom-label">Interdisciplinary</span>
				</div>
			</div>
			<p class="legend-note">Each cell blends two annotators' ratings (1=interdisciplinary, 5=not). Diagonal = both agree. Corners = strong consensus.</p>
		</div>
	</div>

	<div class="matrix-wrapper">
		<table class="agreement-matrix">
			<thead>
				<tr>
					<th class="corner-cell"></th>
					{#each sortedAnnotators as annotator, idx}
						{#if idx < sortedAnnotators.length}
							<th class="header-cell" title={annotator}>
								{getAnnotatorLabel(annotator)}
							</th>
						{/if}
					{/each}
				</tr>
			</thead>
			<tbody>
				{#each sortedMatrix as row, i}
					<tr>
						<th class="row-header" title={sortedAnnotators[i]}>
							{getAnnotatorLabel(sortedAnnotators[i])}
						</th>
						{#each row as cell, j}
							{#if j <= i}
								<td
									class="matrix-cell"
									class:diagonal={i === j}
									style="background-color: {i === j ? '#e5e7eb' : getCellColor(cell, sortedRatings[i], sortedRatings[j])};"
									title={`${sortedAnnotators[i]}: ${ratingToText(sortedRatings[i])}\n${sortedAnnotators[j]}: ${ratingToText(sortedRatings[j])}\nDifference: ${cell.diff}`}
								>
									{#if i === j}
										<span class="rating-label">{cell.rating}</span>
									{/if}
								</td>
							{:else}
								<td class="matrix-cell empty-cell"></td>
							{/if}
						{/each}
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>

<style>
	.matrix-container {
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		padding: 1.5rem;
		margin-bottom: 1rem;
	}

	.header-row {
		position: relative;
		margin-bottom: 1rem;
		min-height: 180px;
	}

	.paper-info {
		margin-right: 200px;
	}

	.paper-info h3 {
		margin: 0 0 0.25rem 0;
		font-size: 1rem;
		color: #1a1a1a;
		font-weight: 600;
	}

	.paper-id-subtitle {
		margin: 0;
		font-family: monospace;
		font-size: 0.75rem;
		color: #6b7280;
	}

	.matrix-wrapper {
		overflow-x: auto;
	}

	.legend {
		position: absolute;
		top: 0;
		right: 0;
		max-width: 190px;
	}

	@media (max-width: 640px) {
		.header-row {
			min-height: auto;
		}

		.paper-info {
			margin-right: 0;
			margin-bottom: 1rem;
		}

		.legend {
			position: static;
			max-width: 100%;
			margin: 0 auto;
		}
	}

	.legend-title {
		font-size: 0.75rem;
		font-weight: 600;
		color: #374151;
		margin: 0 0 0.5rem 0;
	}

	.bivariate-grid-wrapper {
		display: flex;
		align-items: stretch;
		gap: 0.35rem;
		margin-bottom: 0rem;
	}

	.vertical-axis-wrapper {
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		align-items: center;
	}

	.bivariate-grid {
		display: inline-block;
	}

	.grid-row {
		display: flex;
		align-items: center;
		gap: 1px;
		margin-bottom: 1px;
	}

	.color-cell.small {
		width: 24px;
		height: 24px;
		border: 1px solid #d1d5db;
		cursor: help;
	}

	.axis-label {
		font-size: 0.65rem;
		color: #6b7280;
		font-style: italic;
		font-weight: 500;
	}

	.vertical-label {
		writing-mode: vertical-rl;
		transform: rotate(180deg);
	}

	.bottom-label {
		margin-top: 0.25rem;
	}

	.legend-note {
		margin: 0.5rem 0 0 0;
		font-size: 0.65rem;
		color: #6b7280;
		font-style: italic;
		line-height: 1.3;
	}

	.agreement-matrix {
		border-collapse: collapse;
	}

	.corner-cell {
		background: #f9fafb;
		border: 1px solid #e5e7eb;
		width: 40px;
		height: 40px;
	}

	.header-cell {
		background: #f9fafb;
		border: 1px solid #e5e7eb;
		padding: 0.25rem;
		text-align: center;
		font-weight: 600;
		font-size: 0.7rem;
		color: #374151;
		width: 40px;
		height: 40px;
	}

	.row-header {
		background: #f9fafb;
		border: 1px solid #e5e7eb;
		padding: 0.25rem;
		text-align: center;
		font-weight: 600;
		font-size: 0.7rem;
		color: #374151;
		width: 40px;
		height: 40px;
	}

	.matrix-cell {
		border: 1px solid #e5e7eb;
		padding: 0.25rem;
		text-align: center;
		font-weight: 600;
		font-size: 0.75rem;
		cursor: pointer;
		transition: opacity 0.2s;
		width: 40px;
		height: 40px;
	}

	.matrix-cell:hover {
		opacity: 0.8;
	}

	.matrix-cell.diagonal {
		background: #e5e7eb !important;
	}

	.rating-label {
		color: #374151;
		font-weight: 600;
		font-size: 0.875rem;
	}

	.matrix-cell.empty-cell {
		background: transparent !important;
		border: none !important;
		cursor: default !important;
	}
</style>
