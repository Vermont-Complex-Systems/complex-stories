<script module>
    import Scrolly from '$lib/components/helpers/Scrolly.svelte';
    import { renderTextContent } from '$lib/components/helpers/ScrollySnippets.svelte';
    import Question from './SurveyQuestion.svelte';

    export { surveyScrollyContent };
</script>

<!-- Generic survey scrolly content renderer
     Handles question types and delegates text rendering to shared helper
     Stories must provide: surveyItems, scrollyState, userFingerprint, saveAnswer, answers -->
{#snippet surveyScrollyContent(surveyItems, scrollyState, userFingerprint, saveAnswer, answers)}
    <div class="scrolly-content survey-scrolly">
        <Scrolly bind:value={scrollyState.scrollyIndex}>
            {#each surveyItems as item, i}
                {@const active = scrollyState.scrollyIndex === i}
                <div class="step" class:active class:mobile={scrollyState.isMobile} class:tablet={scrollyState.isTablet}>
                    <div class="step-content">
                        {#if item.type === 'question'}
                            <Question
                                question={item.value.question}
                                name={item.value.name}
                                bind:value={answers[item.value.name]}
                                options={item.value.options}
                                multiple={item.value.multiple || false}
                                {userFingerprint}
                                {saveAnswer}
                            />
                        {:else}
                            {@render renderTextContent(item)}
                        {/if}
                    </div>
                </div>
            {/each}
        </Scrolly>
        <div class="spacer"></div>
    </div>
{/snippet}

<style>
    /* Base survey scrolly structure - stories can override with :global() */
    .scrolly-content {
        position: relative;
        z-index: 10;
        width: 100%;
        max-width: 800px;
        margin: 0 auto;
    }

    .spacer {
        height: 75vh;
    }

    .step {
        height: 80vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        margin: 0 auto;
    }

    /* Default step styling - stories should override with story-specific theme */
    .step-content {
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
    }

    .step.active .step-content {
        opacity: 1;
    }

    @media (max-width: 768px) {
        .step-content {
            max-width: 300px;
        }
    }
</style>
