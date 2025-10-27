<script>
	import { getLabelStudioAgreement } from '$lib/api/label-studio.remote';
	import { Avatar } from "bits-ui";

	let projectId = $state(75);
	let forceRefresh = $state(false);

	function handleRefresh() {
		forceRefresh = true;
		// Reset after triggering refresh
		setTimeout(() => forceRefresh = false, 100);
	}

	// Function to get user initials from email/username
	function getUserInitials(identifier) {
		if (!identifier) return 'U';

		// Handle email addresses
		if (identifier.includes('@')) {
			const emailPart = identifier.split('@')[0];
			const parts = emailPart.split(/[._-]/);
			if (parts.length >= 2) {
				return (parts[0][0] + parts[1][0]).toUpperCase();
			}
			return emailPart.slice(0, 2).toUpperCase();
		}

		// Handle username format like "first_last"
		const parts = identifier.split('_');
		if (parts.length >= 2) {
			return (parts[0][0] + parts[1][0]).toUpperCase();
		}

		return identifier.slice(0, 2).toUpperCase();
	}

	function formatPercentage(value) {
		return `${(value * 100).toFixed(1)}%`;
	}

	function getAgreementColor(agreement) {
		if (agreement >= 0.8) return '#059669'; // Green
		if (agreement >= 0.6) return '#d97706'; // Orange
		return '#dc2626'; // Red
	}

	// Create agreement matrix for visualization
	function createAgreementMatrix(data) {
		if (!data?.agreement_analysis?.annotator_pairs) return null;

		const annotators = data.agreement_analysis.annotators || [];
		const pairs = data.agreement_analysis.annotator_pairs;

		// Create a matrix
		const matrix = [];
		for (let i = 0; i < annotators.length; i++) {
			matrix[i] = [];
			for (let j = 0; j < annotators.length; j++) {
				if (i === j) {
					matrix[i][j] = 1.0; // Perfect agreement with self
				} else {
					// Find agreement between annotators[i] and annotators[j]
					const pairKey1 = `${annotators[i]}_${annotators[j]}`;
					const pairKey2 = `${annotators[j]}_${annotators[i]}`;

					const agreement = pairs[pairKey1] || pairs[pairKey2] || 0;
					matrix[i][j] = agreement;
				}
			}
		}

		return { matrix, annotators };
	}
</script>

<svelte:head>
	<title>Label Studio Inter-Annotator Agreement Matrix</title>
</svelte:head>

