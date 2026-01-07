<script>
	let {
		value = $bindable(''),
		placeholder = 'Search...'
	} = $props()
</script>

<input
	type="text"
	bind:value
	{placeholder}
	class="search-input"
/>

<style>
	.search-input {
		flex: 1;
		padding: 0.5rem 0.75rem;
		border: 1px solid #e0e0e0;
		border-radius: 4px;
		font-size: 0.875rem;
	}

	.search-input:focus {
		outline: none;
		border-color: #2563eb;
	}
</style>
