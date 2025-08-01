<script>
  import { Button } from "bits-ui";
  import { X, BookOpen, ExternalLink } from "@lucide/svelte";
  import { base } from '$app/paths';
  
  let { visible = $bindable(false) } = $props();
  
  function closeTutorial() {
    visible = false;
    // Store in localStorage so it doesn't show again
    localStorage.setItem('tutorial-popup-dismissed', 'true');
  }
  
  function goToTutorial() {
    window.open(`${base}/uvm-research-groups`, '_blank');
    closeTutorial();
  }
  
  // Handle keyboard events for backdrop
  function handleBackdropKeydown(event) {
    if (event.key === 'Escape') {
      closeTutorial();
    }
  }
  
  // Check if user has already dismissed this
  let shouldShow = $derived.by(() => {
    if (typeof window === 'undefined') return false;
    return visible && !localStorage.getItem('tutorial-popup-dismissed');
  });
</script>

{#if shouldShow}
  <!-- Backdrop with proper accessibility -->
  <div 
    class="popup-backdrop" 
    onclick={closeTutorial}
    onkeydown={handleBackdropKeydown}
    role="button"
    tabindex="0"
    aria-label="Close tutorial popup"
  ></div>
  
  <!-- Popup Modal -->
  <div class="popup-modal" role="dialog" aria-labelledby="tutorial-title" aria-describedby="tutorial-description" aria-modal="true">
    <div class="popup-header">
      <div class="popup-title-section">
        <BookOpen size={20} />
        <h2 id="tutorial-title">Welcome to Open Academic Analytics!</h2>
      </div>
      <Button.Root onclick={closeTutorial} variant="ghost" size="sm" class="close-button" aria-label="Close tutorial">
        <X size={16} />
      </Button.Root>
    </div>
    
    <div class="popup-content">
      <p id="tutorial-description">
        New to this dashboard? Check out our interactive tutorial to learn how to explore 
        faculty research collaborations, analyze publication patterns, and discover insights 
        in the academic data.
      </p>
      
      <div class="popup-actions">
        <Button.Root onclick={goToTutorial} class="tutorial-button">
          <BookOpen size={16} />
          View Tutorial
          <ExternalLink size={14} />
        </Button.Root>
        
        <Button.Root onclick={closeTutorial} variant="outline" class="dismiss-button">
          Dismiss
        </Button.Root>
      </div>
    </div>
  </div>
{/if}

<style>
  .popup-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1000;
    backdrop-filter: blur(2px);
    cursor: pointer;
  }
  
  .popup-backdrop:focus {
    outline: 2px solid var(--color-focus, #3b82f6);
    outline-offset: -2px;
  }
  
  .popup-modal {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius-lg, 12px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    z-index: 1001;
    width: 90%;
    max-width: 480px;
    max-height: 90vh;
    overflow: hidden;
  }
  
  .popup-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem;
    border-bottom: 1px solid var(--color-border);
    background: var(--color-gray-50);
  }
  
  :global(.dark) .popup-header {
    background: var(--color-gray-800);
  }
  
  .popup-title-section {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  
  .popup-title-section h2 {
    margin: 0;
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    color: var(--color-fg);
  }
  
  .popup-content {
    padding: 1.5rem;
  }
  
  .popup-content p {
    margin: 0 0 1.5rem 0;
    color: var(--color-secondary-gray);
    line-height: 1.5;
    font-size: var(--font-size-base);
  }
  
  .popup-actions {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
  }
  
  :global(.tutorial-button) {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--color-good-blue);
    color: white;
    padding: 0.75rem 1.25rem;
    border-radius: var(--border-radius);
    font-weight: var(--font-weight-medium);
    transition: background-color var(--transition-medium) ease;
    flex: 1;
    justify-content: center;
  }
  
  :global(.tutorial-button:hover) {
    background: var(--color-good-blue-hover, #2563eb);
  }
  
  :global(.dismiss-button) {
    padding: 0.75rem 1.25rem;
    flex-shrink: 0;
  }
  
  :global(.close-button) {
    padding: 0.5rem;
  }
  
  /* Mobile responsive */
  @media (max-width: 640px) {
    .popup-modal {
      width: 95%;
      margin: 1rem;
    }
    
    .popup-header {
      padding: 1rem;
    }
    
    .popup-content {
      padding: 1rem;
    }
    
    .popup-title-section h2 {
      font-size: var(--font-size-base);
    }
    
    .popup-actions {
      flex-direction: column;
    }
    
    :global(.dismiss-button) {
      flex: 1;
    }
  }
</style>