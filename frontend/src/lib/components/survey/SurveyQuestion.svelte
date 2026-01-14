<script>
    import RadioQuestion from './SurveyQuestion.Radio.svelte';
    import CheckboxQuestion from './SurveyQuestion.Checkbox.svelte';

    let { question, name, value, options, multiple = false, userFingerprint, saveAnswer } = $props();

    // Track save state
    let saveStatus = $state('idle'); // 'idle' | 'saving' | 'saved' | 'error'
    let saveMessage = $state('');

    async function handleSave() {
        saveStatus = 'saving';
        saveMessage = 'Saving...';

        try {
            await saveAnswer(name, value);
            saveStatus = 'saved';
            saveMessage = 'Saved ✓';

            // Clear feedback after 2 seconds
            setTimeout(() => {
                saveStatus = 'idle';
                saveMessage = '';
            }, 2000);
        } catch (error) {
            console.error('Failed to save answer:', error);
            saveStatus = 'error';
            saveMessage = 'Error ✗';

            // Clear error after 3 seconds
            setTimeout(() => {
                saveStatus = 'idle';
                saveMessage = '';
            }, 3000);
        }
    }
</script>

{#if multiple}
    <CheckboxQuestion
        {question}
        {name}
        bind:value
        {options}
        onchange={handleSave}
        {saveStatus}
        {saveMessage}
    />
{:else}
    <RadioQuestion
        {question}
        {name}
        bind:value
        {options}
        onchange={handleSave}
        {saveStatus}
        {saveMessage}
    />
{/if}