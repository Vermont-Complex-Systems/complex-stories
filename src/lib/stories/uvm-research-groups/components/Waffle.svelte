<script>
	import { PersonStanding } from '@lucide/svelte';
	
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

	function getColor(person) {
		// Individual name highlighting takes priority
		if (highlightName && person.name === highlightName) {
			return 'red';
		}
		
		// Category highlighting
		if (highlightCategory) {
			switch (highlightCategory) {
				case 'no_oa_uid':
					if (!person.oa_uid) {
						return '#FF5722'; // Orange for no OpenAlex ID
					}
					break;
				case 'male':
					if (person.perceived_as_male === 1) {
						return '#2196F3'; // Blue for perceived male
					}
					break;
				case 'female':
					if (person.perceived_as_male === 0) {
						return '#E91E63'; // Pink for perceived female
					}
					break;
				case 'professor':
					if (person.is_prof === 1) {
						return '#9C27B0'; // Purple for professors
					}
					break;
			}
		}
		
		// Default colors based on research group
		return person.has_research_group ? '#ffd100' : '#257355';
	}

	function shouldHighlight(person) {
		// Check if person should have glow effect
		if (highlightName && person.name === highlightName) {
			return true;
		}
		
		if (!highlightCategory) return false;
		
		switch (highlightCategory) {
			case 'no_oa_uid':
				return !person.oa_uid;
			case 'male':
				return person.perceived_as_male === 1;
			case 'female':
				return person.perceived_as_male === 0;
			case 'professor':
				return person.is_prof === 1;
			default:
				return false;
		}
	}

	function getPersonSvg(person) {
		const size = cellSize - 2;
		const color = getColor(person);
		const glow = shouldHighlight(person) ? 'filter: drop-shadow(0 0 8px currentColor);' : '';
		
		if (person.perceived_as_male === 0) {
			// Female - filled with thicker stroke
			return `
				<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="${color}" stroke="${color}" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" style="cursor: pointer; ${glow}">
					<circle cx="12" cy="5" r="2"/>
					<path d="m9 20 3-6 3 6"/>
					<path d="m6 8 6 2 6-2"/>
					<path d="M12 10v4"/>
				</svg>
			`;
		} else {
			// Male - outline only with thicker stroke
			return `
				<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="cursor: pointer; ${glow}">
					<circle cx="12" cy="5" r="1"/>
					<path d="m9 20 3-6 3 6"/>
					<path d="m6 8 6 2 6-2"/>
					<path d="M12 10v4"/>
				</svg>
			`;
		}
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
					{@html getPersonSvg(person)}
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
			{hoveredPerson.name}<br>
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