<script>
	import { base } from '$app/paths';
	import "$styles/app.css";
	let { children } = $props();
</script>

<nav>
	<a href="{base}/">home</a>
</nav>
<main id="content">
	{@render children?.()}
</main>