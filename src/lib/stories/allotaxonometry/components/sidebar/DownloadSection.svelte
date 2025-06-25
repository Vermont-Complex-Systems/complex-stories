<script>
    import { Accordion } from "bits-ui";
    
    function downloadAsPDF() {
        // Hide everything except the main content
        const sidebar = document.querySelector('.sidebar-container');
        const nav = document.querySelector('nav');
        
        if (sidebar) sidebar.style.display = 'none';
        if (nav) nav.style.display = 'none';
        
        // Trigger print dialog
        window.print();
        
        // Restore elements after print
        setTimeout(() => {
            if (sidebar) sidebar.style.display = '';
            if (nav) nav.style.display = '';
        }, 1000);
    }
</script>

<Accordion.Item value="download" class="accordion-item">
    <Accordion.Header>
        <Accordion.Trigger class="accordion-trigger">
            <span>⬇️ Download</span>
        </Accordion.Trigger>
    </Accordion.Header>
    <Accordion.Content class="accordion-content">
        <div class="download-section">
            <button class="download-button" onclick={downloadAsPDF}>
                Download as PDF
            </button>
        </div>
    </Accordion.Content>
</Accordion.Item>

<style>
    .download-section {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .download-button {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius);
        background-color: var(--color-good-blue);
        color: var(--color-white);
        font-size: var(--14px);
        font-family: var(--font-form);
        cursor: pointer;
        transition: all var(--transition-medium) ease;
        font-weight: var(--font-weight-bold);
    }

    .download-button:hover {
        background-color: var(--color-blue);
        transform: translateY(-1px);
    }

    /* Print styles to hide UI elements */
    @media print {
        :global(.sidebar-container),
        :global(nav),
        :global(.nav) {
            display: none !important;
        }
        
        :global(.main-content) {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        :global(.dashboard-app) {
            position: static !important;
        }
    }
</style>