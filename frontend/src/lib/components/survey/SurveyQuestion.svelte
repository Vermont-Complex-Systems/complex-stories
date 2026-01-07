<script>
    import RadioQuestion from './SurveyQuestion.Radio.svelte';
    import CheckboxQuestion from './SurveyQuestion.Checkbox.svelte';

    let { question, name, value, options, multiple = false, userFingerprint, saveAnswer } = $props();
</script>

{#if multiple}
    <CheckboxQuestion
        {question}
        {name}
        bind:value
        {options}
        onchange={() => saveAnswer(name, value)}
    />
{:else}
    <RadioQuestion
        {question}
        {name}
        bind:value
        {options}
        onchange={() => saveAnswer(name, value)}
    />
{/if}