<script module>
    import Scrolly from '$lib/components/helpers/Scrolly.svelte';
    import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
    
    export { renderContent, scrollyContent, surveyContent };
</script>

{#snippet renderContent(contentArray)}
    {#each contentArray as { type, value, component }, i}
        {#if type === "html" }
            {@html value}
        {:else if type === "math" }
            <Md text={value}/>
        {:else}
            <Md text={value}/>
        {/if}
    {/each}
{/snippet}

{#snippet scrollyContent(steps, state, options = {})}
    <div class="scrolly-content">
        <div class="spacer"></div>
        <Scrolly bind:value={state.scrollyIndex}>
            {#each steps as text, i}
                {@const active = state.scrollyIndex === i}
                <div class="step" class:active class:mobile={state.isMobile} class:tablet={state.isTablet}>
                    <div class="step-content">
                        {@render renderContent([text])}
                        
                        {#if options.interactive && options.responses}
                            <div class="interactive-controls">
                                {#if i === 0}
                                    <!-- Social media privacy -->
                                    <select bind:value={options.responses.socialMedia}>
                                        <option value="">Choose...</option>
                                        <option value="private">Private</option>
                                        <option value="public">Public</option>
                                        <option value="mixed">Mixed</option>
                                    </select>
                                {:else if i === 1}
                                    <!-- Platform matter -->
                                    <select bind:value={options.responses.platformMatters}>
                                        <option value="">Choose...</option>
                                        <option value="yes">Yes, platform matters</option>
                                        <option value="no">No, same across platforms</option>
                                        <option value="sometimes">Sometimes</option>
                                    </select>
                                {:else if i === 2}
                                    <!-- Institution preferences -->
                                    <select bind:value={options.responses.institutionPreferences}>
                                        <option value="">Choose...</option>
                                        <option value="vary-greatly">Vary greatly</option>
                                        <option value="mostly-same">Mostly the same</option>
                                        <option value="depends-context">Depends on context</option>
                                    </select>
                                {:else if i === 3}
                                    <!-- Demographics matter -->
                                    <select bind:value={options.responses.demographicsMatter}>
                                        <option value="">Choose...</option>
                                        <option value="yes">Yes, who I am matters</option>
                                        <option value="no">No, preferences are universal</option>
                                        <option value="somewhat">Somewhat</option>
                                    </select>
                                {/if}
                            </div>
                        {/if}
                    </div>
                </div>
            {/each}
        </Scrolly>
        
        <!-- Submit button and status -->
        {#if options.interactive && options.onSubmit && options.submissionStatus}
            <div class="survey-submit">
                {#if options.submissionStatus.success}
                    <div class="success-message">
                        ✅ Thank you! Your responses have been saved.
                    </div>
                {:else}
                    <button 
                        onclick={options.onSubmit}
                        disabled={options.submissionStatus.submitting}
                        class="submit-button"
                        class:submitting={options.submissionStatus.submitting}
                    >
                        {#if options.submissionStatus.submitting}
                            Submitting...
                        {:else}
                            Submit Survey
                        {/if}
                    </button>
                    
                    {#if options.submissionStatus.error}
                        <div class="error-message">
                            ❌ {options.submissionStatus.error}
                        </div>
                    {/if}
                {/if}
            </div>
        {/if}
        
        <div class="spacer"></div>
    </div>
{/snippet}

{#snippet surveyContent(surveyQuestions, responses)}
    <div class="survey-container">
        {#each surveyQuestions as question, i}
            <div class="survey-question">
                <div class="question-text">
                    {@render renderContent([question])}
                </div>
                <div class="survey-controls">
                    {#if i === 0}
                        <!-- Social media privacy -->
                        <select bind:value={responses.socialMedia}>
                            <option value="">Choose...</option>
                            <option value="private">Private</option>
                            <option value="public">Public</option>
                            <option value="mixed">Mixed</option>
                        </select>
                    {:else if i === 1}
                        <!-- Platform matter -->
                        <select bind:value={responses.platformMatters}>
                            <option value="">Choose...</option>
                            <option value="yes">Yes, platform matters</option>
                            <option value="no">No, same across platforms</option>
                            <option value="sometimes">Sometimes</option>
                        </select>
                    {:else if i === 2}
                        <!-- Institution preferences -->
                        <select bind:value={responses.institutionPreferences}>
                            <option value="">Choose...</option>
                            <option value="vary-greatly">Vary greatly</option>
                            <option value="mostly-same">Mostly the same</option>
                            <option value="depends-context">Depends on context</option>
                        </select>
                    {:else if i === 3}
                        <!-- Demographics matter -->
                        <select bind:value={responses.demographicsMatter}>
                            <option value="">Choose...</option>
                            <option value="yes">Yes, who I am matters</option>
                            <option value="no">No, preferences are universal</option>
                            <option value="somewhat">Somewhat</option>
                        </select>
                    {/if}
                </div>
            </div>
        {/each}
        
        {#if responses.socialMedia && responses.platformMatters && responses.institutionPreferences && responses.demographicsMatter}
            <div class="survey-summary">
                <h3>Your Privacy Profile:</h3>
                <p>Social Media: <strong>{responses.socialMedia}</strong></p>
                <p>Platform Sensitivity: <strong>{responses.platformMatters}</strong></p>
                <p>Institution Preferences: <strong>{responses.institutionPreferences}</strong></p>
                <p>Demographics Impact: <strong>{responses.demographicsMatter}</strong></p>
            </div>
        {/if}
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
        height: 35vh;
    }

    .step {
        height: 80vh;
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

    .interactive-controls {
        margin-top: 1rem;
        padding: 0 1rem;
    }

    .interactive-controls select {
        width: 100%;
        padding: 0.75rem;
        border: 2px solid #ddd;
        border-radius: 4px;
        font-size: 1rem;
        background: white;
        cursor: pointer;
        transition: border-color 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .interactive-controls select:hover {
        border-color: var(--color-primary, #007acc);
    }

    .interactive-controls select:focus {
        outline: none;
        border-color: var(--color-primary, #007acc);
        box-shadow: 0 0 0 3px rgba(0, 122, 204, 0.1);
    }

    /* Style selected option differently */
    .interactive-controls select:not([value=""]) {
        background: #f8f9fa;
        border-color: #28a745;
    }

    /* Survey submit section */
    .survey-submit {
        text-align: center;
        padding: 2rem;
        max-width: 600px;
        margin: 0 auto;
    }

    .submit-button {
        background: #007acc;
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        min-width: 150px;
    }

    .submit-button:hover:not(:disabled) {
        background: #0066aa;
        transform: translateY(-1px);
    }

    .submit-button:disabled {
        background: #ccc;
        cursor: not-allowed;
        transform: none;
    }

    .submit-button.submitting {
        background: #6c757d;
    }

    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        font-weight: 500;
        margin: 1rem 0;
    }

    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
        font-weight: 500;
        margin: 1rem 0;
    }

    /* Survey styling */
    .survey-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
    }

    .survey-question {
        margin-bottom: 2rem;
        padding: 1.5rem;
        background: #f9f9f9;
        border-radius: 8px;
        border-left: 4px solid var(--color-primary, #007acc);
    }

    .question-text {
        margin-bottom: 1rem;
        font-weight: 500;
    }

    .survey-controls select {
        width: 100%;
        padding: 0.75rem;
        border: 2px solid #ddd;
        border-radius: 4px;
        font-size: 1rem;
        background: white;
        cursor: pointer;
        transition: border-color 0.2s ease;
    }

    .survey-controls select:hover {
        border-color: var(--color-primary, #007acc);
    }

    .survey-controls select:focus {
        outline: none;
        border-color: var(--color-primary, #007acc);
        box-shadow: 0 0 0 3px rgba(0, 122, 204, 0.1);
    }

    .survey-summary {
        margin-top: 3rem;
        padding: 2rem;
        background: linear-gradient(135deg, #e3f2fd 0%, #f1f8e9 100%);
        border-radius: 12px;
        border: 1px solid #90caf9;
    }

    .survey-summary h3 {
        margin: 0 0 1rem 0;
        color: #1565c0;
        font-family: var(--serif);
    }

    .survey-summary p {
        margin: 0.5rem 0;
        font-size: 1.1rem;
    }

    .survey-summary strong {
        color: #2e7d32;
        text-transform: capitalize;
    }
</style>