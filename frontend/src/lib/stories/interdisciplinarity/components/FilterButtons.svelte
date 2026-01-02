<script>
	let {
		value = $bindable('all'),
		options = []
	} = $props()
</script>

<div class="filter-buttons">
	{#each options as option}
		<button
			class="filter-btn"
			class:active={value === option.value}
			onclick={() => value = option.value}
		>
			{option.label}
		</button>
	{/each}
</div>

<style>
	.filter-buttons {
		display: flex;
		gap: 0.25rem;
	}

	.filter-btn {
		padding: 0.5rem 0.75rem;
		font-size: 0.875rem;
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 4px;
		cursor: pointer;
		transition: all 0.2s;
		font-weight: 500;
		color: #666;
	}

	.filter-btn:hover {
		background: #f5f5f5;
	}

	.filter-btn.active {
		background: #2563eb;
		color: white;
		border-color: #2563eb;
	}
</style>
