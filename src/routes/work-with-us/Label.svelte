<!-- Label.svelte with modern CSS variants -->
<script>
	import { reveal } from 'svelte-reveal'
	
	export let useReveal = {};
	export let variant = 'primary';
	export let size = 'medium';
</script>

<p 
	use:reveal={useReveal} 
	class="label" 
	data-variant={variant}
	data-size={size}
>
	<slot/>
</p>

<style>
	.label {
		/* Base styles */
		display: flex;
		color: white;
		font-weight: bold;
		margin-bottom: 1rem;
		width: fit-content;
		border-radius: 0.25rem;
		
		/* Default values using CSS custom properties */
		background: var(--label-bg, violet);
		font-size: var(--label-size, x-large);
		padding: var(--label-padding, 0.25rem 0.5rem);
	}
	
	/* Variant styles using CSS custom properties */
	.label:where([data-variant="primary"]) {
		--label-bg: violet;
	}
	
	.label:where([data-variant="secondary"]) {
		--label-bg: #2aa198;
	}
	
	.label:where([data-variant="accent"]) {
		--label-bg: #667eea;
	}
	
	.label:where([data-variant="success"]) {
		--label-bg: #48bb78;
	}
	
	.label:where([data-variant="warning"]) {
		--label-bg: #ed8936;
	}
	
	/* Size variants */
	.label:where([data-size="small"]) {
		--label-size: medium;
		--label-padding: 0.2rem 0.4rem;
	}
	
	.label:where([data-size="medium"]) {
		--label-size: large;
		--label-padding: 0.25rem 0.5rem;
	}
	
	.label:where([data-size="large"]) {
		--label-size: x-large;
		--label-padding: 0.6rem 0.9rem;
	}

	.label:where([data-size="xlarge"]) {
		--label-size: xx-large;
		--label-padding: 0.8rem 1.2rem;
	}
	
	/* Combination variants - you can mix and match! */
	.label:where([data-variant="accent"][data-size="small"]) {
		--label-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	}
</style>