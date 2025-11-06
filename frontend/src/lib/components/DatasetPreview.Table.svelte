<script>
	import { quickUpdateAnnotation, quickDeleteAnnotation } from '$lib/api/annotations.remote';
	import EditableTable from '$lib/components/EditableTable.svelte';

	let { dataset, datasetName = 'academic-research-groups', filters: routeFilters = {} } = $props();

	// Extract columns from the first row if data exists (excluding id)
	const columns = $derived(dataset && dataset.length > 0 ? Object.keys(dataset[0]).filter(col => col !== 'id') : []);

	// Column data types - much simpler than custom validation functions
	const columnTypes = {
		is_prof: 'binary',
		perceived_as_male: 'binary',
		has_research_group: 'binary',
		group_size: 'integer',
		first_pub_year: 'integer',
		payroll_name: 'text',
		full_name: 'text',
		department: 'text',
	};

	// Wrapper functions for the API calls
	async function handleUpdate(id, field, value) {
		await quickUpdateAnnotation({ id, field, value });
	}

	async function handleDelete(id) {
		await quickDeleteAnnotation({ id });
	}

</script>

<EditableTable
			data={dataset}
			onUpdate={handleUpdate}
			onDelete={handleDelete}
			editableColumns={columns}
			excludeColumns={['id']}
			allowDelete={true}
			searchable={true}
			sortable={true}
			showRowNumbers={true}
			showStats={true}
			columnTypes={columnTypes}
		/>
