<script>
	import { previewDataset } from '../preview.remote.js';
	import { page } from '$app/stores';

	const slug = $page.params.slug;
</script>

<div class="dataset-preview-container">
	<!-- Header -->
	<section class="preview-header">
		<div class="preview-header-content">
			<nav class="breadcrumb">
				<a href="/datasets" class="breadcrumb-link">datasets</a>
				<span class="breadcrumb-separator">/</span>
				<span class="breadcrumb-current">{slug}.parquet</span>
			</nav>
			<div class="file-header">
				<div class="file-info">
					<h1 class="file-name">{slug}.parquet</h1>
					<div class="file-actions">
						<a href="http://127.0.0.1:8000/datasets/data/{slug}.parquet" class="btn btn-download" target="_blank">
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

	<!-- File Content -->
	<section class="file-content">
		{#await previewDataset({ datasetName: slug, limit: 999 })}
			<div class="loading-state">
				<div class="spinner"></div>
				<p>Loading preview...</p>
			</div>
		{:then previewData}
			<!-- File metadata bar -->
			<div class="file-meta">
				<div class="meta-info">
					<span class="meta-item">{previewData.total_rows_shown} rows displayed</span>
					<span class="meta-separator">•</span>
					<span class="meta-item">{previewData.columns.length} columns</span>
					<span class="meta-separator">•</span>
					<span class="meta-item">Showing first {previewData.preview_rows} rows</span>
				</div>
			</div>

			{#if previewData.data.length > 0}
				<div class="file-viewer">
					<div class="table-wrapper">
						<table class="data-table">
							<thead>
								<tr>
									<th class="row-number-header">#</th>
									{#each previewData.columns as column}
										<th class="column-header">{column}</th>
									{/each}
								</tr>
							</thead>
							<tbody>
								{#each previewData.data as row, index}
									<tr class="data-row">
										<td class="row-number">{index + 1}</td>
										{#each previewData.columns as column}
											<td class="data-cell">{row[column] ?? ''}</td>
										{/each}
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</div>
			{:else}
				<div class="empty-state">
					<p>No data to preview</p>
				</div>
			{/if}
		{:catch error}
			<div class="error-state">
				<p>Error: {error.message}</p>
				<p>Full error: {JSON.stringify(error)}</p>
			</div>
		{/await}
	</section>
</div>

<style>
	/* Override main element constraints for full-width layout */
	:global(main:has(.dataset-preview-container)) {
		max-width: none;
		padding: 0;
	}

	.dataset-preview-container {
		min-height: 100vh;
		background: #ffffff;
	}

	/* Header */
	.preview-header {
		border-bottom: 1px solid #d0d7de;
		background: #f6f8fa;
		padding: 1rem 2rem;
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

	.breadcrumb-current {
		color: #656d76;
		font-weight: 600;
	}

	.file-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
	}

	.file-name {
		font-size: 20px;
		font-weight: 600;
		color: #1f2328;
		margin: 0;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
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

	.file-meta {
		border-bottom: 1px solid #d0d7de;
		background: #f6f8fa;
		padding: 0.75rem 1rem;
	}

	.meta-info {
		font-size: 12px;
		color: #656d76;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
	}

	.meta-separator {
		margin: 0 0.5rem;
	}

	.file-viewer {
		overflow: auto;
		border: 1px solid #d0d7de;
		border-top: none;
	}

	.table-wrapper {
		overflow: auto;
		max-height: 80vh;
	}

	.data-table {
		width: 100%;
		border-collapse: collapse;
		font-size: 12px;
		font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace;
		background: #ffffff;
	}

	.row-number-header,
	.column-header {
		background: #f6f8fa;
		border-bottom: 1px solid #d0d7de;
		border-right: 1px solid #d0d7de;
		padding: 8px 16px;
		text-align: left;
		font-weight: 600;
		color: #24292f;
		position: sticky;
		top: 0;
		white-space: nowrap;
	}

	.row-number-header {
		width: 60px;
		text-align: center;
		background: #f6f8fa;
		border-right: 1px solid #d0d7de;
	}

	.data-row:hover {
		background: #f6f8fa;
	}

	.row-number {
		background: #f6f8fa;
		border-right: 1px solid #d0d7de;
		padding: 8px 16px;
		text-align: center;
		color: #656d76;
		font-weight: 500;
		font-size: 12px;
		white-space: nowrap;
		user-select: none;
	}

	.data-cell {
		padding: 8px 16px;
		border-bottom: 1px solid #d0d7de;
		color: #24292f;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		max-width: 300px;
	}

	.loading-state, .error-state, .empty-state {
		text-align: center;
		padding: 3rem 2rem;
		color: #656d76;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
	}

	.spinner {
		width: 2rem;
		height: 2rem;
		border: 2px solid #d0d7de;
		border-top: 2px solid #0969da;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin: 0 auto 1rem;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	/* Dark mode */
	:global(.dark) .dataset-preview-container {
		background: #0d1117;
	}

	:global(.dark) .preview-header {
		background: #161b22;
		border-color: #30363d;
	}

	:global(.dark) .file-meta {
		background: #161b22;
		border-color: #30363d;
	}

	:global(.dark) .file-viewer {
		border-color: #30363d;
	}

	:global(.dark) .data-table {
		background: #0d1117;
	}

	:global(.dark) .row-number-header,
	:global(.dark) .column-header {
		background: #161b22;
		border-color: #30363d;
		color: #f0f6fc;
	}

	:global(.dark) .row-number {
		background: #161b22;
		border-color: #30363d;
		color: #7d8590;
	}

	:global(.dark) .data-cell {
		border-color: #30363d;
		color: #f0f6fc;
	}

	:global(.dark) .data-row:hover {
		background: #161b22;
	}

	:global(.dark) .file-name {
		color: #f0f6fc;
	}

	:global(.dark) .breadcrumb-current {
		color: #7d8590;
	}

	:global(.dark) .meta-info {
		color: #7d8590;
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

		.table-wrapper {
			max-height: 60vh;
		}

		.data-cell {
			max-width: 150px;
		}
	}
</style>