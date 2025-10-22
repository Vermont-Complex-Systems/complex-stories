<script>
  import { innerWidth } from 'svelte/reactivity/window';
  
  let { 
    value = $bindable(),
    options = [],
    label = null,
    maxWidthRatio = 0.3, // Use 30% of window width by default
    minWidth = 200
  } = $props();

  // Calculate responsive width
  let selectWidth = $derived(
    Math.max(minWidth, (innerWidth.current || 800) * maxWidthRatio)
  );
</script>

<div class="select-container" style="width: {selectWidth}px;">
  {#if label}
    <label class="select-label">{label}</label>
  {/if}
  <select bind:value class="styled-select">
    {#each options as option}
      <option value={option.value}>{option.label}</option>
    {/each}
  </select>
</div>

<style>
  .select-container {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin: 0 0 5px 0;
  }

  .select-label {
    font-size: 14px;
    font-weight: 500;
    color: var(--color-fg);
    margin-bottom: 2px;
  }

  .styled-select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid var(--color-border);
    border-radius: 6px;
    background: var(--color-bg);
    color: var(--color-fg);
    font-size: 14px;
    font-family: system-ui, -apple-system, sans-serif;
    cursor: pointer;
    transition: all 0.2s ease;
    appearance: none;
    background-image: url("data:image/svg+xml;charset=utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 8L2 4h8z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 12px center;
    background-size: 12px;
    padding-right: 36px;
  }

  .styled-select:hover {
    border-color: var(--color-border-hover, #999);
    background-color: var(--color-bg-hover, rgba(0, 0, 0, 0.02));
  }

  .styled-select:focus {
    outline: none;
    border-color: var(--color-accent, #0066cc);
    box-shadow: 0 0 0 2px var(--color-accent-alpha, rgba(0, 102, 204, 0.2));
  }

  .styled-select option {
    padding: 8px;
    background: var(--color-bg);
    color: var(--color-fg);
  }

  /* Dark mode adjustments */
  :global(.dark) .styled-select {
    background-image: url("data:image/svg+xml;charset=utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23ccc' d='M6 8L2 4h8z'/%3E%3C/svg%3E");
  }

  :global(.dark) .styled-select:hover {
    background-color: var(--color-bg-hover, rgba(255, 255, 255, 0.05));
  }
</style>