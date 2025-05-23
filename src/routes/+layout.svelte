<script>
	let { children } = $props();
	import "$styles/app.css";
</script>

<nav>
	<a href="/">home</a>
</nav>
<main id="content">
  {@render children?.()}
</main>