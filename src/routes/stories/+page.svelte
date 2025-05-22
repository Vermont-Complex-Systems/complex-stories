<script>
	let { data } = $props();
</script>

<h1>stories</h1>

<ul>
	{#each data.summaries as { slug, title }}
		<li><a href="/stories/{slug}">{title}</a></li>
	{/each}
</ul>
