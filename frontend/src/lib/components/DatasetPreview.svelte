<script>
	import PreviewTable from "$lib/components/DatasetPreview.Table.svelte"
    import { page } from '$app/state';

	let { dataset, datasetName = 'academic-research-groups', filters = {} } = $props();

	// Extract unique filters from dataset for breadcrumb
	const breadcrumbFilters = $derived(() => {
		if (!dataset || dataset.length === 0) return {};

		const result = {};
		const firstRow = dataset[0];

		// Get unique inst_ipeds_id if all rows have the same value
		const instIds = [...new Set(dataset.map(row => row.inst_ipeds_id).filter(id => id))];
		if (instIds.length === 1) {
			result.inst_ipeds_id = instIds[0];
		}

		// Get unique payroll_year if all rows have the same value
		const years = [...new Set(dataset.map(row => row.payroll_year).filter(year => year))];
		if (years.length === 1) {
			result.payroll_year = years[0];
		}

		return result;
	});
</script>

<div class="dataset-preview-container">
	<section class="preview-header">
		<div class="preview-header-content">
			<nav class="breadcrumb">
				<a href="/datasets" class="breadcrumb-link">datasets</a>
				<span class="breadcrumb-separator">/</span>
				<span class="breadcrumb-item">{datasetName}</span>
				{#if breadcrumbFilters.inst_ipeds_id}
					<span class="breadcrumb-separator">/</span>
					<span class="breadcrumb-item">{breadcrumbFilters.inst_ipeds_id}</span>
				{/if}
				{#if breadcrumbFilters.payroll_year}
					<span class="breadcrumb-separator">/</span>
					<span class="breadcrumb-item">{breadcrumbFilters.payroll_year}</span>
				{/if}
			</nav>
			<div class="file-header">
				<div class="file-info">
					<div class="file-actions">
						<a href="https://api.complexstories.uvm.edu/datasets/{page.params.slug}?format=parquet" class="btn btn-download" target="_blank">
							<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
								<path d="M7.47 10.78a.75.75 0 001.06 0l3.75-3.75a.75.75 0 00-1.06-1.06L8.75 8.44V1.75a.75.75 0 00-1.5 0v6.69L4.78 5.97a.75.75 0 00-1.06 1.06l3.75 3.75zM3.75 13a.75.75 0 000 1.5h8.5a.75.75 0 000-1.5h-8.5z"/>
							</svg>
							Download
						</a>
						<button class="btn btn-secondary" onclick={() => window.print()}>
							<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
								<path d="M5 1a2 2 0 00-2 2v1h10V3a2 2 0 00-2-2H5zM4 7a1 1 0 011-1h6a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1V7zm8 0v3h1a1 1 0 001-1V7a1 1 0 00-1-1h-1z"/>
							</svg>
							Print
						</button>
					</div>
				</div>
			</div>
		</div>
	</section>

	<section class="file-content">
		<PreviewTable {dataset} />
	</section>
</div>

<style>
	/* Override main element constraints for full-width layout */
	:global(main:has(.dataset-preview-container)) {
		max-width: none;
		padding: 1.5rem 1.5rem 0.5rem 9.5rem;
	}

	
	/* Header */
	.preview-header {
		border-bottom: 1px solid #d0d7de;
		background: #f6f8fa;
		padding: 1.5rem;
	}

	.dataset-preview-container {
		position: relative;
		min-height: 100vh;
		background: #ffffff;
		padding: 1.5rem 9.5rem 0.5rem 9.5rem;
	}
	
	.breadcrumb {
		margin-bottom: 0.75rem;
		font-size: 14px;
	}

	.breadcrumb-link {
		color: #0969da;
		text-decoration: none;
		font-weight: 600;
	}

	.breadcrumb-link:hover {
		text-decoration: underline;
	}

	.breadcrumb-separator {
		margin: 0 0.5rem;
		color: #656d76;
	}

	.breadcrumb-item {
		color: #24292f;
		font-weight: 600;
	}

	.file-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
	}

	.file-actions {
		display: flex;
		gap: 0.5rem;
	}

	.btn {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.375rem 0.75rem;
		font-size: 12px;
		font-weight: 500;
		line-height: 1.45;
		border: 1px solid;
		border-radius: 6px;
		text-decoration: none;
		cursor: pointer;
		transition: all 0.2s;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
	}

	.btn-download {
		background: #1f883d;
		border-color: rgba(31, 136, 61, 0.4);
		color: #ffffff;
	}

	.btn-download:hover {
		background: #1a7f37;
		border-color: rgba(31, 136, 61, 0.4);
	}

	.btn-secondary {
		background: #f6f8fa;
		border-color: #d0d7de;
		color: #24292f;
	}

	.btn-secondary:hover {
		background: #f3f4f6;
		border-color: #d0d7de;
	}

	/* File content */
	.file-content {
		background: #ffffff;
	}

	
	/* Dark mode */
	:global(.dark) .dataset-preview-container {
		background: #0d1117;
	}

	:global(.dark) .preview-header {
		background: #161b22;
		border-color: #30363d;
	}

	
	/* Mobile responsive */
	@media (max-width: 768px) {
		.preview-header {
			padding: 1rem;
		}

		.file-header {
			flex-direction: column;
			align-items: flex-start;
			gap: 1rem;
		}

		.file-actions {
			width: 100%;
		}

		.btn {
			flex: 1;
			justify-content: center;
		}

	}
</style>