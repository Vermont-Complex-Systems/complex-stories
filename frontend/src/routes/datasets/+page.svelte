<script lang="ts">
	import type { PageData } from './$types';

	export let data: PageData;

	const formatFileSize = (bytes: number): string => {
		if (!bytes) return 'Unknown';
		const sizes = ['B', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(1024));
		return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
	};

	const getStatusColor = (status: string): string => {
		switch (status) {
			case 'available': return 'bg-green-100 text-green-800';
			case 'error': return 'bg-red-100 text-red-800';
			default: return 'bg-gray-100 text-gray-800';
		}
	};
</script>

<svelte:head>
	<title>Datasets - Complex Stories</title>
	<meta name="description" content="Available datasets for Complex Stories platform" />
</svelte:head>

<div class="datasets-container">
	<div class="datasets-header">
		<div class="datasets-header-content">
			<h1>Datasets</h1>
			<p class="datasets-description">
				Explore the datasets available through the Complex Stories platform. These datasets power our
				interactive stories and visualizations.
			</p>

			<!-- API Status -->
			<div class="api-status">
				<div class="status-indicator {data.apiConnected ? 'connected' : 'disconnected'}"></div>
				<span class="status-text">
					API Status: {data.apiConnected ? 'Connected' : 'Disconnected'}
				</span>
				{#if !data.apiConnected}
					<span class="fallback-note">(Using fallback data)</span>
				{/if}
			</div>
		</div>
	</div>

	{#if data.error}
		<div class="error-banner">
			<h3>Connection Error</h3>
			<p>{data.error}</p>
		</div>
	{/if}

	{#if data.datasets.length === 0}
		<div class="empty-state">
			<div class="empty-icon">📊</div>
			<h3>No datasets available</h3>
			<p>Datasets will appear here once the API is connected.</p>
		</div>
	{:else}
		<div class="datasets-grid">
			{#each data.datasets as dataset}
				<div class="dataset-card">
					<!-- Header -->
					<div class="card-header">
						<h3 class="dataset-name">
							{dataset.name.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
						</h3>
						<span class="status-badge {dataset.status}">{dataset.status}</span>
					</div>

					<!-- Description -->
					<p class="dataset-description">{dataset.description}</p>

					<!-- Stats -->
					{#if dataset.stats && !dataset.stats.error}
						<div class="dataset-stats">
							<div class="stat-item">
								<dt>Rows</dt>
								<dd>{dataset.stats.row_count?.toLocaleString() || 'N/A'}</dd>
							</div>
							<div class="stat-item">
								<dt>Columns</dt>
								<dd>{dataset.stats.column_count || 'N/A'}</dd>
							</div>
							<div class="stat-item full-width">
								<dt>File Size</dt>
								<dd>{formatFileSize(dataset.stats.file_size_bytes)}</dd>
							</div>

							<!-- Keywords -->
							{#if dataset.keywords && dataset.keywords.length > 0}
								<div class="keywords">
									<dt>Keywords</dt>
									<div class="keyword-list">
										{#each dataset.keywords as keyword}
											<span class="keyword-tag">{keyword}</span>
										{/each}
									</div>
								</div>
							{/if}
						</div>
					{:else if dataset.stats?.error}
						<div class="error-box">
							<p>Error: {dataset.stats.error}</p>
						</div>
					{/if}

					<!-- Actions -->
					<div class="card-actions">
						<a href={dataset.url} class="btn btn-primary" target="_blank" rel="noopener noreferrer">
							Download
						</a>
						{#if data.apiConnected}
							<a href="/datasets/{dataset.name}/preview" class="btn btn-secondary">
								Preview
							</a>
						{/if}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	/* Override main element constraints for full-width layout */
	:global(main:has(.datasets-container)) {
		max-width: none;
		padding: 0;
	}

	.datasets-container {
		position: relative;
		min-height: 100vh;
	}

	.datasets-header {
		padding: 1.5rem 1.5rem 0.5rem 9.5rem;
		text-align: left;
	}

	.datasets-header-content {
		padding-top: 1rem;
	}

	.datasets-header h1 {
		font-family: var(--mono);
		font-size: clamp(1.5rem, 3vw, 2rem);
		font-weight: var(--font-weight-bold);
		color: var(--color-fg);
		margin: 0 0 1rem 0;
	}

	.datasets-description {
		font-family: var(--mono);
		font-size: var(--font-size-medium);
		color: var(--color-secondary-gray);
		margin-bottom: 1.5rem;
		line-height: 1.6;
	}

	.api-status {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 1.5rem;
	}

	.status-indicator {
		width: 0.75rem;
		height: 0.75rem;
		border-radius: 50%;
	}

	.status-indicator.connected {
		background-color: #10b981;
	}

	.status-indicator.disconnected {
		background-color: #ef4444;
	}

	.status-text {
		font-size: var(--font-size-small);
		color: var(--color-secondary-gray);
	}

	.fallback-note {
		font-size: var(--font-size-small);
		color: var(--color-tertiary-gray);
	}

	.error-banner {
		background-color: #fef2f2;
		border: 1px solid #fecaca;
		border-radius: var(--border-radius);
		padding: 1rem;
		margin-bottom: 1.5rem;
	}

	.error-banner h3 {
		color: #991b1b;
		font-weight: var(--font-weight-medium);
		margin: 0 0 0.25rem 0;
	}

	.error-banner p {
		color: #dc2626;
		font-size: var(--font-size-small);
		margin: 0;
	}

	.empty-state {
		text-align: center;
		padding: 3rem 0;
	}

	.empty-icon {
		font-size: 4rem;
		margin-bottom: 1rem;
	}

	.empty-state h3 {
		font-size: var(--font-size-large);
		font-weight: var(--font-weight-medium);
		color: var(--color-fg);
		margin: 0 0 0.5rem 0;
	}

	.empty-state p {
		color: var(--color-secondary-gray);
		margin: 0;
	}

	.datasets-grid {
		display: grid;
		grid-template-columns: 1fr;
		gap: 3rem 1.5rem;
		margin: 2rem 0;
		padding: 0 9.5rem;
	}

	@media (min-width: 768px) {
		.datasets-grid {
			grid-template-columns: repeat(2, 1fr);
			gap: 3.5rem 2rem;
		}
	}

	@media (min-width: 1200px) {
		.datasets-grid {
			grid-template-columns: repeat(3, 1fr);
			gap: 4rem 2.5rem;
			max-width: 1600px !important;
		}
	}

	.dataset-card {
		background: rgba(255, 255, 255, 0.8);
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 12px;
		overflow: hidden;
		transition: all var(--transition-medium);
		min-height: 250px;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
		padding: 1.5rem;
	}

	.dataset-card:hover {
		transform: translateY(-4px);
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
		background: rgba(255, 255, 255, 0.9);
	}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 1rem;
		gap: 1rem;
	}

	.dataset-name {
		font-family: var(--sans);
		font-size: var(--font-size-medium);
		font-weight: var(--font-weight-bold);
		color: var(--color-fg);
		margin: 0;
		flex: 1;
		line-height: 1.2;
	}

	.status-badge {
		display: inline-flex;
		align-items: center;
		padding: 0.25rem 0.75rem;
		border-radius: 1rem;
		font-size: var(--font-size-xsmall);
		font-weight: var(--font-weight-medium);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		flex-shrink: 0;
	}

	.status-badge.available {
		background-color: #d1fae5;
		color: #065f46;
	}

	.status-badge.error {
		background-color: #fee2e2;
		color: #991b1b;
	}

	.dataset-description {
		color: var(--color-secondary-gray);
		font-size: var(--font-size-small);
		margin: 0 0 1.5rem 0;
		line-height: 1.5;
	}

	.dataset-stats {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
		margin-bottom: 1.5rem;
	}

	.stat-item {
		display: flex;
		flex-direction: column;
	}

	.stat-item.full-width {
		grid-column: 1 / -1;
	}

	.stat-item dt {
		font-size: var(--font-size-xsmall);
		font-weight: var(--font-weight-medium);
		color: var(--color-tertiary-gray);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: 0.25rem;
	}

	.stat-item dd {
		font-size: var(--font-size-medium);
		font-weight: var(--font-weight-semibold);
		color: var(--color-fg);
		margin: 0;
	}

	.keywords {
		grid-column: 1 / -1;
		margin-top: 0.5rem;
	}

	.keywords dt {
		font-size: var(--font-size-xsmall);
		font-weight: var(--font-weight-medium);
		color: var(--color-tertiary-gray);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: 0.5rem;
	}

	.keyword-list {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.keyword-tag {
		display: inline-flex;
		align-items: center;
		padding: 0.25rem 0.5rem;
		background-color: #dbeafe;
		color: #1d4ed8;
		border-radius: 0.25rem;
		font-size: var(--font-size-xsmall);
		font-weight: var(--font-weight-medium);
	}

	.error-box {
		background-color: #fef2f2;
		border: 1px solid #fecaca;
		border-radius: var(--border-radius);
		padding: 0.75rem;
		margin-bottom: 1.5rem;
	}

	.error-box p {
		color: #dc2626;
		font-size: var(--font-size-xsmall);
		margin: 0;
	}

	.card-actions {
		display: flex;
		gap: 0.5rem;
	}

	.btn {
		/* Reset button defaults first */
		border: none;
		background: none;
		padding: 0;
		cursor: pointer;
		font-family: inherit;

		/* Apply our styling */
		flex: 1;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 0.75rem 1rem;
		border-radius: var(--border-radius);
		font-family: var(--font-form);
		font-size: var(--font-size-small);
		font-weight: var(--font-weight-medium);
		text-decoration: none;
		text-align: center;
		transition: all var(--transition-medium);
		white-space: nowrap;
		min-width: fit-content;
	}

	.btn-primary {
		background: var(--color-button-bg);
		color: var(--color-button-fg);
		border: 1px solid var(--color-border);
	}

	.btn-primary:hover {
		background: var(--color-button-hover);
		transform: translateY(-1px);
	}

	.btn-secondary {
		background: var(--color-bg);
		color: var(--color-fg);
		border: 1px solid var(--color-border);
	}

	.btn-secondary:hover {
		background: var(--color-button-hover);
		color: var(--color-button-fg);
		transform: translateY(-1px);
	}

	/* Mobile responsive */
	@media (max-width: 768px) {
		.datasets-header {
			padding: 1rem var(--margin-left-mobile);
			text-align: left;
		}

		.datasets-grid {
			grid-template-columns: 1fr;
			padding: 0 var(--margin-left-mobile);
		}

		.card-header {
			flex-direction: column;
			align-items: flex-start;
			gap: 0.5rem;
		}
	}

	/* Dark mode */
	:global(.dark) .dataset-card {
		background: rgba(30, 30, 30, 0.8);
		border-color: rgba(255, 255, 255, 0.1);
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
	}

	:global(.dark) .dataset-card:hover {
		background: rgba(40, 40, 40, 0.9);
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
	}

	:global(.dark) .btn-secondary {
		background-color: rgba(255, 255, 255, 0.1);
		color: var(--color-fg);
		border-color: var(--color-border);
	}

	:global(.dark) .btn-secondary:hover {
		background-color: rgba(255, 255, 255, 0.2);
	}
</style>