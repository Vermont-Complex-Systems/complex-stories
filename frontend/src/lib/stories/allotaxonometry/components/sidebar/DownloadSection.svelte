<script>
  let { isDataReady = false } = $props();

  let showTooltip = $state(false);

    async function exportToPNG() {
    try {
      const domtoimage = (await import('dom-to-image-more')).default;
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
      const domtoimage = (await import('dom-to-image-more')).default;
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

<div class="download-section">
  <div class="section-header">
    <span class="section-label">Export Dashboard</span>
  </div>

  <div class="download-buttons">
    <button onclick={exportToPNG} disabled={!isDataReady} class="download-btn">
      <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
      Download PNG
    </button>
    <button onclick={exportToSVG} disabled={!isDataReady} class="download-btn">
      <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
      Download SVG
    </button>

    <div
      class="pdf-button-container"
      role="button"
      tabindex="0"
      onmouseenter={() => showTooltip = true}
      onmouseleave={() => showTooltip = false}
  >
      <button disabled={true} class="download-btn disabled-btn">
        📄 PDF (Limited)
      </button>

      {#if showTooltip}
      <div class="tooltip">
          Browser PDF export has poor quality. Download SVG and convert with Inkscape/Illustrator for publication-quality PDFs.
      </div>
      {/if}
    </div>
  </div>
</div>

<style>

  .section-header {
    margin-bottom: 0.5rem;
  }

  .icon {
    font-size: 1.2em;
  }

  .download-buttons {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .download-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    width: 100%;
    padding: 0.75rem 1rem;
    border: 1px solid var(--color-border);
    background-color: var(--color-bg);
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--color-text-primary);
    transition: all 0.15s ease;
  }

  .btn-icon {
    width: 1rem;
    height: 1rem;
    flex-shrink: 0;
  }

  .download-btn:hover:not(:disabled) {
    background-color: var(--color-input-bg);
    border-color: var(--color-good-blue, #3b82f6);
    box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.1);
  }

  .download-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .disabled-btn {
    cursor: help !important;
  }

  .pdf-button-container {
    position: relative;
  }

  .tooltip {
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    background: #333;
    color: white;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    font-size: 0.75rem;
    max-width: 250px;
    white-space: normal;
    z-index: 1000;
    margin-bottom: 0.5rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    line-height: 1.4;
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

  /* Mobile responsive */
  @media (max-width: 768px) {
    .download-btn {
      padding: 1rem;
      font-size: 1rem;
    }
  }
</style>