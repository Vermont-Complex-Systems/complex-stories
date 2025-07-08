<script>
	import { reveal } from 'svelte-reveal';
</script>

<h1 use:reveal={{ delay: 50 }}>How to work with us!</h1>
<h3 use:reveal={{ delay: 50 }}>Lets work together to write sustainable and reproducible software.</h3>
<div class="box">
    <p use:reveal={{ delay: 50 }}>Jonathan St-Onge</p>
    <p use:reveal={{ delay: 1000 }}>07.08.2025</p>
</div>

<style>
	p {
		line-height: 1.75rem
	}
	
	
	h3 {
		font-size: 1.5rem;
		margin-bottom: 0;
	}
	
	.box {
		display: flex;
		gap: 1rem;
		margin-bottom: 2rem;
	}
</style>