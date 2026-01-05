<script module>
	import Md from '$lib/components/helpers/MarkdownRenderer.svelte';

	export { renderTextContent };
</script>

<!-- Shared snippet for rendering common text content types (html, markdown, math) -->
<!-- Component rendering must be handled story-specifically since components can't be passed as data -->
{#snippet renderTextContent(item)}
	{#if item.type === "html"}
		{@html item.value}
	{:else if item.type === "markdown"}
		<Md text={item.value}/>
	{:else if item.type === "math"}
		<div class="plot-container">
			<Md text={item.value}/>
		</div>
	{/if}
{/snippet}

<style>
    .plot-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 0;
        padding: 0;
    }        
</style>