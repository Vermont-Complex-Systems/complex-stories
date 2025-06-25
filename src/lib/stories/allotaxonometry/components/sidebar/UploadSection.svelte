<script>
    import { Accordion } from "bits-ui";
    
    let { 
        sys1 = $bindable(null),
        sys2 = $bindable(null),
        title = $bindable(['System 1', 'System 2']),
        handleFileUpload,
        uploadStatus
    } = $props();
    
    let fileInput1, fileInput2;
</script>

<Accordion.Item value="upload" class="accordion-item">
    <Accordion.Header>
        <Accordion.Trigger class="accordion-trigger">
            <span>📁 Upload Data</span>
        </Accordion.Trigger>
    </Accordion.Header>
    <Accordion.Content class="accordion-content">
        <div class="upload-section">
            <div class="input-group">
                <label for="file1" class="input-label">System 1 (.json)</label>
                <div class="file-input-wrapper">
                    <input 
                        id="file1"
                        type="file" 
                        accept=".json"
                        bind:this={fileInput1}
                        onchange={(e) => e.target.files[0] && handleFileUpload(e.target.files[0], 'sys1')}
                        class="file-input-hidden"
                    />
                    <button class="file-input-button" onclick={() => fileInput1.click()}>
                        Choose file
                    </button>
                </div>
            </div>
            
            <div class="input-group">
                <label for="file2" class="input-label">System 2 (.json)</label>
                <div class="file-input-wrapper">
                    <input 
                        id="file2"
                        type="file" 
                        accept=".json"
                        bind:this={fileInput2}
                        onchange={(e) => e.target.files[0] && handleFileUpload(e.target.files[0], 'sys2')}
                        class="file-input-hidden"
                    />
                    <button class="file-input-button" onclick={() => fileInput2.click()}>
                        Choose file
                    </button>
                </div>
            </div>
            
            {#if uploadStatus}
                <div class="upload-status {uploadStatus.includes('Error') ? 'error' : 'success'}">
                    {uploadStatus}
                </div>
            {/if}
        </div>
    </Accordion.Content>
</Accordion.Item>

<style>
    .upload-section {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-top: 1rem;
    }

    .input-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .input-label {
        font-size: var(--14px);
    }

    .file-input-wrapper {
        position: relative;
    }

    .file-input-hidden {
        position: absolute;
        opacity: 0;
        pointer-events: none;
    }

    .file-input-button {
        width: 100%;
        padding: 0.75rem;
        background-color: var(--color-input-bg);
        color: var(--color-input-fg);
        font-size: var(--14px);
        font-family: var(--font-form);
        cursor: pointer;
        transition: all var(--transition-medium) ease;
    }

    .file-input-button:hover {
        background-color: var(--color-gray-200);
        border-color: var(--color-good-blue);
    }

    :global(.dark) .file-input-button:hover {
        background-color: var(--color-gray-700);
    }

    .upload-status {
        font-size: var(--14px);
        padding: 0.75rem;
        border-radius: var(--border-radius);
        font-weight: var(--font-weight-normal);
        font-family: var(--font-form);
    }

    .upload-status.success {
        color: var(--color-electric-green);
        background-color: rgba(58, 230, 96, 0.1);
        border: 1px solid var(--color-electric-green);
    }

    .upload-status.error {
        color: var(--color-red);
        background-color: rgba(255, 83, 61, 0.1);
        border: 1px solid var(--color-red);
    }
</style>