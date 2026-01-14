<script>
    let { question, name, value = $bindable([]), options, onchange, saveStatus = 'idle', saveMessage = '' } = $props();

    function handleCheckboxChange(optionValue, isChecked) {
        if (isChecked) {
            value = [...value, optionValue];
        } else {
            value = value.filter(v => v !== optionValue);
        }
        onchange();
    }
</script>

<div class="checkbox-question">
    <div class="question-header">
        <h3>{question}</h3>
    </div>
    <div class="options">
        {#each options as option}
            <label class="checkbox-option">
                <input
                    type="checkbox"
                    name={name}
                    value={option.value}
                    checked={value.includes(option.value)}
                    onchange={(e) => handleCheckboxChange(option.value, e.target.checked)}
                />
                <span>{option.label}</span>
            </label>
        {/each}
    </div>
    <div class="save-feedback-container">
        {#if saveMessage}
            <span
                class="save-feedback"
                class:success={saveStatus === 'saved'}
                class:error={saveStatus === 'error'}
                class:saving={saveStatus === 'saving'}
            >
                {saveMessage}
            </span>
        {/if}
    </div>
</div>

<style>
    .checkbox-question {
        width: 100%;
    }

    .question-header {
        text-align: center;
        margin-bottom: 1rem;
    }

    h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
        font-weight: 600;
        color: #333;
        line-height: 1.4;
    }

    .options {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .checkbox-option {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        background: #f9f9f9;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .checkbox-option:hover {
        background: #f0f0f0;
        border-color: #0891b2;
    }

    input[type="checkbox"] {
        width: 18px;
        height: 18px;
        cursor: pointer;
        accent-color: #0891b2;
    }

    .checkbox-option span {
        flex: 1;
        font-size: 1rem;
        color: #333;
    }

    .save-feedback-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 0.75rem;
        min-height: 1.5rem;
    }

    .save-feedback {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 500;
        padding: 0.2rem 0.6rem;
        border-radius: 3px;
        opacity: 0;
        animation: fadeInOut 2s ease-in-out;
        white-space: nowrap;
    }

    .save-feedback.success {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }

    .save-feedback.error {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }

    .save-feedback.saving {
        background: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
        opacity: 1;
    }

    @keyframes fadeInOut {
        0% { opacity: 0; transform: translateY(-2px); }
        20% { opacity: 1; transform: translateY(0); }
        80% { opacity: 1; transform: translateY(0); }
        100% { opacity: 0; transform: translateY(-2px); }
    }

    @media (max-width: 640px) {
        h3 {
            font-size: 1.3rem !important;
        }

        .checkbox-option {
            padding: 0.6rem;
        }

        .checkbox-option span {
            font-size: 0.9rem;
        }
    }
</style>
