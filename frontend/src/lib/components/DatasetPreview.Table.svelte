
<script>
	import { quickUpdateAnnotation, quickDeleteAnnotation } from '$lib/api/annotations.remote';
	import { getCurrentUser } from '$lib/api/auth.remote';
	import * as d3 from "d3";

	let { dataset, datasetName = 'academic-research-groups', filters: routeFilters = {} } = $props();
	
	// Define which fields are editable for annotations - all columns except id
	const editableFields = $derived(columns);

	// Track editing state - simple approach
	let editingCell = $state(null);
	let editValue = $state('');
	let showAutocomplete = $state(false);
	let autocompleteOptions = $state([]);
	let selectedOptionIndex = $state(-1);

	// Track save feedback
	let savedCell = $state(null);
	let saveMessage = $state('');

	// Track row deletion
	let selectedRowIndex = $state(null);
	let showDeleteConfirm = $state(false);

	// Track global search
	let globalSearch = $state('');

	// Get unique values for a column (for autocomplete)
	function getColumnValues(column) {
		if (!dataset) return [];
		const values = dataset
			.map(row => row[column])
			.filter(val => val != null && val !== '')
			.map(val => String(val));
		return [...new Set(values)].sort();
	}

	// Track sorting state
	let sortColumn = $state(null);
	let sortDirection = $state('asc'); // 'asc' or 'desc'


	// Extract columns from the first row if data exists
	const columns = $derived(dataset && dataset.length > 0 ? Object.keys(dataset[0]).slice(1) : []);
	const rowCount = $derived(dataset ? dataset.length : 0);
	const displayData = $derived.by(() => {
		if (!dataset) return [];

		// First apply global search across all columns
		let filteredData = dataset;
		if (globalSearch && globalSearch.trim() !== '') {
			const searchTerm = globalSearch.toLowerCase();
			filteredData = dataset.filter(row => {
				// Search across all column values in the row
				return Object.values(row).some(value => {
					const cellValue = String(value || '').toLowerCase();
					return cellValue.includes(searchTerm);
				});
			});
		}

		// Then apply sorting if specified
		if (sortColumn) {
			const sortFn = sortDirection === 'asc' ? d3.ascending : d3.descending;
			return d3.sort(filteredData, (a, b) => sortFn(a[sortColumn], b[sortColumn]));
		}

		return filteredData;
	});

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
		showAutocomplete = false;
		autocompleteOptions = [];
		selectedOptionIndex = -1;
	}

	function startEdit(rowIndex, column, currentValue, row) {
		if (!canEditRow(row)) return;

		editingCell = `${rowIndex}-${column}`;
		editValue = formatValue(currentValue, column);

		// Setup autocomplete
		const allValues = getColumnValues(column);
		autocompleteOptions = allValues;
		showAutocomplete = allValues.length > 1;
	}

	function filterAutocomplete(input, column) {
		if (!input) {
			autocompleteOptions = getColumnValues(column);
		} else {
			const filtered = getColumnValues(column).filter(value =>
				value.toLowerCase().includes(input.toLowerCase())
			);
			autocompleteOptions = filtered;
		}
		showAutocomplete = autocompleteOptions.length > 0;
		selectedOptionIndex = -1; // Reset selection when filtering
	}

	function selectAutocomplete(value) {
		editValue = value;
		showAutocomplete = false;
		selectedOptionIndex = -1;
	}

	function handleKeyboardNavigation(e, row, column) {
		switch (e.key) {
			case 'ArrowDown':
				if (showAutocomplete) {
					e.preventDefault();
					selectedOptionIndex = selectedOptionIndex < autocompleteOptions.length - 1
						? selectedOptionIndex + 1
						: selectedOptionIndex;
				}
				break;
			case 'ArrowUp':
				if (showAutocomplete) {
					e.preventDefault();
					selectedOptionIndex = selectedOptionIndex > 0
						? selectedOptionIndex - 1
						: -1;
				}
				break;
			case 'Enter':
				e.preventDefault();
				if (showAutocomplete && selectedOptionIndex >= 0 && selectedOptionIndex < autocompleteOptions.length) {
					selectAutocomplete(autocompleteOptions[selectedOptionIndex]);
				}
				saveEdit(row, column);
				break;
			case 'Escape':
				e.preventDefault();
				cancelEdit();
				break;
		}
	}

	function handleSort(column) {
		if (sortColumn === column) {
			sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
		} else {
			sortColumn = column;
			sortDirection = 'asc';
		}
	}

	function selectRowForDeletion(rowIndex, currentUser) {
		selectedRowIndex = rowIndex;
		showDeleteConfirm = true;
	}

	function cancelDelete() {
		selectedRowIndex = null;
		showDeleteConfirm = false;
	}

	async function confirmDelete() {
		if (selectedRowIndex === null) return;

		const row = displayData[selectedRowIndex];
		if (!row.id) {
			console.error('No id found for row:', row);
			cancelDelete();
			return;
		}

		try {
			// Use quick delete command - no token needed!
			await quickDeleteAnnotation({ id: row.id });

			// Remove from local dataset
			const index = dataset.findIndex(r => r.id === row.id);
			if (index !== -1) {
				dataset.splice(index, 1);
			}

			cancelDelete();
		} catch (error) {
			console.error('Failed to delete row:', error);
			cancelDelete();
		}
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
			// Use id-based update - no token needed!
			await quickUpdateAnnotation({
				id: row.id,
				field: column,
				value: value
			});

			// Update local data
			row[column] = value;

			// Show success feedback
			const cellId = `${displayData.indexOf(row)}-${column}`;
			savedCell = cellId;
			saveMessage = 'Saved ✓';

			// Clear feedback after 2 seconds
			setTimeout(() => {
				savedCell = null;
				saveMessage = '';
			}, 2000);

			cancelEdit();
		} catch (error) {
			console.error('Failed to update:', error);

			// Show error feedback
			const cellId = `${displayData.indexOf(row)}-${column}`;
			savedCell = cellId;
			saveMessage = 'Error ✗';

			// Clear feedback after 3 seconds
			setTimeout(() => {
				savedCell = null;
				saveMessage = '';
			}, 3000);

			cancelEdit();
		}
	}
