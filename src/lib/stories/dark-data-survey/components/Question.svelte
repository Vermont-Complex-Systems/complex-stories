<script>
    import RadioQuestion from './RadioQuestion.svelte';

    let { question, name, value, options, userFingerprint, saveAnswer } = $props();
</script>

<RadioQuestion
    {question}
    {name}
    bind:value
    {options}
    onchange={() => saveAnswer(name, value)}
/>