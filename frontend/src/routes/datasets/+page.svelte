<script>
	import { getDatasets } from './preview.remote.js';
	import Spinner from "$lib/components/helpers/Spinner.svelte"
</script>

<div class="datasets-container">
	<section class="datasets-header">
		<h1>Datasets</h1>
		<p class="datasets-description">
			Explore the datasets available through the Complex Stories platform. These datasets power our
			interactive stories and visualizations.
		</p>
	</section>

{#await getDatasets()}
	<Spinner text="loading datasets..." />
{:then result}
	<div class="datasets-section">
		<div class="datasets-grid">
		{#each result.datasets as dataset}
			<div class="dataset-card">
				<div class="card-header">
					<h3 class="dataset-name">
						{dataset.name.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
					</h3>
					<span class="status-badge available">available</span>
				</div>

				<p class="dataset-description">{dataset.description}</p>

				{#if dataset.keywords && dataset.keywords.length > 0}
					<div class="keywords">
						<div class="keyword-list">
							{#each dataset.keywords as keyword}
								<span class="keyword-tag">{keyword}</span>
							{/each}
						</div>
					</div>
				{/if}

				<div class="card-actions">
					{#if dataset.format && dataset.format.includes('Streaming')}
						<a href="/datasets/{dataset.name}" class="btn btn-primary">
							Preview
						</a>
						{#if dataset.auth_required}
							<span class="auth-badge">Auth Required</span>
						{/if}
					{:else}
						<a href="https://api.complexstories.uvm.edu/datasets/{dataset.name}?format=parquet" class="btn btn-primary" target="_blank" rel="noopener noreferrer">
							Download
						</a>
						<a href="/datasets/{dataset.name}" class="btn btn-secondary">
							Preview
						</a>
					{/if}
				</div>
			</div>
		{/each}
		</div>
	</div>
{:catch error}
	{console.log(error)}
	<p>Error: {error.message}</p>
{/await}

</div>

<style>
	/* Override main element constraints for full-width layout */
	:global(main#content:has(.datasets-container)) {
		max-width: none;
		padding: 0 !important;
	}

	.datasets-container {
		position: relative;
		min-height: 100vh;
	}

	.datasets-header {
		padding: 7.5rem var(--margin-left) 0.5rem var(--margin-left);
		text-align: left;
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

	.datasets-section {
		margin: 2rem 0;
		padding: 0 var(--margin-left);
	}

	/* Mobile responsive */
	@media (max-width: 768px) {
		.datasets-header {
			padding: 1.5rem var(--margin-left-mobile);
			text-align: left;
		}

		.datasets-section {
			padding: 0 var(--margin-left-mobile);
		}
	}

	.datasets-grid {
		display: grid;
		grid-template-columns: 1fr;
		gap: 3rem 1.5rem;
		margin: 0 auto;
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
		min-height: 280px;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
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

	.auth-badge {
		display: inline-flex;
		align-items: center;
		padding: 0.5rem 0.75rem;
		background-color: #fef3c7;
		color: #92400e;
		border-radius: 0.25rem;
		font-size: var(--font-size-xsmall);
		font-weight: var(--font-weight-medium);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		border: 1px solid #fbbf24;
		white-space: nowrap;
	}

	.dataset-description {
		color: var(--color-secondary-gray);
		font-size: var(--font-size-small);
		margin: 0 0 1.5rem 0;
		line-height: 1.5;
	}

	.keywords {
		margin-bottom: 1.5rem;
		flex-grow: 1;
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

	.card-actions {
		display: flex;
		gap: 0.5rem;
	}

	.btn {
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
		cursor: pointer;
		border: none;
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

	.preview-section {
		margin: 3rem 1rem 0;
		padding: 2rem;
		background: rgba(255, 255, 255, 0.8);
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 12px;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
	}

	.preview-section h2 {
		font-family: var(--sans);
		font-size: var(--font-size-large);
		font-weight: var(--font-weight-bold);
		color: var(--color-fg);
		margin: 0 0 1rem 0;
		text-transform: capitalize;
	}

	.preview-section > button {
		background: var(--color-bg);
		color: var(--color-fg);
		border: 1px solid var(--color-border);
		padding: 0.5rem 1rem;
		border-radius: var(--border-radius);
		font-size: var(--font-size-small);
		cursor: pointer;
		margin-bottom: 1.5rem;
		transition: all var(--transition-medium);
	}

	.preview-section > button:hover {
		background: var(--color-button-hover);
		color: var(--color-button-fg);
	}

	.preview-table {
		overflow: auto;
		border: 1px solid var(--color-border);
		border-radius: var(--border-radius);
		margin-top: 1rem;
	}

	.preview-table p {
		font-size: var(--font-size-small);
		color: var(--color-secondary-gray);
		margin: 0 0 1rem 0;
		font-weight: var(--font-weight-medium);
	}

	.preview-table table {
		width: 100%;
		border-collapse: collapse;
		font-size: var(--font-size-small);
	}

	.preview-table th,
	.preview-table td {
		padding: 0.75rem;
		text-align: left;
		border-bottom: 1px solid var(--color-border);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		max-width: 200px;
	}

	.preview-table th {
		background: var(--color-bg-alt);
		font-weight: var(--font-weight-semibold);
		color: var(--color-fg);
		position: sticky;
		top: 0;
	}

	.preview-table td {
		color: var(--color-secondary-gray);
	}

	.preview-table tbody tr:hover {
		background: var(--color-bg-alt);
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

	:global(.dark) .preview-section {
		background: rgba(30, 30, 30, 0.8);
		border-color: rgba(255, 255, 255, 0.1);
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
	}

	/* Mobile responsive */
	@media (max-width: 768px) {
		.datasets-grid {
			grid-template-columns: 1fr;
			padding: 0 0.5rem;
		}

		.preview-section {
			margin: 2rem 0.5rem 0;
			padding: 1rem;
		}
	}
</style>