<script>
  let { 
    visible = false, 
    x = 0, 
    y = 0, 
    content = '',
    offset = { x: 10, y: -30 }
  } = $props();
</script>

{#if visible}
  <div 
    class="tooltip" 
    style="left: {x + offset.x}px; top: {y + offset.y}px;"
  >
    {content}
  </div>
{/if}

<style>
  .tooltip {
    position: fixed;
    background: var(--color-bg);
    color: var(--color-fg);
    border: 1px solid var(--color-border);
    padding: 0.75rem 1rem; /* More generous padding */
    border-radius: var(--border-radius);
    font-size: var(--font-size-small);
    font-family: var(--sans);
    white-space: pre-line;
    line-height: 1.4;
    pointer-events: none;
    z-index: var(--z-overlay);
    max-width: 300px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: opacity var(--transition-fast);
  }

  :global(.dark) .tooltip {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }
</style>