<script>
  import { Accordion } from "bits-ui";
  import domtoimage from 'dom-to-image-more';

  let { isDataReady = false } = $props();
  
  let showTooltip = $state(false);

    async function exportToPNG() {
    try {
      const dashboard = document.getElementById('allotaxonometer-dashboard');
      
      // Scroll to top to ensure full visibility
      window.scrollTo(0, 0);
      
      // Get computed dimensions including any overflow
      const rect = dashboard.getBoundingClientRect();
      const computedStyle = getComputedStyle(dashboard);
      
      // Use scrollWidth/Height for full content size
      const fullWidth = Math.max(rect.width, dashboard.scrollWidth);
      const fullHeight = Math.max(rect.height, dashboard.scrollHeight);
      
      const dataUrl = await domtoimage.toPng(dashboard, {
        quality: 1.0,
        bgcolor: 'white',
        scale: 2,
        width: fullWidth,   // Use full content width
        height: fullHeight, // Use full content height
        style: {
          // Ensure no clipping
          overflow: 'visible',
          position: 'static',
          transform: 'none',
          // Force the element to show its full size
          width: fullWidth + 'px',
          height: fullHeight + 'px'
        }
      });
      
      const link = document.createElement('a');
      link.download = 'dashboard.png';
      link.href = dataUrl;
      link.click();
    } catch (error) {
      console.error('PNG export failed:', error);
    }
  }


  async function exportToSVG() {
    try {
      const dashboard = document.getElementById('allotaxonometer-dashboard');
      const dataUrl = await domtoimage.toSvg(dashboard);
      
      const link = document.createElement('a');
      link.download = 'dashboard.svg';
      link.href = dataUrl;
      link.click();
    } catch (error) {
      console.error('SVG export failed:', error);
    }
  }
</script>

<Accordion.Item value="download">
  <Accordion.Header>
    <Accordion.Trigger class="section-trigger">
      <div class="section-header">
        <div class="icon">📥</div>
        <span>Export</span>
      </div>
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M6 9l6 6 6-6"/>
      </svg>
    </Accordion.Trigger>
  </Accordion.Header>
  
  <Accordion.Content class="section-content">
    <div class="download-section">
      <button onclick={exportToPNG} disabled={!isDataReady}>
        Download PNG
      </button>
      <button onclick={exportToSVG} disabled={!isDataReady}>
        Download SVG  
      </button>
      
      <div 
        class="pdf-button-container"
        onmouseenter={() => showTooltip = true}
        onmouseleave={() => showTooltip = false}
    >
        <button disabled={true}>
        📄 PDF (Limited by Browser)
        </button>

        {#if showTooltip}
        <div class="tooltip">
            Browser PDF export has poor quality. Download SVG and convert with Inkscape/Illustrator for publication-quality PDFs.
        </div>
        {/if}
      </div>
    </div>
  </Accordion.Content>
</Accordion.Item>

<style>

  .section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .icon {
    font-size: 1.2em;
  }

  .download-section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  button {
    padding: 0.5rem 1rem;
    border: 1px solid var(--color-border);
    background: var(--color-bg);
    border-radius: var(--border-radius);
    cursor: pointer;
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    color: var(--color-fg);
    transition: all var(--transition-medium) ease;
    width: 100%; /* Make button fill container */
  }
  
  button:hover:not(:disabled) {
    background: var(--color-gray-100);
    border-color: var(--color-gray-300);
  }

  button:disabled {
    opacity: 0.5;
    cursor: help; /* Change cursor to indicate hoverable */
  }

  :global(.dark) button {
    background: var(--color-gray-800);
    border-color: var(--color-gray-600);
  }

  :global(.dark) button:hover:not(:disabled) {
    background: var(--color-gray-700);
    border-color: var(--color-gray-500);
  }

  .pdf-button-container {
    position: relative;
    cursor: help; /* Show help cursor on container */
  }
  
  .tooltip {
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    background: #333;
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 12px;
    max-width: 250px;
    white-space: normal;
    z-index: 1000;
    margin-bottom: 5px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  }
  
  .tooltip::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 5px solid transparent;
    border-top-color: #333;
  }
</style>