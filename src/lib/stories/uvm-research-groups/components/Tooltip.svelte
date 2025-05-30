<!-- Tooltip.svelte -->
<script>
  let { 
    visible = false,
    x = 0,
    y = 0,
    point = null,
    offset = { x: 15, y: -15 }
  } = $props();

  // Calculate tooltip position with smart positioning
  let tooltipX = $derived(x + offset.x);
  let tooltipY = $derived(y + offset.y);
</script>

{#if visible && point}
  <div 
    class="tooltip" 
    style="left: {tooltipX}px; top: {tooltipY}px;"
  >
    <div class="tooltip-header">
      <strong>{point.name}</strong>
      <span class="year">({point.year})</span>
    </div>
    <div class="tooltip-body">
      <div class="tooltip-row">
        <span class="label">Age difference:</span>
        <span class="value">{point.age_diff} years</span>
      </div>
      <div class="tooltip-row">
        <span class="label">Collaborations:</span>
        <span class="value">{point.collabs}</span>
      </div>
      {#if point.faculty}
        <div class="tooltip-row">
          <span class="label">Faculty:</span>
          <span class="value">{point.faculty}</span>
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  .tooltip {
    position: absolute;
    background: rgba(0, 0, 0, 0.92);
    color: white;
    padding: 0;
    border-radius: 8px;
    font-size: 12px;
    pointer-events: none;
    z-index: 1000;
    font-family: system-ui, sans-serif;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
    min-width: 200px;
    animation: fadeIn 0.2s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: scale(0.95);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }

  .tooltip-header {
    padding: 8px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px 8px 0 0;
  }

  .tooltip-header strong {
    color: #fff;
    font-weight: 600;
  }

  .year {
    color: #cbd5e0;
    font-weight: normal;
    margin-left: 4px;
  }

  .tooltip-body {
    padding: 8px 12px;
  }

  .tooltip-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 4px 0;
  }

  .label {
    color: #a0aec0;
    font-size: 11px;
  }

  .value {
    color: #fff;
    font-weight: 500;
    font-size: 11px;
  }

  /* Add arrow pointing to the circle */
  .tooltip::before {
    content: '';
    position: absolute;
    left: -6px;
    top: 50%;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-top: 6px solid transparent;
    border-bottom: 6px solid transparent;
    border-right: 6px solid rgba(0, 0, 0, 0.92);
  }
</style>