<div class="container">
	<section class="header">
		<h1>Inter-Annotator Agreement Matrix</h1>
		<p>Visual analysis of agreement between annotators on Label Studio project {projectId}</p>

		<div class="controls">
			<label for="project-id">Project ID:</label>
			<input
				id="project-id"
				type="number"
				bind:value={projectId}
				min="1"
				class="project-input"
				onchange={() => forceRefresh = true}
			/>
			<button onclick={handleRefresh} class="btn">Refresh</button>
		</div>
	</section>

	{#await getLabelStudioAgreement({ projectId, forceRefresh })}
		<div class="loading">
			<p>Loading agreement data...</p>
		</div>
	{:then agreementData}
		{console.log('Full agreement data:', agreementData)}
		{#if agreementData?.agreement_analysis}
			{console.log('Agreement analysis:', agreementData.agreement_analysis)}
			{console.log('Field agreements:', agreementData.agreement_analysis.field_agreements)}
			{@const matrixData = createAgreementMatrix(agreementData)}
		<div class="results">
			<!-- Project Overview -->
			<div class="overview">
				<h2>Project Overview</h2>
				<div class="stats">
					<div class="stat">
						<span class="value">{agreementData.agreement_analysis.total_tasks || 0}</span>
						<span class="label">Total Tasks</span>
					</div>
					<div class="stat">
						<span class="value">{agreementData.agreement_analysis.multi_annotated_tasks || 0}</span>
						<span class="label">Multi-Annotated</span>
					</div>
					<div class="stat">
						<span class="value">{agreementData.agreement_analysis.unique_annotators || 0}</span>
						<span class="label">Annotators</span>
					</div>
					<div class="stat">
						<span class="value" style="color: {getAgreementColor(agreementData.agreement_analysis.overall_agreement || 0)}">
							{formatPercentage(agreementData.agreement_analysis.overall_agreement || 0)}
						</span>
						<span class="label">Overall Agreement</span>
					</div>
				</div>
			</div>

			<!-- Agreement Matrix -->
			{#if matrixData}
				<div class="matrix-section">
					<h2>Agreement Matrix</h2>
					<p>Each cell shows the agreement percentage between two annotators</p>

					<div class="matrix-container">
						<div class="matrix">
							<!-- Column headers -->
							<div class="matrix-header">
								<div class="corner-cell"></div>
								{#each matrixData.annotators as annotator}
									<div class="header-cell">
										<Avatar.Root class="avatar-small">
											<Avatar.Fallback class="avatar-fallback-small">
												{getUserInitials(annotator)}
											</Avatar.Fallback>
										</Avatar.Root>
									</div>
								{/each}
							</div>

							<!-- Matrix rows -->
							{#each matrixData.matrix as row, i}
								<div class="matrix-row">
									<div class="row-header">
										<Avatar.Root class="avatar-small">
											<Avatar.Fallback class="avatar-fallback-small">
												{getUserInitials(matrixData.annotators[i])}
											</Avatar.Fallback>
										</Avatar.Root>
										<span class="annotator-name">{matrixData.annotators[i]}</span>
									</div>
									{#each row as agreement, j}
										<div
											class="matrix-cell"
											style="background-color: {getAgreementColor(agreement)}; color: white;"
											title="Agreement between {matrixData.annotators[i]} and {matrixData.annotators[j]}: {formatPercentage(agreement)}"
										>
											{formatPercentage(agreement)}
										</div>
									{/each}
								</div>
							{/each}
						</div>
					</div>

					<!-- Legend -->
					<div class="legend">
						<h3>Agreement Scale</h3>
						<div class="legend-items">
							<div class="legend-item">
								<div class="color-box" style="background-color: #059669;"></div>
								<span>High (≥80%)</span>
							</div>
							<div class="legend-item">
								<div class="color-box" style="background-color: #d97706;"></div>
								<span>Medium (60-79%)</span>
							</div>
							<div class="legend-item">
								<div class="color-box" style="background-color: #dc2626;"></div>
								<span>Low (&lt;60%)</span>
							</div>
						</div>
					</div>
				</div>
			{/if}

			<!-- Field-level agreements -->
			{#if agreementData.agreement_analysis.field_agreements}
				<div class="field-agreements">
					<h2>Field-Level Agreement</h2>
					{#each Object.entries(agreementData.agreement_analysis.field_agreements) as [field, metrics]}
						<div class="field-card">
							<div class="field-header">
								<h3>{field}</h3>
								<span class="field-score" style="color: {getAgreementColor(metrics.mean_agreement)}">
									{formatPercentage(metrics.mean_agreement)}
								</span>
							</div>
							<div class="field-metrics">
								<span>Mean: {formatPercentage(metrics.mean_agreement)}</span>
								<span>Std: {formatPercentage(metrics.std_agreement)}</span>
								<span>Tasks: {metrics.num_tasks}</span>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
		{:else}
			<div class="no-data">
				<h3>No agreement data available</h3>
				<p>This may occur if there are no tasks with multiple annotations.</p>
			</div>
		{/if}
	{:catch error}
		<div class="error">
			<h3>Error Loading Data</h3>
			<p>{error.message}</p>
			<button onclick={handleRefresh} class="btn">Retry</button>
		</div>
	{/await}
</div>

<style>
	.container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
	}

	.header h1 {
		font-size: 2rem;
		margin-bottom: 0.5rem;
		color: var(--color-fg);
	}

	.header p {
		color: var(--color-secondary-gray);
		margin-bottom: 2rem;
	}

	.controls {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-bottom: 2rem;
		padding: 1rem;
		background: var(--color-bg-alt);
		border-radius: 0.5rem;
		border: 1px solid var(--color-border);
	}

	.controls label {
		font-weight: 500;
		color: var(--color-fg);
	}

	.project-input {
		padding: 0.5rem;
		border: 1px solid var(--color-border);
		border-radius: 0.25rem;
		width: 80px;
		background: var(--color-bg);
		color: var(--color-fg);
	}

	.btn {
		padding: 0.5rem 1rem;
		background: var(--color-button-bg);
		color: var(--color-button-fg);
		border: 1px solid var(--color-border);
		border-radius: 0.25rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	.btn:hover {
		background: var(--color-button-hover);
		transform: translateY(-1px);
	}

	.loading, .error, .no-data {
		text-align: center;
		padding: 2rem;
		color: var(--color-secondary-gray);
	}

	.error {
		color: var(--color-error, #dc2626);
	}

	.overview {
		background: var(--color-bg-alt);
		padding: 1.5rem;
		border-radius: 0.5rem;
		margin-bottom: 2rem;
		border: 1px solid var(--color-border);
	}

	.overview h2 {
		margin: 0 0 1rem 0;
		color: var(--color-fg);
	}

	.stats {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: 1rem;
	}

	.stat {
		text-align: center;
		padding: 1rem;
		background: var(--color-bg);
		border-radius: 0.25rem;
		border: 1px solid var(--color-border);
	}

	.stat .value {
		display: block;
		font-size: 1.5rem;
		font-weight: bold;
		color: var(--color-fg);
		margin-bottom: 0.25rem;
	}

	.stat .label {
		font-size: 0.875rem;
		color: var(--color-secondary-gray);
	}

	.matrix-section {
		background: var(--color-bg-alt);
		padding: 1.5rem;
		border-radius: 0.5rem;
		margin-bottom: 2rem;
		border: 1px solid var(--color-border);
	}

	.matrix-section h2 {
		margin: 0 0 0.5rem 0;
		color: var(--color-fg);
	}

	.matrix-section p {
		color: var(--color-secondary-gray);
		margin-bottom: 1.5rem;
	}

	.matrix-container {
		overflow-x: auto;
		margin-bottom: 1.5rem;
	}

	.matrix {
		display: inline-block;
		min-width: 100%;
	}

	.matrix-header {
		display: flex;
		margin-bottom: 2px;
	}

	.corner-cell {
		width: 180px;
		height: 60px;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-right: none;
	}

	.header-cell {
		width: 70px;
		height: 60px;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-right: none;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		font-weight: 500;
		font-size: 0.75rem;
		color: var(--color-fg);
		text-align: center;
		padding: 0.25rem;
		gap: 0.25rem;
		word-break: break-word;
	}

	.header-cell:last-child {
		border-right: 1px solid var(--color-border);
	}

	.matrix-row {
		display: flex;
		margin-bottom: 2px;
	}

	.row-header {
		width: 180px;
		height: 40px;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-right: none;
		display: flex;
		align-items: center;
		justify-content: flex-start;
		font-weight: 500;
		font-size: 0.75rem;
		color: var(--color-fg);
		padding: 0.5rem;
		gap: 0.5rem;
		word-break: break-word;
	}

	.matrix-cell {
		width: 70px;
		height: 40px;
		border: 1px solid var(--color-border);
		border-right: none;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 500;
		font-size: 0.75rem;
		cursor: pointer;
		transition: opacity 0.2s;
	}

	.matrix-cell:last-child {
		border-right: 1px solid var(--color-border);
	}

	.matrix-cell:hover {
		opacity: 0.8;
	}

	.legend {
		margin-top: 1rem;
	}

	.legend h3 {
		margin: 0 0 0.5rem 0;
		color: var(--color-fg);
		font-size: 1rem;
	}

	.legend-items {
		display: flex;
		gap: 1rem;
		flex-wrap: wrap;
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.875rem;
		color: var(--color-fg);
	}

	.color-box {
		width: 20px;
		height: 20px;
		border-radius: 0.25rem;
		border: 1px solid var(--color-border);
	}

	.field-agreements {
		background: var(--color-bg-alt);
		padding: 1.5rem;
		border-radius: 0.5rem;
		border: 1px solid var(--color-border);
	}

	.field-agreements h2 {
		margin: 0 0 1rem 0;
		color: var(--color-fg);
	}

	.field-card {
		background: var(--color-bg);
		padding: 1rem;
		border-radius: 0.25rem;
		margin-bottom: 1rem;
		border: 1px solid var(--color-border);
	}

	.field-card:last-child {
		margin-bottom: 0;
	}

	.field-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	.field-header h3 {
		margin: 0;
		color: var(--color-fg);
		font-size: 1rem;
	}

	.field-score {
		font-weight: bold;
		font-size: 1.125rem;
	}

	.field-metrics {
		display: flex;
		gap: 1rem;
		font-size: 0.875rem;
		color: var(--color-secondary-gray);
	}

	/* Avatar styles */
	:global(.avatar-small) {
		width: 28px;
		height: 28px;
	}

	:global(.avatar-fallback-small) {
		background: var(--color-button-bg);
		color: var(--color-button-fg);
		font-size: 0.75rem;
		font-weight: 600;
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
	}

	.annotator-name {
		max-width: 100%;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font-size: 0.7rem;
		line-height: 1.2;
	}

	/* Mobile responsive */
	@media (max-width: 768px) {
		.container {
			padding: 1rem;
		}

		.controls {
			flex-direction: column;
			align-items: stretch;
		}

		.stats {
			grid-template-columns: repeat(2, 1fr);
		}

		.legend-items {
			flex-direction: column;
		}

		.field-header {
			flex-direction: column;
			align-items: flex-start;
			gap: 0.5rem;
		}

		.field-metrics {
			flex-direction: column;
			gap: 0.25rem;
		}
	}
</style>