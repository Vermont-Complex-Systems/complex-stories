
<script>
	import { quickUpdateAnnotation } from '$lib/api/annotations.remote';
	import { getCurrentUser } from '$lib/api/auth.remote';

	let { dataset } = $props();

	// Extract columns from the first row if data exists
	const columns = $derived(dataset && dataset.length > 0 ? Object.keys(dataset[0]).slice(1) : []);
	const rowCount = $derived(dataset ? dataset.length : 0);
	const displayData = $derived(dataset || []);

	// Define which fields are editable for annotations
	const editableFields = ['is_prof', 'perceived_as_male', 'has_research_group', 'group_size', 'group_url', 'notes', 'host_dept', 'oa_uid', 'oa_display_name', 'college', 'first_pub_year', 'inst_ipeds_id'];

	// Track editing state - simple approach
	let editingCell = $state(null);
	let editValue = $state('');

	function formatValue(value, column) {
		// Display boolean values as 1/0
		if (column === 'is_prof' || column === 'perceived_as_male' || column === 'has_research_group') {
			if (value === true) return '1';
			if (value === false) return '0';
			if (value === null || value === undefined) return '';
		}
		return value ?? '';
	}

	function cancelEdit() {
		editingCell = null;
		editValue = '';
	}

	async function saveEdit(row, column) {

		// Check if we have id for identification
		if (!row.id) {
			console.error('No id found for row:', row);
			cancelEdit();
			return;
		}

		let value = editValue;

		// Simple type conversion
		if (column === 'is_prof' || column === 'perceived_as_male' || column === 'has_research_group') {
			if (value === '1' || value === 'true') value = true;
			else if (value === '0' || value === 'false') value = false;
			else if (value === '') value = null;
		} else if (column === 'group_size' || column === 'first_pub_year') {
			value = value === '' ? null : parseInt(value) || null;
		}

		try {
			// Use id-based update (now unified API)
			await quickUpdateAnnotation({
				id: row.id,
				field: column,
				value: value
			});

			// Update local data
			row[column] = value;
			cancelEdit();
		} catch (error) {
			console.error('Failed to update:', error);
			cancelEdit();
		}
	}
</script>

<div class="file-meta">
	<div class="meta-info">
		<span class="meta-item">{displayData.length} rows</span>
		<span class="meta-separator">•</span>
		<span class="meta-item">{columns.length} columns</span>
	</div>
</div>

{#await getCurrentUser()}
	<!-- Loading user data -->
	{#if dataset && dataset.length > 0}
		<div class="file-viewer">
			<div class="table-wrapper">
				<table class="data-table">
					<thead>
						<tr>
							<th class="row-number-header">#</th>
							{#each columns as column}
								<th class="column-header">{column}</th>
							{/each}
						</tr>
					</thead>
					<tbody>
						{#each displayData as row, index}
							<tr class="data-row">
								<td class="row-number">{index + 1}</td>
								{#each columns as column}
									<td class="data-cell">
										<span>{formatValue(row[column], column)}</span>
									</td>
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
{:then currentUser}
	<!-- User data loaded, show editable table -->
	{@const isEditable = (column) => editableFields.includes(column)}
	{@const canEditRow = (row) => {
		if (!currentUser) return false;
		if (currentUser.role === 'admin') return true;
		if (currentUser.role === 'annotator') return true;
		if (currentUser.role === 'faculty') {
			return currentUser.payroll_name === row.payroll_name;
		}
		return false;
	}}
	{@const startEdit = (rowIndex, column, currentValue, row) => {
		if (!canEditRow(row)) {
			return;
		}
		editingCell = `${rowIndex}-${column}`;
		editValue = formatValue(currentValue, column);
	}}

	{#if dataset && dataset.length > 0}
		<div class="file-viewer">
			<div class="table-wrapper">
				<table class="data-table">
					<thead>
						<tr>
							<th class="row-number-header">#</th>
							{#each columns as column}
								<th class="column-header">{column}</th>
							{/each}
						</tr>
					</thead>
					<tbody>
						{#each displayData as row, index}
							<tr class="data-row">
								<td class="row-number">{index + 1}</td>
								{#each columns as column}
									<td class="data-cell" class:editable={isEditable(column) && canEditRow(row)}>
										{#if editingCell === `${index}-${column}`}
											<input
												bind:value={editValue}
												onblur={() => saveEdit(row, column)}
												onkeydown={(e) => {
													if (e.key === 'Enter') saveEdit(row, column);
													if (e.key === 'Escape') cancelEdit();
												}}
												autofocus
											/>
										{:else}
											<span
												onclick={() => isEditable(column) && canEditRow(row) && startEdit(index, column, row[column], row)}
												class:clickable={isEditable(column) && canEditRow(row)}
											>
												{formatValue(row[column], column)}
											</span>
										{/if}
									</td>
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
	<!-- Error loading user -->
	<div class="error">
		<h3>Error loading user data</h3>
		<p>{error.message}</p>
	</div>
{/await}

<style>
    .file-meta {
		border-bottom: 1px solid #d0d7de;
		background: #f6f8fa;
		padding: 0.5rem 0.5rem 0.5rem 1.5rem;
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

	.data-cell.editable {
		cursor: pointer;
	}

	.data-cell.editable:hover {
		background-color: #f6f8fa;
	}

	.clickable {
		display: block;
		width: 100%;
		height: 100%;
		padding: 4px;
		border-radius: 3px;
	}

	.clickable:hover {
		background-color: #e1f5fe;
	}

	.data-cell input {
		width: 100%;
		padding: 4px;
		border: 2px solid #0969da;
		border-radius: 3px;
		font-size: 12px;
		font-family: inherit;
		background: white;
		outline: none;
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

	:global(.dark) .meta-info {
		color: #7d8590;
	}

    /* Mobile responsive */
	@media (max-width: 768px) {
		.table-wrapper {
			max-height: 60vh;
		}

		.data-cell {
			max-width: 150px;
		}
	}

</style>