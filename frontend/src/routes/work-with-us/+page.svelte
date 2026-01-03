<script>
	import { reveal, setDefaultOptions } from 'svelte-reveal';
	
	import Slides from './Slides.svelte'
	
	setDefaultOptions({
		easing: 'easeOutCubic',
		duration: 500
	});
</script>

<Slides />

