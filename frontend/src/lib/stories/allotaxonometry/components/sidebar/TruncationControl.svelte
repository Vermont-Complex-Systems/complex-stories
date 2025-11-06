<!-- sidebar/TruncationControl.svelte -->
<script>
    import { Accordion, Button } from "bits-ui";
    
    let { truncationSettings = $bindable() } = $props();
    let showSettingsChanged = $state(false);

    $effect(() => {
        // When settings change, show a temporary message
        truncationSettings.enabled;
        truncationSettings.maxRows;
        
        showSettingsChanged = true;
        setTimeout(() => showSettingsChanged = false, 3000);
    });
</script>

<Accordion.Item value="settings" class="accordion-item">
    <Accordion.Header>
        <Accordion.Trigger class="accordion-trigger">
            <span>⚙️ Data Processing</span>
        </Accordion.Trigger>
    </Accordion.Header>
    <Accordion.Content class="accordion-content">
        <div class="settings-section">
            <div class="setting-item">
                <label class="toggle-label">
                    <input 
                        type="checkbox" 
                        bind:checked={truncationSettings.enabled}
                        class="toggle-input"
                    />
                    <span class="toggle-text">
                        Auto-truncate large datasets
                    </span>
                </label>
                <p class="setting-description">
                    {#if truncationSettings.enabled}
                        Automatically keeps top {truncationSettings.maxRows.toLocaleString()} most frequent items for better performance
                    {:else}
                        Process all data (may be slow for large files)
                    {/if}
                </p>
            </div>
            
            {#if truncationSettings.enabled}
                <div class="setting-item">
                    <label for="maxRows" class="input-label">Max items to process:</label>
                    <input 
                        id="maxRows"
                        type="number" 
                        bind:value={truncationSettings.maxRows}
                        min="1000"
                        max="50000"
                        step="1000"
                        class="number-input"
                    />
                </div>
            {/if}
        </div>
    </Accordion.Content>
</Accordion.Item>