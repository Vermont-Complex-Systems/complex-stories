<script>
  let { 
    legendItems = [],
    visible = true 
  } = $props();
</script>

<div class="legend" class:visible>
  <div class="legend-content">
    <div class="legend-title">Legend</div>
    
    <div class="legend-items">
      {#each legendItems as item, i}
        <div 
          class="legend-item" 
          style="animation-delay: {i * 0.1}s"
        >
          <div 
            class="legend-dot" 
            style="background: {item.color};"
          ></div>
          <span>{item.label}</span>
        </div>
      {/each}
    </div>
  </div>
</div>

<style>
  .legend {
    background: var(--step-bg);
    border: 1px solid var(--color-border, #ddd);
    border-radius: 8px;
    padding: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    font-size: 11px;
    backdrop-filter: blur(10px);
    min-width: 180px;
    max-width: 220px;

    /* Transition properties */
    opacity: 0;
    transform: translateY(-10px);
    transition: opacity 0.6s ease, transform 0.6s ease;
  }

  /* Mobile-specific legend styling */
  @media (max-width: 480px) {
    .legend {
      min-width: 160px;
      max-width: 100%;
      width: auto;
      padding: 10px;
      font-size: 10px;
    }

    .legend-items {
      gap: 4px;
    }

    .legend-item {
      margin-bottom: 2px;
    }

    .legend-item span {
      font-size: 9px;
      word-break: normal;
      overflow-wrap: anywhere;
    }
  }

  .legend.visible {
    opacity: 1;
    transform: translateY(0);
  }

  .legend-content {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .legend-title {
    font-weight: bold;
    font-size: 12px;
    color: var(--color-text, var(--step-bg));
    margin-bottom: 4px;
    text-align: center;
    border-bottom: 1px solid var(--color-border, #eee);
    padding-bottom: 4px;
  }

  .legend-items {
    display: flex;
    flex-direction: column;
    gap: 6px;
    max-height: 300px;
    overflow-y: auto;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
    opacity: 0;
    transform: translateX(10px);
    animation: slideIn 0.4s ease forwards;
  }

  .legend-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    border: 1px solid rgba(0, 0, 0, 0.3);
    flex-shrink: 0;
    transition: background-color 0.4s ease;
  }

  .legend-item span {
    font-size: 10px;
    color: var(--color-text, var(--step-bg));
    line-height: 1.2;
    word-break: break-word;
  }

  @keyframes slideIn {
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
</style>