<script module>
    import Scrolly from '$lib/components/helpers/Scrolly.svelte';

    export { scrollyContent, surveyScrollyContent };
</script>

<!-- Generic scrolly wrapper for story content -->
{#snippet scrollyContent(steps, state, contentRenderer)}
    <div class="scrolly-content">
        <div class="spacer"></div>
        <Scrolly bind:value={state.scrollyIndex}>
            {#each steps as step, i}
                {@const active = state.scrollyIndex === i}
                <div class="step" class:active class:mobile={state.isMobile} class:tablet={state.isTablet}>
                    <div class="step-content">
                        {@render contentRenderer(step, active)}
                    </div>
                </div>
            {/each}
        </Scrolly>
        <div class="spacer"></div>
    </div>
{/snippet}

<!-- Survey-specific scrolly wrapper -->
{#snippet surveyScrollyContent(surveyItems, state, contentRenderer)}
    <div class="scrolly-content survey-scrolly">
        <Scrolly bind:value={state.scrollyIndex}>
            {#each surveyItems as item, i}
                {@const active = state.scrollyIndex === i}
                <div class="step" class:active class:mobile={state.isMobile} class:tablet={state.isTablet}>
                    <div class="step-content">
                        {@render contentRenderer(item, active)}
                    </div>
                </div>
            {/each}
        </Scrolly>
        <div class="spacer"></div>
    </div>
{/snippet}

<style>
    /* Standard scrolly content styling - using :global to apply across all stories */
    :global(.scrolly-content) {
        position: relative;
        z-index: 10;
        width: 100%;
        max-width: 800px;
        margin: 0 auto;
    }

    :global(.spacer) {
        height: 75vh;
    }

    :global(.step) {
        height: 120vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        margin: 0 auto;
    }

    /* Aesthetics of sticky text */
    :global(.step > *) {
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

    /* Aesthetics of sticky text when active */
    :global(.step.active > *) {
        background: white;
        color: black;
    }

    /* Interactive controls within scrolly steps */
    :global(.step-content) {
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
</style>
