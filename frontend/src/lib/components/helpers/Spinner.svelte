<script>
  let { text = "Loading..." } = $props();
</script>

<div class="loading-container">
  <div class="spinner"></div>
  <span class="loading-text">{text}</span>
</div>

<style>
  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 300px;
    gap: 1rem;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid var(--color-primary, #007acc);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  .loading-text {
    font-family: var(--serif);
    font-size: 1.1rem;
    color: var(--color-gray-600);
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
</style>