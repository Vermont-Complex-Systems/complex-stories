<script>
	import { reveal, setDefaultOptions } from 'svelte-reveal';
	
	import Slide1 from './Slide1.svelte';
	import Slide2 from './Slide2.svelte';
	import Slide3a from './Slide3a.svelte';
	import Slide3b from './Slide3b.svelte';
	import Slide3c from './Slide3c.svelte';
	import Slide4 from './Slide4.svelte';
	import Divider from './Divider.svelte';
	
	setDefaultOptions({
		easing: 'easeOutCubic',
		duration: 500
	});
</script>

<Slide1 />
<Divider />
<Slide2 />
<Divider />
<Slide3a />
<Divider />
<Slide3b />
<Divider />
<Slide3c />
<Divider />
<Slide4 />

<style>
	:global(p) {
		line-height: 1.5rem;
	}
</style>