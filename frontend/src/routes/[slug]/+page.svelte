<script>
	let { data } = $props();
</script>

{#await import(`$lib/stories/${data.story.slug}/components/Index.svelte`) then mod}
	<mod.default story={data.story} data={data.copyData} />
{/await}
