<script>
    import { Accordion } from "bits-ui";
    
    let { 
        sys1 = $bindable(null),
        sys2 = $bindable(null),
        title = $bindable(['System 1', 'System 2'])
    } = $props();
    
    let fileInput1, fileInput2;
    let uploadStatus = $state('');

    async function handleFileUpload(file, system) {
        try {
            uploadStatus = `Loading ${system}...`;
            const text = await file.text();
            const data = JSON.parse(text);
            
            if (system === 'sys1') {
                sys1 = data;
                title[0] = file.name.replace('.json', '');
            } else {
                sys2 = data;
                title[1] = file.name.replace('.json', '');
            }
            
            uploadStatus = `${system.toUpperCase()} loaded successfully!`;
            setTimeout(() => uploadStatus = '', 3000);
        } catch (error) {
            uploadStatus = `Error loading ${system}: ${error.message}`;
            setTimeout(() => uploadStatus = '', 5000);
        }
    }
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
    }

    .input-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .input-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--text-primary);
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
        border: 1px solid var(--border-color);
        border-radius: var(--radius);
        background-color: var(--bg-secondary);
        color: var(--text-primary);
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .file-input-button:hover {
        background-color: var(--border-color);
        border-color: var(--accent-color);
    }

    .upload-status {
        font-size: 0.875rem;
        padding: 0.75rem;
        border-radius: var(--radius);
        font-weight: 500;
    }

    .upload-status.success {
        color: var(--success-color);
        background-color: rgba(40, 167, 69, 0.1);
        border: 1px solid var(--success-color);
    }

    .upload-status.error {
        color: var(--error-color);
        background-color: rgba(220, 53, 69, 0.1);
        border: 1px solid var(--error-color);
    }
</style>