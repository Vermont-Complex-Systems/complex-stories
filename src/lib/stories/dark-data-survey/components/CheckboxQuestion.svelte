<script>
    let { question, name, value = $bindable([]), options, onchange } = $props();

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
    <h3>{question}</h3>
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
</div>

<style>
    .checkbox-question {
        width: 100%;
    }

    h3 {
        margin: 0 0 1rem 0;
        font-size: 1.1rem;
        font-weight: 500;
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

    @media (max-width: 640px) {
        h3 {
            font-size: 1rem;
        }

        .checkbox-option {
            padding: 0.6rem;
        }

        .checkbox-option span {
            font-size: 0.9rem;
        }
    }
</style>
