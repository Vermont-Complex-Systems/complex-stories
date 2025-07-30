<script>
	let { 
		person,
		size = 48,
		highlightName = null,
		highlightCategory = null
	} = $props();

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

	let color = $derived(getColor(person));
	let glow = $derived(shouldHighlight(person) ? 'filter: drop-shadow(0 0 8px currentColor);' : '');
	let iconSize = $derived(size - 2);
</script>

{#if person.perceived_as_male === 0}
	<!-- Female - filled with thicker stroke -->
	<svg 
		width={iconSize} 
		height={iconSize} 
		viewBox="0 0 24 24" 
		fill={color} 
		stroke={color} 
		stroke-width="1" 
		stroke-linecap="round" 
		stroke-linejoin="round" 
		style="cursor: pointer; {glow}"
	>
		<circle cx="12" cy="5" r="2"/>
		<path d="m9 20 3-6 3 6"/>
		<path d="m6 8 6 2 6-2"/>
		<path d="M12 10v4"/>
	</svg>
{:else}
	<!-- Male - outline only with thicker stroke -->
	<svg 
		width={iconSize} 
		height={iconSize} 
		viewBox="0 0 24 24" 
		fill="none" 
		stroke={color} 
		stroke-width="2.5" 
		stroke-linecap="round" 
		stroke-linejoin="round" 
		style="cursor: pointer; {glow}"
	>
		<circle cx="12" cy="5" r="1"/>
		<path d="m9 20 3-6 3 6"/>
		<path d="m6 8 6 2 6-2"/>
		<path d="M12 10v4"/>
	</svg>
{/if}