<script>
    import { Button } from "bits-ui";
    
    let {
        sys1 = $bindable(null),
        sys2 = $bindable(null),
        title = $bindable(['System 1', 'System 2']),
        handleFileUpload,
        uploadStatus,
        uploadWarnings = []
    } = $props();
    
    let fileInput;
    let dragOver = $state(false);
    let availableFiles = $state([]);
    let selectedSys1Index = $state(0);
    let selectedSys2Index = $state(1);
    
    // Handle file selection and auto-populate first two
    async function handleFiles(files) {
        const newFiles = [];

        for (const file of files) {
            newFiles.push({
                id: crypto.randomUUID(),
                name: file.name.replace(/\.(json|csv)$/i, ''),
                fileType: file.name.split('.').pop()?.toLowerCase(),
                file: file,
                addedAt: new Date()
            });
        }

        // Sort alphabetically for consistent ordering
        newFiles.sort((a, b) => a.name.localeCompare(b.name));
        availableFiles = newFiles;

        // Reset selections and auto-upload first two
        selectedSys1Index = 0;
        selectedSys2Index = Math.min(1, availableFiles.length - 1);

        if (availableFiles.length >= 1) {
            await uploadToSystem(availableFiles[0], 'sys1');
        }
        if (availableFiles.length >= 2) {
            await uploadToSystem(availableFiles[1], 'sys2');
        }
    }
    
    // Direct upload on click
    async function uploadToSystem(fileEntry, system) {
        const result = await handleFileUpload(fileEntry.file, system);
        return result;
    }
    
    // Handle keyboard navigation
    function handleSys1KeyDown(e) {
        if (!availableFiles.length) return;
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedSys1Index = Math.min(selectedSys1Index + 1, availableFiles.length - 1);
            uploadToSystem(availableFiles[selectedSys1Index], 'sys1');
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedSys1Index = Math.max(selectedSys1Index - 1, 0);
            uploadToSystem(availableFiles[selectedSys1Index], 'sys1');
        }
    }
    
    function handleSys2KeyDown(e) {
        if (!availableFiles.length) return;
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedSys2Index = Math.min(selectedSys2Index + 1, availableFiles.length - 1);
            uploadToSystem(availableFiles[selectedSys2Index], 'sys2');
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedSys2Index = Math.max(selectedSys2Index - 1, 0);
            uploadToSystem(availableFiles[selectedSys2Index], 'sys2');
        }
    }
    
    // Handle option keyboard events
    function handleOptionKeyDown(e, index, system) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            if (system === 'sys1') {
                selectSys1File(index);
            } else {
                selectSys2File(index);
            }
        }
    }
    
    // Handle click selection
    function selectSys1File(index) {
        selectedSys1Index = index;
        uploadToSystem(availableFiles[index], 'sys1');
    }
    
    function selectSys2File(index) {
        selectedSys2Index = index;
        uploadToSystem(availableFiles[index], 'sys2');
    }
    
    function clearFiles() {
        availableFiles = [];
    }
    
    // Drag and drop handlers
    function handleDragOver(e) {
        e.preventDefault();
        dragOver = true;
    }
    
    function handleDragLeave(e) {
        e.preventDefault();
        dragOver = false;
    }
    
    function handleDrop(e) {
        e.preventDefault();
        dragOver = false;
        const files = Array.from(e.dataTransfer.files).filter(f => 
            f.name.endsWith('.json') || f.name.endsWith('.csv')
        );
        if (files.length > 0) {
            handleFiles(files);
        }
    }

    // Handle drop zone keyboard events
    function handleDropZoneKeyDown(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            fileInput.click();
        }
    }
</script>

