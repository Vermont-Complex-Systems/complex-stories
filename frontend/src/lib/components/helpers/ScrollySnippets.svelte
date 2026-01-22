<script module>
    import Scrolly from '$lib/components/helpers/Scrolly.svelte';
    import Md from '$lib/components/helpers/MarkdownRenderer.svelte';

    export { scrollyContent, renderTextContent };
</script>

<!-- Shared snippet for rendering common text content types (html, markdown, math) -->
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

<!-- Generic scrolly wrapper for story content
     Uses renderTextContent by default, but allows custom contentRenderer for stories with components -->
{#snippet scrollyContent(steps, state, contentRenderer = renderTextContent)}
    <div class="scrolly-content">
        <div class="spacer"></div>
        <Scrolly bind:value={state.scrollyIndex}>
            {#each steps as step, i}
                {@const active = state.scrollyIndex === i}
                <div class="step" class:active class:mobile={state.isMobile} class:tablet={state.isTablet}>
                    <div class="step-content">
                        {i}
                        {@render contentRenderer(step, active)}
                    </div>
                </div>
            {/each}
        </Scrolly>
        <div class="spacer"></div>
    </div>
{/snippet}

<style>
    /* Standard scrolly content styling - scoped to prevent leakage between stories */
    :global(.scrolly-content) {
        position: relative;
        z-index: 10;
        width: 100%;
        max-width: 800px;
        margin: 0 auto;
    }

    :global(.scrolly-content .spacer) {
        height: 75vh;
    }

    :global(.scrolly-content .step) {
        height: 120vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        margin: 0 auto;
    }

    /* Aesthetics of sticky text - scoped to scrolly-content */
    :global(.scrolly-content .step > *) {
        padding: 1rem;
        background: #f5f5f5;
        color: #ccc;
        border-radius: 5px;
        box-shadow: 1px 1px 10px rgba(0, 0, 0, 0.2);
        transition: all 500ms ease;
        text-align: center;
        max-width: 600px;
        margin: 0 auto;
    }

    /* Aesthetics of sticky text when active - scoped to scrolly-content */
    :global(.scrolly-content .step.active > *) {
        background: white;
        color: black;
    }

    /* Interactive controls within scrolly steps - scoped to scrolly-content */
    :global(.scrolly-content .step-content) {
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
    }

    /* Survey-specific step styling */
    :global(.survey-scrolly .scrolly-content) {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    :global(.survey-scrolly .step) {
        height: 80vh;
    }

    :global(.survey-scrolly .step-content) {
        padding: 2rem;
        background: white;
        color: #333;
        border-radius: 2px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
        transition: all 500ms ease;
        max-width: 360px;
        margin: 0 auto;
        width: 100%;
        opacity: 0.3;
        font-family: 'Georgia', 'Times New Roman', Times, serif;
    }

    :global(.survey-scrolly .step.active .step-content) {
        opacity: 1;
    }

    @media (max-width: 768px) {
        :global(.survey-scrolly .step-content) {
            max-width: 300px;
        }
    }

    /* Content rendering styles */
    .plot-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 0;
        padding: 0;
    }
</style>
