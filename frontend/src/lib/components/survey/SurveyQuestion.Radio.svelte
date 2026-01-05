<script>
import { RadioGroup, Label } from "bits-ui";

let { question, name, value = $bindable(), options, errors, onchange } = $props();
</script>

<div class="question-text">
    <h3>{question}</h3>
</div>
<div class="survey-controls">
    <RadioGroup.Root bind:value {name} class="radio-group" onValueChange={onchange}>
        {#each options as option}
            <div class="radio-item">
                <RadioGroup.Item id={`${name}-${option.value}`} value={option.value} class="radio-button" />
                <Label.Root for={`${name}-${option.value}`} class="radio-label">{option.label}</Label.Root>
            </div>
        {/each}
    </RadioGroup.Root>
    {#if errors}
        {#each errors as error}
            <p class="error">{error.message}</p>
        {/each}
    {/if}
</div>

<style>
    .question-text h3 {
        margin: 0 0 1rem 0;
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        text-align: center;
    }

    :global(.radio-group) {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        margin: 0 auto;
        width: fit-content;
    }

    :global(.radio-item) {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    :global(.radio-button) {
        width: 20px;
        height: 20px;
        border: 2px solid #666;
        border-radius: 50%;
        background: white;
        cursor: pointer;
        transition: all 0.2s ease;
        flex-shrink: 0;
    }

    :global(.radio-button:hover) {
        border-color: var(--color-primary, #007acc);
    }

    :global(.radio-button[data-state="checked"]) {
        border-width: 6px;
        border-color: var(--color-primary, #007acc);
    }

    :global(.radio-label) {
        cursor: pointer;
        user-select: none;
        color: #333;
    }

    .error {
        background: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 4px;
        border: 1px solid #f5c6cb;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
</style>