<div class="upload-container">
    <div class="upload-content">
        <div class="upload-section">
            <!-- Drop Zone with proper accessibility -->
            <div
                class="drop-zone {dragOver ? 'drag-over' : ''}"
                ondragover={handleDragOver}
                ondragleave={handleDragLeave}
                ondrop={handleDrop}
                onkeydown={handleDropZoneKeyDown}
                onclick={() => fileInput.click()}
                role="button"
                tabindex="0"
                aria-label="Upload files by dragging and dropping or clicking to browse"
            >
                <input
                    type="file"
                    accept=".json,.csv"
                    multiple
                    bind:this={fileInput}
                    onchange={(e) => e.target.files?.length && handleFiles(Array.from(e.target.files))}
                    class="file-input-hidden"
                />
                
                <div class="drop-zone-content">
                    <div class="upload-icon">📁</div>
                    <p class="drop-text">
                        Drag files or
                        <button
                            class="browse-link"
                            onclick={() => fileInput.click()}
                        >
                            browse
                        </button>
                    </p>
                </div>
            </div>

            <p class="upload-hint">
                Hint: when browsing files, hold Ctrl to select multiple files to compare.
            </p>
            
            <!-- Multi-Select Widgets -->
            {#if availableFiles.length > 0}
                <div class="multiselect-container">
                    <!-- System 1 -->
                    <div class="multiselect-widget">
                        <div class="widget-label">
                            <span class="system-number sys1">1</span>
                            System 1
                        </div>
                        <div 
                            class="custom-select"
                            onkeydown={handleSys1KeyDown}
                            tabindex="0"
                            role="listbox"
                            aria-label="System 1 files"
                        >
                            {#each availableFiles as file, index (file.id)}
                                <div 
                                    class="select-option {selectedSys1Index === index ? 'selected' : ''} {index === 0 ? 'auto-selected' : ''}"
                                    onclick={() => selectSys1File(index)}
                                    onkeydown={(e) => handleOptionKeyDown(e, index, 'sys1')}
                                    role="option"
                                    tabindex="0"
                                    aria-selected={selectedSys1Index === index}
                                >
                                    {file.name}.{file.fileType}
                                </div>
                            {/each}
                        </div>
                    </div>
                    
                    <!-- System 2 -->
                    <div class="multiselect-widget">
                        <div class="widget-label">
                            <span class="system-number sys2">2</span>
                            System 2
                        </div>
                        <div 
                            class="custom-select"
                            onkeydown={handleSys2KeyDown}
                            tabindex="0"
                            role="listbox"
                            aria-label="System 2 files"
                        >
                            {#each availableFiles as file, index (file.id)}
                                <div 
                                    class="select-option {selectedSys2Index === index ? 'selected' : ''} {index === 1 ? 'auto-selected' : ''}"
                                    onclick={() => selectSys2File(index)}
                                    onkeydown={(e) => handleOptionKeyDown(e, index, 'sys2')}
                                    role="option"
                                    tabindex="0"
                                    aria-selected={selectedSys2Index === index}
                                >
                                    {file.name}.{file.fileType}
                                </div>
                            {/each}
                        </div>
                    </div>
                </div>
                
                <!-- Clear Button -->
                <div class="clear-section">
                    <Button.Root 
                        onclick={clearFiles}
                        variant="outline" 
                        size="sm"
                        class="clear-button"
                    >
                        Clear Files
                    </Button.Root>
                </div>
            {/if}
            
            <!-- Status Messages -->
            {#if uploadStatus}
                <div class="upload-status {uploadStatus.includes('Error') ? 'error' : 'success'}">
                    {uploadStatus}
                </div>
            {/if}
            
            {#if uploadWarnings.length > 0}
                <div class="upload-warnings">
                    <div class="warning-header">⚠️ Warnings:</div>
                    {#each uploadWarnings as warning}
                        <div class="warning-item">{warning}</div>
                    {/each}
                </div>
            {/if}
        </div>
    </div>
</div>

<style>
    .upload-container {
        width: 100%;
        margin-bottom: 0.5rem;
    }

    .upload-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        font-weight: 500;
        color: var(--color-text-primary);
        font-size: 0.9rem;
    }

    .upload-content {
        margin-top: 0.25rem;
    }

    .upload-section {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        margin-top: 0.5rem;
    }

    .file-count {
        background: var(--color-good-blue);
        color: white;
        padding: 0.125rem 0.375rem;
        border-radius: 10px;
        font-size: var(--11px);
        font-weight: 600;
        min-width: 1.25rem;
        text-align: center;
    }

    /* Drop Zone */
    .drop-zone {
        border: 1px dashed var(--color-border);
        border-radius: var(--border-radius);
        padding: 0.75rem;
        text-align: center;
        background-color: var(--color-input-bg);
        transition: all var(--transition-medium) ease;
        cursor: pointer;
    }

    .drop-zone:hover,
    .drop-zone.drag-over {
        border-color: var(--color-good-blue);
        background-color: rgba(0, 123, 255, 0.05);
    }

    .drop-zone:focus {
        outline: 2px solid var(--color-focus, #3b82f6);
        outline-offset: 2px;
        border-color: var(--color-good-blue);
    }

    .file-input-hidden {
        position: absolute;
        opacity: 0;
        pointer-events: none;
    }

    .drop-zone-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    .upload-icon {
        font-size: 1rem;
        opacity: 0.7;
    }

    .drop-text {
        font-size: var(--13px);
        color: var(--color-text-primary);
        margin: 0;
    }

    .browse-link {
        color: var(--color-good-blue);
        text-decoration: underline;
        background: none;
        border: none;
        cursor: pointer;
        font-size: inherit;
    }

    .upload-hint {
        font-size: var(--11px, 0.69rem);
        color: #999;
        margin: 0.5rem 0 0 0;
        text-align: center;
        font-style: italic;
    }

    /* Multi-Select Container */
    .multiselect-container {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .multiselect-widget {
        display: flex;
        flex-direction: column;
        gap: 0.375rem;
    }

    .widget-label {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: var(--13px);
        font-weight: var(--font-weight-medium);
        color: var(--color-text-primary);
    }

    .system-number {
        width: 1.25rem;
        height: 1.25rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: var(--10px);
        font-weight: var(--font-weight-bold);
        color: rgb(59, 59, 59);
    }

    .system-number.sys1 {
        background-color: rgb(230, 230, 230);
    }

    .system-number.sys2 {
        background-color: rgb(195, 230, 243);
    }

    /* Custom Select */
    .custom-select {
        width: 100%;
        height: 120px;
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius);
        background-color: var(--color-input-bg);
        color: var(--color-text-primary);
        font-family: var(--font-body);
        font-size: var(--12px);
        overflow-y: auto;
        cursor: pointer;
        display: flex;
        flex-direction: column;
    }

    .custom-select:focus {
        outline: 2px solid var(--color-good-blue);
        outline-offset: -2px;
        border-color: var(--color-good-blue);
    }

    .select-option {
        padding: 0.15rem 0.5rem;
        background-color: var(--color-input-bg);
        color: var(--color-text-primary);
        cursor: pointer;
        transition: background-color var(--transition-fast) ease;
        flex-shrink: 0;
    }

    .select-option:hover,
    .select-option:focus {
        background-color: rgba(0, 123, 255, 0.1);
        outline: none;
    }

    .select-option.selected {
        background-color: var(--color-good-blue);
        color: white;
    }

    .select-option.auto-selected {
        background-color: rgba(0, 123, 255, 0.2);
        font-weight: var(--font-weight-medium);
    }

    .select-option.selected.auto-selected {
        background-color: var(--color-good-blue);
        color: white;
    }

    /* Clear Section */
    .clear-section {
        display: flex;
        justify-content: center;
    }

    :global(.clear-button) {
        font-size: var(--12px);
        padding: 0.375rem 0.75rem;
        color: var(--color-text-secondary);
        border-color: var(--color-border);
    }

    :global(.clear-button:hover) {
        color: var(--color-red);
        border-color: var(--color-red);
    }

    /* Status Messages */
    .upload-status {
        font-size: var(--13px);
        padding: 0.5rem 0.75rem;
        border-radius: var(--border-radius);
        font-weight: var(--font-weight-normal);
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

    .upload-warnings {
        font-size: var(--12px);
        padding: 0.5rem 0.75rem;
        border-radius: var(--border-radius);
        background-color: rgba(255, 193, 7, 0.1);
        border: 1px solid var(--color-warning, #ffc107);
        color: var(--color-warning-text, #856404);
    }

    .warning-header {
        font-weight: var(--font-weight-medium);
        margin-bottom: 0.25rem;
    }

    .warning-item {
        margin-bottom: 0.125rem;
        padding-left: 0.75rem;
        font-size: var(--11px);
    }

    .warning-item:last-child {
        margin-bottom: 0;
    }
</style>