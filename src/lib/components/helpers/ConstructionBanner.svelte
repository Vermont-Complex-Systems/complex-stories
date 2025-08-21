<script>
  import { AlertTriangle } from "@lucide/svelte";
  
  let {
    message = "Website Under Construction",
    position = "top-right", // "top-right" | "top-left" | "top-center"
    variant = "warning", // "warning" | "info" | "danger"
    showIcon = true,
    animate = true
  } = $props();

  // Position classes
  const positionClasses = {
    "top-right": "top-right",
    "top-left": "top-left", 
    "top-center": "top-center"
  };

  // Variant styles
  const variants = {
    warning: {
      bg: "#fbbf24",
      text: "#92400e", 
      border: "#f59e0b",
      darkBg: "#d97706",
      darkText: "#fef3c7"
    },
    info: {
      bg: "#60a5fa",
      text: "#1e40af",
      border: "#3b82f6", 
      darkBg: "#3b82f6",
      darkText: "#dbeafe"
    },
    danger: {
      bg: "#f87171",
      text: "#991b1b",
      border: "#ef4444",
      darkBg: "#dc2626", 
      darkText: "#fecaca"
    }
  };

  let currentVariant = $derived(variants[variant] || variants.warning);
  let positionClass = $derived(positionClasses[position] || "top-right");
</script>

<div 
  class="construction-banner {positionClass}"
  class:animate
  style="
    --banner-bg: {currentVariant.bg};
    --banner-text: {currentVariant.text};
    --banner-border: {currentVariant.border};
    --banner-dark-bg: {currentVariant.darkBg};
    --banner-dark-text: {currentVariant.darkText};
  "
>
  {#if showIcon}
    <AlertTriangle size={78} />
  {/if}
  <span>{message}</span>
</div>

<style>
  .construction-banner {
    position: fixed;
    z-index: calc(var(--z-overlay));
    
    display: flex;
    align-items: center;
    gap: 0.5rem;
    
    background: var(--banner-bg);
    color: var(--banner-text);
    border: 2px solid var(--banner-border);
    border-radius: 0.5rem;
    padding: 0.5rem 1rem;
    
    font-family: var(--sans);
    font-size: var(--font-size-xsmall);
    font-weight: var(--font-weight-bold);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    backdrop-filter: blur(8px);
    
    /* Add rotation */
    transform: rotate(10deg);
    transform-origin: center;
  }

  /* Position variants - adjusted positioning */
  .top-right {
    top: 6rem; /* Moved down from 1rem */
    right: 6rem; /* Moved left from 1rem */
  }

  .top-left {
    top: 3rem; /* Moved down from 1rem */
    left: 1rem;
  }

  .top-center {
    top: 3rem; /* Moved down from 1rem */
    left: 50%;
    transform: translateX(-50%) rotate(3deg); /* Combined transforms */
  }

  /* Animation - updated to preserve rotation */
  .animate {
    animation: bannerPulse 2s ease-in-out infinite;
  }

  @keyframes bannerPulse {
    0%, 100% { 
      transform: rotate(10deg) scale(1);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    50% { 
      transform: rotate(10deg) scale(1.02);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
    }
  }

  /* Center position animation adjustment */
  .top-center.animate {
    animation: bannerPulseCenter 2s ease-in-out infinite;
  }

  @keyframes bannerPulseCenter {
    0%, 100% { 
      transform: translateX(-50%) rotate(10deg) scale(1);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    50% { 
      transform: translateX(-50%) rotate(10deg) scale(1.02);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
    }
  }

  /* Dark mode */
  :global(.dark) .construction-banner {
    background: var(--banner-dark-bg);
    color: var(--banner-dark-text);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }

  /* Mobile responsive - adjusted positioning */
  @media (max-width: 768px) {
    .construction-banner {
      top: 2rem; /* Moved down from 0.5rem */
      padding: 0.375rem 0.75rem;
      font-size: 10px;
      gap: 0.25rem;
    }

    .top-left {
      left: 0.5rem;
    }

    .top-right {
      right: 1rem; /* Moved left from 0.5rem */
    }
  }

  /* Very small screens */
  @media (max-width: 480px) {
    .construction-banner {
      top: 1.5rem; /* Moved down from 0.25rem */
      padding: 0.25rem 0.5rem;
      font-size: 9px;
    }

    .top-left {
      left: 0.25rem;
    }

    .top-right {
      right: 0.75rem; /* Moved left from 0.25rem */
    }
  }

  /* Accessibility - respect reduced motion */
  @media (prefers-reduced-motion: reduce) {
    .construction-banner {
      animation: none !important;
      /* Keep rotation but remove animation for reduced motion users */
      transform: rotate(10deg) !important;
    }
    
    .top-center {
      transform: translateX(-50%) rotate(10deg) !important;
    }
  }
</style>