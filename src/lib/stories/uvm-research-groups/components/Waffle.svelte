<script>
	import PersonIcon from './PersonIcon.svelte';
	
	let { data = [], rows = 5, cellSize = 50, highlightName = null, highlightCategory = null, title = null } = $props();

	let hoveredPerson = $state(null);
	let mousePos = $state({ x: 0, y: 0 });

	let cols = $derived(Math.ceil(Math.sqrt(data.length * 2))); // 2x wider than tall
	let actualRows = $derived(Math.ceil(data.length / cols));

	function getPosition(index) {
		return {
			x: (index % cols) * cellSize,
			y: Math.floor(index / cols) * cellSize
		};
	}
</script>

<div class="waffle">
	{#if title}
		<h4>{title}</h4>
	{/if}
	
	<svg width={cols * cellSize} height={actualRows * cellSize}>
		{#each data as person, i}
			{@const pos = getPosition(i)}
			<foreignObject
				x={pos.x}
				y={pos.y}
				width={cellSize}
				height={cellSize}
				onmouseenter={() => hoveredPerson = person}
				onmouseleave={() => hoveredPerson = null}
				onmousemove={(e) => mousePos = { x: e.clientX, y: e.clientY }}
			>
				<div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
					<PersonIcon 
						{person} 
						size={cellSize} 
						{highlightName} 
						{highlightCategory} 
					/>
				</div>
			</foreignObject>
		{/each}
	</svg>

	{#if hoveredPerson}
		<div 
			class="tooltip"
			style:left="{mousePos.x + 10}px"
			style:top="{mousePos.y - 10}px"
		>
			{hoveredPerson.ego_display_name}<br>
			{hoveredPerson.has_research_group ? 'Has research group' : 'No research group'}
			{#if hoveredPerson.college}
				<br>College: {hoveredPerson.college}
			{/if}
			{#if hoveredPerson.department}
				<br>Department: {hoveredPerson.department}
			{/if}
			{#if highlightCategory === 'no_oa_uid'}
				<br>OpenAlex ID: {hoveredPerson.oa_uid || 'None'}
			{/if}
		</div>
	{/if}
</div>

<style>
	.waffle {
		position: relative;
		display: inline-block;
	}

	h4 {
		margin: 0 0 0.5rem 0;
		font-size: 14px;
		font-weight: bold;
		color: #666;
	}

	.tooltip {
		position: fixed;
		background: black;
		color: white;
		padding: 8px;
		border-radius: 4px;
		font-size: 12px;
		pointer-events: none;
		z-index: 1000;
	}
</style>