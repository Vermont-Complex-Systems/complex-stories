<script>
	import { PersonStanding } from '@lucide/svelte';
	
	let { data = [], rows = 5, cellSize = 50, highlightName = null, title = null } = $props();

	let hoveredPerson = $state(null);
	let mousePos = $state({ x: 0, y: 0 });

	let cols = $derived(Math.ceil(Math.sqrt(data.length * 2))); // 1.5x wider than tall
	let actualRows = $derived(Math.ceil(data.length / cols));

	function getPosition(index) {
		return {
			x: (index % cols) * cellSize,
			y: Math.floor(index / cols) * cellSize
		};
	}

	function getColor(person) {
		if (highlightName && person.name === highlightName) {
			return '#FF5722'; // Orange for highlighted person
		}
		return person.has_research_group ? '#4CAF50' : '#FFC107';
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
				<PersonStanding 
					size={cellSize - 2} 
					color={getColor(person)}
					style="cursor: pointer; {highlightName && person.name === highlightName ? 'filter: drop-shadow(0 0 8px currentColor);' : ''}"
				/>
			</foreignObject>
		{/each}
	</svg>

	{#if hoveredPerson}
		<div 
			class="tooltip"
			style:left="{mousePos.x + 10}px"
			style:top="{mousePos.y - 10}px"
		>
			{hoveredPerson.name}<br>
			{hoveredPerson.has_research_group ? 'Has research group' : 'No research group'}
			{#if hoveredPerson.college}
            <br>College: {hoveredPerson.college}
                {/if}
			{#if hoveredPerson.host_dept}
                <br>Department: {hoveredPerson.host_dept}
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