</script>

<div class="file-meta">
	<div class="meta-info">
		<div class="meta-stats">
			<span class="meta-item">{displayData.length} rows</span>
			<span class="meta-separator">•</span>
			<span class="meta-item">{columns.length} columns</span>
		</div>
	</div>
</div>

{#if dataset && dataset.length > 0}
	<div class="search-panel">
		<div class="search-container">
			<input
				type="text"
				class="search-input"
				placeholder="Search this file..."
				bind:value={globalSearch}
			/>
			{#if globalSearch}
				<button class="clear-search-btn" onclick={() => globalSearch = ''}>
					✕
				</button>
			{/if}
		</div>
	</div>
{/if}

{#await getCurrentUser()}
	{#if dataset && dataset.length > 0}
		<div class="file-viewer">
			<div class="table-wrapper">
				<table class="data-table">
					<thead>
						<tr>
							<th class="row-number-header">#</th>
							{#each columns as column, index}
								<th class="column-header sortable" class:first-column-header={index === 0} onclick={() => handleSort(column)}>
									{column}
									{#if sortColumn === column}
										<span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
									{/if}
								</th>
							{/each}
						</tr>
					</thead>
					<tbody>
						{#each displayData as row, index}
							<tr class="data-row">
								<td class="row-number" class:selected={selectedRowIndex === index} onclick={() => selectRowForDeletion(index)}>
									{#if selectedRowIndex === index}
										<span class="delete-icon">🗑️</span>
									{:else}
										{index + 1}
									{/if}
								</td>
								{#each columns as column, index}
									<td class="data-cell" class:first-column-cell={index === 0}>
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
							{#each columns as column, index}
								<th class="column-header sortable" class:first-column-header={index === 0} onclick={() => handleSort(column)}>
									{column}
									{#if sortColumn === column}
										<span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
									{/if}
								</th>
							{/each}
						</tr>
					</thead>
					<tbody>
						{#each displayData as row, index}
							<tr class="data-row">
								<td class="row-number" class:selected={selectedRowIndex === index} class:editable={canEditRow(row)} onclick={() => canEditRow(row) && selectRowForDeletion(index, currentUser)}>
									{#if selectedRowIndex === index}
										<span class="delete-icon">🗑️</span>
									{:else}
										{index + 1}
									{/if}
								</td>
								{#each columns as column, colIndex}
									<td class="data-cell" class:editable={isEditable(column) && canEditRow(row)} class:first-column-cell={colIndex === 0}>
										{#if editingCell === `${index}-${column}`}
											<div class="input-container">
												<input
													bind:value={editValue}
													oninput={(e) => filterAutocomplete(e.target.value, column)}
													onblur={() => {
														// Delay to allow autocomplete click
														setTimeout(() => saveEdit(row, column), 100);
													}}
													onkeydown={(e) => handleKeyboardNavigation(e, row, column)}
													autofocus
												/>
												{#if showAutocomplete && autocompleteOptions.length > 0}
													<div class="autocomplete-dropdown">
														{#each autocompleteOptions.slice(0, 10) as option, index}
															<div
																class="autocomplete-option"
																class:selected={index === selectedOptionIndex}
																onclick={() => selectAutocomplete(option)}
															>
																{option}
															</div>
														{/each}
													</div>
												{/if}
											</div>
										{:else}
											<div class="cell-content">
												<span
													onclick={() => isEditable(column) && canEditRow(row) && startEdit(index, column, row[column], row)}
													class:clickable={isEditable(column) && canEditRow(row)}
												>
													{formatValue(row[column], column)}
												</span>
												{#if savedCell === `${index}-${column}`}
													<span class="save-feedback" class:success={saveMessage.includes('✓')} class:error={saveMessage.includes('✗')}>
														{saveMessage}
													</span>
												{/if}
											</div>
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

<!-- Delete confirmation modal -->
{#if showDeleteConfirm && selectedRowIndex !== null}
	<div class="modal-overlay" onclick={cancelDelete}>
		<div class="modal-content" onclick={(e) => e.stopPropagation()}>
			<h3>Delete Row</h3>
			<p>Are you sure you want to delete this row? This action cannot be undone.</p>
			<div class="modal-actions">
				<button class="cancel-btn" onclick={cancelDelete}>Cancel</button>
				<button class="delete-btn" onclick={confirmDelete}>Delete</button>
			</div>
		</div>
	</div>
{/if}

<style>
    .file-meta {
		border-bottom: 1px solid #d0d7de;
		background: #f6f8fa;
		padding: .5rem 0.5rem 0.5rem 1.5rem;
	}

	.meta-info {
		font-size: 12px;
		color: #656d76;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
	}

	.meta-stats {
		display: flex;
		align-items: center;
	}

	.meta-separator {
		margin: 0 0.5rem;
	}

	.search-panel {
		background: #f6f8fa;
		border-bottom: 1px solid #d0d7de;
		padding: 12px 12px;
	}

	.search-container {
		position: relative;
	}

	.search-input {
		width: 100%;
		padding: 8px 12px;
		padding-right: 32px;
		border: 1px solid #d0d7de;
		border-radius: 6px;
		font-size: 14px;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
		background: white;
		color: #24292f;
		box-sizing: border-box;
	}

	.search-input:focus {
		outline: none;
		border-color: #0969da;
		box-shadow: 0 0 0 3px rgba(9, 105, 218, 0.1);
	}

	.clear-search-btn {
		position: absolute;
		right: 8px;
		top: 50%;
		transform: translateY(-50%);
		background: transparent;
		border: none;
		color: #656d76;
		cursor: pointer;
		font-size: 12px;
		padding: 4px;
		border-radius: 3px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.clear-search-btn:hover {
		background: #f6f8fa;
		color: #24292f;
	}

	.file-viewer {
		overflow: auto;
		border: 1px solid #d0d7de;
		border-top: none;
	}

	.table-wrapper {
		overflow: auto;
		max-height: 80vh;
		position: relative;
	}

	.data-table {
		width: 100%;
		border-collapse: collapse;
		font-size: 12px;
		font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace;
		background: #ffffff;
		table-layout: auto;
		margin: 0;
		border-spacing: 0;
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
		z-index: 10;
	}

	.column-header.sortable {
		cursor: pointer;
		user-select: none;
	}

	.column-header.sortable:hover {
		background: #eaeef2;
	}

	.sort-indicator {
		margin-left: 4px;
		font-size: 10px;
		opacity: 0.7;
	}

	.row-number-header {
		width: 60px;
		text-align: center;
		background: #f6f8fa;
		border-right: 1px solid #d0d7de;
		position: sticky;
		left: 0;
		z-index: 12;
	}

	.first-column-header {
		position: sticky;
		left: 0;
		background: #f6f8fa;
		z-index: 12;
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
		position: sticky;
		left: 0;
		z-index: 5;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	.row-number:hover {
		background: #eaeef2;
	}

	.row-number.selected {
		background: #ffebe9;
		border-color: #f85149;
	}

	.delete-icon {
		font-size: 14px;
		color: #d1242f;
	}

	.data-cell {
		padding: 4px 16px;
		border-bottom: 1px solid #d0d7de;
		color: #24292f;
		white-space: nowrap;
		overflow: visible;
		position: relative;
		vertical-align: top;
	}

	.first-column-cell {
		position: sticky;
		left: 0;
		background: #f6f8fa;
		z-index: 5;
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

	.cell-content {
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
	}

	.save-feedback {
		font-size: 11px;
		font-weight: 500;
		padding: 2px 6px;
		border-radius: 3px;
		margin-left: 8px;
		opacity: 0;
		animation: fadeInOut 2s ease-in-out;
	}

	.save-feedback.success {
		background: #d4edda;
		color: #155724;
		border: 1px solid #c3e6cb;
	}

	.save-feedback.error {
		background: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
	}

	@keyframes fadeInOut {
		0% { opacity: 0; transform: translateY(-2px); }
		20% { opacity: 1; transform: translateY(0); }
		80% { opacity: 1; transform: translateY(0); }
		100% { opacity: 0; transform: translateY(-2px); }
	}

	.input-container {
		position: relative;
		width: 100%;
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

	.autocomplete-dropdown {
		position: absolute;
		top: 100%;
		left: 0;
		right: 0;
		background: white;
		border: 1px solid #d0d7de;
		border-radius: 3px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		max-height: 240px;
		overflow-y: auto;
		z-index: 9999;
	}

	.autocomplete-option {
		padding: 8px 12px;
		cursor: pointer;
		font-size: 12px;
		border-bottom: 1px solid #f6f8fa;
	}

	.autocomplete-option:hover,
	.autocomplete-option.selected {
		background: #f6f8fa;
	}

	.autocomplete-option:last-child {
		border-bottom: none;
	}

	/* Modal styles */
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 10000;
	}

	.modal-content {
		background: white;
		padding: 24px;
		border-radius: 8px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
		max-width: 400px;
		width: 90%;
	}

	.modal-content h3 {
		margin: 0 0 12px 0;
		color: #24292f;
		font-size: 16px;
		font-weight: 600;
	}

	.modal-content p {
		margin: 0 0 20px 0;
		color: #656d76;
		font-size: 14px;
		line-height: 1.5;
	}

	.modal-actions {
		display: flex;
		gap: 12px;
		justify-content: flex-end;
	}

	.cancel-btn, .delete-btn {
		padding: 8px 16px;
		border: 1px solid;
		border-radius: 6px;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
	}

	.cancel-btn {
		background: white;
		border-color: #d0d7de;
		color: #24292f;
	}

	.cancel-btn:hover {
		background: #f6f8fa;
	}

	.delete-btn {
		background: #d1242f;
		border-color: #d1242f;
		color: white;
	}

	.delete-btn:hover {
		background: #b91c1c;
		border-color: #b91c1c;
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

	:global(.dark) .row-number-header {
		background: #161b22;
	}

	:global(.dark) .first-column-header {
		background: #161b22;
	}

	:global(.dark) .first-column-cell {
		background: #0d1117;
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

	:global(.dark) .autocomplete-dropdown {
		background: #161b22;
		border-color: #30363d;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
	}

	:global(.dark) .autocomplete-option {
		border-color: #30363d;
		color: #f0f6fc;
	}

	:global(.dark) .autocomplete-option:hover,
	:global(.dark) .autocomplete-option.selected {
		background: #21262d;
	}

	:global(.dark) .row-number:hover {
		background: #21262d;
	}

	:global(.dark) .row-number.selected {
		background: #2d1b1e;
		border-color: #f85149;
	}

	:global(.dark) .modal-content {
		background: #161b22;
		color: #f0f6fc;
	}

	:global(.dark) .modal-content h3 {
		color: #f0f6fc;
	}

	:global(.dark) .modal-content p {
		color: #7d8590;
	}

	:global(.dark) .cancel-btn {
		background: #21262d;
		border-color: #30363d;
		color: #f0f6fc;
	}

	:global(.dark) .cancel-btn:hover {
		background: #30363d;
	}

	:global(.dark) .search-panel {
		background: #161b22;
		border-color: #30363d;
	}

	:global(.dark) .search-input {
		background: #0d1117;
		border-color: #30363d;
		color: #f0f6fc;
	}

	:global(.dark) .search-input:focus {
		border-color: #58a6ff;
		box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
	}

	:global(.dark) .clear-search-btn {
		color: #7d8590;
	}

	:global(.dark) .clear-search-btn:hover {
		background: #21262d;
		color: #f0f6fc;
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