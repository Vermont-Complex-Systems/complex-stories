<script>
	import { getCurrentUser } from '$lib/api/auth.remote';
	import * as d3 from "d3";

	let {
		data = [],
		onUpdate = null,
		onDelete = null,
		editableColumns = [],
		excludeColumns = ['id'],
		allowDelete = true,
		searchable = true,
		sortable = true,
		showRowNumbers = true,
		showStats = true,
		customFormatters = {},
		customPermissions = null,
		columnTypes = {}
	} = $props();

	// Track editing state
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

	// Track sorting state
	let sortColumn = $state(null);
	let sortDirection = $state('asc');

	// Extract columns from the first row if data exists
	const columns = $derived.by(() => {
		if (!data || data.length === 0) return [];
		const allColumns = Object.keys(data[0]);
		return allColumns.filter(col => !excludeColumns.includes(col));
	});

	const rowCount = $derived(data ? data.length : 0);

	const displayData = $derived.by(() => {
		if (!data) return [];

		// Apply global search across all columns
		let filteredData = data;
		if (searchable && globalSearch && globalSearch.trim() !== '') {
			const searchTerm = globalSearch.toLowerCase();
			filteredData = data.filter(row => {
				return Object.values(row).some(value => {
					const cellValue = String(value || '').toLowerCase();
					return cellValue.includes(searchTerm);
				});
			});
		}

		// Apply sorting if specified
		if (sortable && sortColumn) {
			const sortFn = sortDirection === 'asc' ? d3.ascending : d3.descending;
			return d3.sort(filteredData, (a, b) => sortFn(a[sortColumn], b[sortColumn]));
		}

		return filteredData;
	});

	// Get unique values for a column (for autocomplete)
	function getColumnValues(column) {
		if (!data) return [];
		const values = data
			.map(row => row[column])
			.filter(val => val != null && val !== '')
			.map(val => String(val));
		return [...new Set(values)].sort();
	}

	// Format cell values - use custom formatters if provided
	function formatValue(value, column) {
		if (customFormatters && customFormatters[column]) {
			return customFormatters[column](value);
		}

		// Default formatting for academic data
		if (typeof value === 'boolean') {
			return value ? '1' : '0';
		}
		if (value === null || value === undefined) {
			return '';
		}
		return String(value);
	}

	// Default permissions - academic research groups pattern
	function defaultCanEdit(row, column, user) {
		if (!user) return false;
		if (!editableColumns.includes(column)) return false;
		if (user.role === 'admin') return true;
		if (user.role === 'annotator') return true;
		if (user.role === 'faculty') {
			return user.payroll_name === row.payroll_name;
		}
		return false;
	}

	function defaultCanDelete(row, user) {
		if (!user || !allowDelete) return false;
		if (user.role === 'admin') return true;
		if (user.role === 'annotator') return true;
		return false;
	}

	function canEditCell(row, column, user) {
		if (customPermissions?.canEdit) {
			return customPermissions.canEdit(row, column, user);
		}
		return defaultCanEdit(row, column, user);
	}

	function canDeleteRow(row, user) {
		if (customPermissions?.canDelete) {
			return customPermissions.canDelete(row, user);
		}
		return defaultCanDelete(row, user);
	}

	// Validate and convert values based on column type
	function validateValue(value, column) {
		const type = columnTypes[column] || 'text';

		switch (type) {
			case 'binary':
				if (value === '1' || value === 'true' || value === true) return true;
				if (value === '0' || value === 'false' || value === false) return false;
				if (value === '' || value === null || value === undefined) return null;
				throw new Error(`Invalid binary value: ${value}`);

			case 'integer':
				if (value === '' || value === null || value === undefined) return null;
				const parsed = parseInt(value);
				if (isNaN(parsed)) throw new Error(`Invalid integer: ${value}`);
				return parsed;

			case 'float':
				if (value === '' || value === null || value === undefined) return null;
				const parsedFloat = parseFloat(value);
				if (isNaN(parsedFloat)) throw new Error(`Invalid number: ${value}`);
				return parsedFloat;

			case 'ordinal':
				// For ordinal data, could validate against allowed values
				// For now, treat as text but could be enhanced
				return value === '' ? null : String(value);

			case 'text':
			default:
				return value === '' ? null : String(value);
		}
	}

	function cancelEdit() {
		editingCell = null;
		editValue = '';
		showAutocomplete = false;
		autocompleteOptions = [];
		selectedOptionIndex = -1;
	}

	function startEdit(rowIndex, column, currentValue, row, user) {
		if (!canEditCell(row, column, user)) return;

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
		selectedOptionIndex = -1;
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
		if (!sortable) return;

		if (sortColumn === column) {
			sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
		} else {
			sortColumn = column;
			sortDirection = 'asc';
		}
	}

	function selectRowForDeletion(rowIndex) {
		selectedRowIndex = rowIndex;
		showDeleteConfirm = true;
	}

	function cancelDelete() {
		selectedRowIndex = null;
		showDeleteConfirm = false;
	}

	async function confirmDelete() {
		if (selectedRowIndex === null || !onDelete) return;

		const row = displayData[selectedRowIndex];
		const id = row.id || row._id; // Support both id and _id

		if (!id) {
			console.error('No id found for row:', row);
			cancelDelete();
			return;
		}

		try {
			await onDelete(id);

			// Remove from local data
			const index = data.findIndex(r => (r.id || r._id) === id);
			if (index !== -1) {
				data.splice(index, 1);
			}

			cancelDelete();
		} catch (error) {
			console.error('Failed to delete row:', error);
			// Show error feedback
			saveMessage = 'Delete failed ✗';
			setTimeout(() => {
				saveMessage = '';
			}, 3000);
			cancelDelete();
		}
	}

	async function saveEdit(row, column) {
		if (!onUpdate) {
			console.error('No onUpdate callback provided');
			cancelEdit();
			return;
		}

		const id = row.id || row._id; // Support both id and _id
		if (!id) {
			console.error('No id found for row:', row);
			cancelEdit();
			return;
		}

		let value = editValue;

		// Apply type-based validation
		try {
			value = validateValue(value, column);
		} catch (error) {
			console.error('Validation failed:', error);
			// Show validation error
			const cellId = `${displayData.indexOf(row)}-${column}`;
			savedCell = cellId;
			saveMessage = 'Invalid ✗';
			setTimeout(() => {
				savedCell = null;
				saveMessage = '';
			}, 3000);
			return;
		}

		try {
			await onUpdate(id, column, value);

			// Update local data
			row[column] = value;

			// Show success feedback
			const cellId = `${displayData.indexOf(row)}-${column}`;
			savedCell = cellId;
			saveMessage = 'Saved ✓';

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

			setTimeout(() => {
				savedCell = null;
				saveMessage = '';
			}, 3000);

			cancelEdit();
		}
	}
