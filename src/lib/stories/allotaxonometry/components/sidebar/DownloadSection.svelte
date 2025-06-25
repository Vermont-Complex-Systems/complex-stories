<script>
    import { Accordion, Button } from "bits-ui";

    let {
        // Original props
        sys1,
        sys2,
        alpha,
        title = ['System 1', 'System 2'],
        topN = 30,
        isDataReady = false,
        class: className = '',
        
        // New props for pre-computed data
        me = null,
        rtd = null, 
        dat = null,
        barData = [],
        balanceData = [],
        maxlog10 = 0,
        max_count_log = 2,
        max_shift = 1
    } = $props();

    // Add validation and logging
    $effect(() => {
        console.log('DownloadSection props:', { 
            sys1: sys1 ? 'present' : 'missing', 
            sys2: sys2 ? 'present' : 'missing', 
            alpha, 
            title, 
            topN,
            dat: dat ? 'present' : 'missing',
            barDataLength: barData.length,
            alphaType: typeof alpha,
            alphaIsInfinity: alpha === Infinity,
            alphaIsNaN: isNaN(alpha)
        });
    });

    // Export state
    let exporting = $state(false);
    let exportProgress = $state('');
    let lastExportType = $state('');

    async function exportFile(format = 'pdf') {
        console.log('exportFile called with:', { format, alpha, alphaType: typeof alpha });
        
        if (!sys1 || !sys2) {
            alert('No data to export');
            return;
        }

        if (!dat || !rtd) {
            alert('Data not ready for export. Please wait for processing to complete.');
            return;
        }

        // Validate alpha before proceeding
        if (alpha === null || alpha === undefined) {
            alert('Invalid alpha value: null or undefined');
            return;
        }

        if (isNaN(alpha) && alpha !== Infinity) {
            alert('Invalid alpha value: NaN');
            return;
        }
        
        exporting = true;
        lastExportType = format;
        exportProgress = 'Preparing data...';
        
        try {
            exportProgress = 'Processing visualization...';
            
            // Handle Infinity serialization
            const alphaForJSON = alpha === Infinity ? 'Infinity' : alpha;
            
            console.log('Sending pre-computed data to API:', {
                alpha: alphaForJSON,
                title1: title[0],
                title2: title[1],
                format,
                topN,
                datPresent: !!dat,
                rtdPresent: !!rtd,
                barDataLength: barData.length
            });
            
            const response = await fetch('/api/export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    // Send pre-computed data instead of raw data
                    dat,
                    rtd,
                    barData: barData.slice(0, topN),
                    balanceData,
                    maxlog10,
                    max_count_log,
                    max_shift,
                    alpha: alphaForJSON,
                    title1: title[0],
                    title2: title[1],
                    format
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Export failed');
            }
            
            exportProgress = 'Downloading file...';
            
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            // Set filename based on format and titles
            const sanitizedTitle1 = title[0].replace(/[^a-zA-Z0-9]/g, '_');
            const sanitizedTitle2 = title[1].replace(/[^a-zA-Z0-9]/g, '_');
            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
            
            a.download = `${sanitizedTitle1}_vs_${sanitizedTitle2}_alpha${alphaForJSON}_${timestamp}.${format}`;
            
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            exportProgress = 'Complete!';
            setTimeout(() => {
                exportProgress = '';
                lastExportType = '';
            }, 1000);
            
        } catch (error) {
            console.error('Export failed:', error);
            alert(`Export failed: ${error.message}`);
            exportProgress = '';
            lastExportType = '';
        } finally {
            exporting = false;
        }
    }

    // Updated computed properties for button states
    let canExport = $derived(isDataReady && sys1 && sys2 && dat && rtd && !exporting);
    let progressMessage = $derived(
        exporting ? `${exportProgress} (${lastExportType.toUpperCase()})` : exportProgress
    );
</script>

<Accordion.Item value="download" class="accordion-item">
    <Accordion.Header>
        <Accordion.Trigger class="accordion-trigger">
            <span>💾 Export Dashboard</span>
        </Accordion.Trigger>
    </Accordion.Header>
    <Accordion.Content class="accordion-content">
        <div class="download-section">
            <div class="export-grid">
                <Button.Root 
                    onclick={() => exportFile('pdf')}
                    disabled={!canExport}
                    variant="default"
                    size="sm"
                    class="export-button"
                >
                    📄 PDF
                </Button.Root>

                <Button.Root 
                    onclick={() => exportFile('html')}
                    disabled={!canExport}
                    variant="outline"
                    size="sm"
                    class="export-button"
                >
                    🌐 HTML
                </Button.Root>

                <Button.Root 
                    onclick={() => exportFile('rtd-json')}
                    disabled={!canExport}
                    variant="outline"
                    size="sm"
                    class="export-button"
                >
                    📊 Data
                </Button.Root>
            </div>

            {#if exportProgress}
                <div class="export-status {exportProgress.startsWith('Error') ? 'error' : 'success'}">
                    {exportProgress}
                </div>
            {/if}

            {#if !canExport && !disabled}
                <div class="export-help">
                    {!dat || !rtd ? 'Processing data...' : 'Upload data to enable exports'}
                </div>
            {/if}
        </div>
    </Accordion.Content>
</Accordion.Item>

<style>
    .download-section {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-top: 1rem;
    }

    .export-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 0.5rem;
    }

    :global(.export-button) {
        font-size: var(--12px) !important;
        padding: 0.5rem 0.25rem !important;
        font-family: var(--font-form) !important;
        height: auto !important;
    }

    .export-status {
        font-size: var(--14px);
        padding: 0.75rem;
        border-radius: var(--border-radius);
        font-weight: var(--font-weight-normal);
        font-family: var(--font-form);
        text-align: center;
    }

    .export-status.success {
        color: var(--color-electric-green);
        background-color: rgba(58, 230, 96, 0.1);
        border: 1px solid var(--color-electric-green);
    }

    .export-status.error {
        color: var(--color-red);
        background-color: rgba(255, 83, 61, 0.1);
        border: 1px solid var(--color-red);
    }

    .export-help {
        font-size: var(--12px);
        color: var(--color-secondary-gray);
        text-align: center;
        font-family: var(--font-form);
        font-style: italic;
    }
</style>