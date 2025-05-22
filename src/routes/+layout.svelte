<script>
	let { children } = $props();
</script>

<nav>
	<a href="/">home</a>
	<a href="/stories">stories</a>
</nav>

{@render children()}