</script>

{#if showStats}
	<div class="file-meta">
		<div class="meta-info">
			<div class="meta-stats">
				<span class="meta-item">{displayData.length} rows</span>
				<span class="meta-separator">•</span>
				<span class="meta-item">{columns.length} columns</span>
			</div>
		</div>
	</div>
{/if}

{#if searchable && data && data.length > 0}
	<div class="search-panel">
		<div class="search-container">
			<input
				type="text"
				class="search-input"
				placeholder="Search table..."
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
	{#if data && data.length > 0}
		<div class="file-viewer">
			<div class="table-wrapper">
				<table class="data-table">
					<thead>
						<tr>
							{#if showRowNumbers}
								<th class="row-number-header">#</th>
							{/if}
							{#each columns as column, index}
								<th
									class="column-header"
									class:sortable={sortable}
									class:first-column-header={index === 0 && !showRowNumbers}
									onclick={() => handleSort(column)}
								>
									{column}
									{#if sortable && sortColumn === column}
										<span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
									{/if}
								</th>
							{/each}
						</tr>
					</thead>
					<tbody>
						{#each displayData as row, index}
							<tr class="data-row">
								{#if showRowNumbers}
									<td class="row-number" class:selected={selectedRowIndex === index}>
										{#if selectedRowIndex === index}
											<span class="delete-icon">🗑️</span>
										{:else}
											{index + 1}
										{/if}
									</td>
								{/if}
								{#each columns as column, colIndex}
									<td class="data-cell" class:first-column-cell={colIndex === 0 && !showRowNumbers}>
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
			<p>No data to display</p>
		</div>
	{/if}
{:then currentUser}
	{#if data && data.length > 0}
		<div class="file-viewer">
			<div class="table-wrapper">
				<table class="data-table">
					<thead>
						<tr>
							{#if showRowNumbers}
								<th class="row-number-header">#</th>
							{/if}
							{#each columns as column, index}
								<th
									class="column-header"
									class:sortable={sortable}
									class:first-column-header={index === 0 && !showRowNumbers}
									onclick={() => handleSort(column)}
								>
									{column}
									{#if sortable && sortColumn === column}
										<span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
									{/if}
								</th>
							{/each}
						</tr>
					</thead>
					<tbody>
						{#each displayData as row, index}
							<tr class="data-row">
								{#if showRowNumbers}
									<td
										class="row-number"
										class:selected={selectedRowIndex === index}
										class:editable={canDeleteRow(row, currentUser)}
										onclick={() => canDeleteRow(row, currentUser) && selectRowForDeletion(index)}
									>
										{#if selectedRowIndex === index}
											<span class="delete-icon">🗑️</span>
										{:else}
											{index + 1}
										{/if}
									</td>
								{/if}
								{#each columns as column, colIndex}
									<td
										class="data-cell"
										class:editable={canEditCell(row, column, currentUser)}
										class:first-column-cell={colIndex === 0 && !showRowNumbers}
									>
										{#if editingCell === `${index}-${column}`}
											<div class="input-container">
												<input
													bind:value={editValue}
													oninput={(e) => filterAutocomplete(e.target.value, column)}
													onblur={() => {
														setTimeout(() => saveEdit(row, column), 100);
													}}
													onkeydown={(e) => handleKeyboardNavigation(e, row, column)}
													autofocus
												/>
												{#if showAutocomplete && autocompleteOptions.length > 0}
													<div class="autocomplete-dropdown">
														{#each autocompleteOptions.slice(0, 10) as option, optIndex}
															<div
																class="autocomplete-option"
																class:selected={optIndex === selectedOptionIndex}
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
													onclick={() => canEditCell(row, column, currentUser) && startEdit(index, column, row[column], row, currentUser)}
													class:clickable={canEditCell(row, column, currentUser)}
												>
													{formatValue(row[column], column)}
												</span>
												{#if savedCell === `${index}-${column}`}
													<span
														class="save-feedback"
														class:success={saveMessage.includes('✓')}
														class:error={saveMessage.includes('✗')}
													>
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
			<p>No data to display</p>
		</div>
	{/if}
{:catch error}
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
		transition: background-color 0.2s;
	}

	.row-number.editable {
		cursor: pointer;
	}

	.row-number.editable:hover {
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

	.empty-state {
		padding: 2rem;
		text-align: center;
		color: #656d76;
		font-style: italic;
	}

	.error {
		padding: 2rem;
		text-align: center;
		color: #d1242f;
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

	/* Dark mode support */
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

	:global(.dark) .first-column-header,
	:global(.dark) .first-column-cell {
		background: #161b22;
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
</style>