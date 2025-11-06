<script module>
    import Scrolly from '$lib/components/helpers/Scrolly.svelte';
    import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
    import Question from './Survey.Question.svelte';
    import BarChartRank from './BarChartRank.svelte';
    import {countCategory} from '../data/data.remote'

    export { renderContent, scrollyContent, surveyScrollyContent };
</script>

{#snippet renderContent(contentArray, userFingerprint = null, saveAnswer = null, answers = null)}
    {#each contentArray as { type, value, component }, i}
        {#if type === 'question' && userFingerprint && saveAnswer && answers}
            <Question
                question={value.question}
                name={value.name}
                bind:value={answers[value.name]}
                options={value.options}
                multiple={value.multiple || false}
                {userFingerprint}
                {saveAnswer}
            />
        {:else if type === "html"}
            {@html value}
        {:else if type === "math"}
            <Md text={value}/>
        <!-- Each component should be added here. A bit sloppy. -->
        {:else if type === "component"}
            {#if component === "chart-rank"}
                {#await countCategory("TP_Social")}
                    load..
                {:then data} 
                    <div class="chart-rank">
                        <BarChartRank {data} fill={'types'}/>
                    </div>
                {/await}    
            {/if}
        {:else if type === "markdown"}
            <Md text={value}/>
        {/if}
    {/each}
{/snippet}

<!-- Non-survey scrolly content snippet -->
{#snippet scrollyContent(steps, state)}
    <div class="scrolly-content">
        <div class="spacer"></div>
        <Scrolly bind:value={state.scrollyIndex}>
            {#each steps as text, i}
                {@const active = state.scrollyIndex === i}
                <div class="step" class:active class:mobile={state.isMobile} class:tablet={state.isTablet}>
                    <div class="step-content">
                        {@render renderContent([text])}
                    </div>
                </div>
            {/each}
        </Scrolly>
        <div class="spacer"></div>
    </div>
{/snippet}

<!-- Survey scrolly content snippet -->
{#snippet surveyScrollyContent(surveyItems, state, userFingerprint, saveAnswer, answers)}
    <div class="scrolly-content survey-scrolly">
        <Scrolly bind:value={state.scrollyIndex}>
            {#each surveyItems as item, i}
                {@const active = state.scrollyIndex === i}
                <div class="step" class:active class:mobile={state.isMobile} class:tablet={state.isTablet}>
                    <div class="step-content">
                        {@render renderContent([item], userFingerprint, saveAnswer, answers)}
                    </div>
                </div>
            {/each}
        </Scrolly>
        <div class="spacer"></div>
    </div>
{/snippet}


<style>
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
        height: 120vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        margin: 0 auto;
    }

    /* esthetics of sticky text */
    .step > :global(*) {
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

    /* esthetics of sticky text _when active_ */
    .step.active > :global(*) {
        background: white;
        color: black;
    }

    /* Interactive controls within scrolly steps */
    .step-content {
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
    }

    /* Survey-specific step styling */
    .survey-scrolly .scrolly-content {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .survey-scrolly .step {
        height: 80vh;
    }

    .survey-scrolly .step-content {
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

    .survey-scrolly .step.active .step-content {
        opacity: 1;
    }

    @media (max-width: 768px) {
        .survey-scrolly .step-content {
            max-width: 300px;
        }
    }

    .chart-rank {
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
</style>