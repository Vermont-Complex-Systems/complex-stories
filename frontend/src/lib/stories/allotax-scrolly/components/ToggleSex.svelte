<script>
    import { Toggle } from "bits-ui";

    let { isGirls = $bindable() } = $props();
</script>

<div class="data-toggle-wrapper">
    <Toggle.Root bind:pressed={isGirls} class="data-toggle">
        <span class="toggle-label">{isGirls ? 'Girls' : 'Boys'}</span>
        <div class="toggle-switch">
            <div class="toggle-knob"></div>
        </div>
    </Toggle.Root>
</div>

<style>
    .data-toggle-wrapper {
        display: flex;
        align-items: center;
    }

    /* Modern toggle styling */
    :global(.data-toggle) {
        display: flex !important;
        align-items: center;
        gap: 0.75rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        color: var(--color-fg, #333) !important;
        cursor: pointer;
        padding: 0.6rem 0.9rem !important;
        border-radius: 2rem;
        transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 0.8rem;
        font-weight: 500;
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.1),
            0 2px 4px -1px rgba(0, 0, 0, 0.06);
        min-width: auto;
        width: auto;
        height: auto;
    }

    /* Background colors based on state */
    :global(.data-toggle[data-state="on"]) {
        background: rgba(236, 72, 153, 0.15) !important; /* Light pink background for girls */
        color: #be185d !important; /* Darker pink text */
    }

    :global(.data-toggle[data-state="off"]) {
        background: rgba(59, 130, 246, 0.15) !important; /* Light blue background for boys */
        color: #1e40af !important; /* Darker blue text */
    }

    /* Default state (if neither on nor off) */
    :global(.data-toggle:not([data-state="on"]):not([data-state="off"])) {
        background: rgba(255, 255, 255, 0.95) !important;
    }

    /* Hover effects - make backgrounds more transparent */
    :global(.data-toggle[data-state="on"]:hover) {
        background: rgba(236, 72, 153, 0.08) !important; /* More transparent pink on hover */
    }

    :global(.data-toggle[data-state="off"]:hover) {
        background: rgba(59, 130, 246, 0.08) !important; /* More transparent blue on hover */
    }

    :global(.data-toggle:not([data-state="on"]):not([data-state="off"]):hover) {
        background: rgba(255, 255, 255, 0.7) !important;
    }

    /* Toggle switch styles */
    .toggle-switch {
        position: relative;
        width: 2.2rem;
        height: 1.1rem;
        background: #e5e7eb;
        border-radius: 9999px;
        transition: background-color 200ms;
    }

    /* Switch colors */
    :global(.data-toggle[data-state="on"]) .toggle-switch {
        background: #ec4899; /* Pink for girls */
    }

    :global(.data-toggle[data-state="off"]) .toggle-switch {
        background: #3b82f6; /* Blue for boys */
    }

    .toggle-knob {
        position: absolute;
        top: 0.1rem;
        left: 0.1rem;
        width: 0.9rem;
        height: 0.9rem;
        background: white;
        border-radius: 50%;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: transform 200ms;
    }

    :global(.data-toggle[data-state="on"]) .toggle-knob {
        transform: translateX(1.1rem);
    }

    .toggle-label {
        font-family: var(--sans, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif);
        white-space: nowrap;
        font-weight: 600;
    }

    /* Dark mode support */
    :global(.dark .data-toggle[data-state="on"]) {
        background: rgba(236, 72, 153, 0.2) !important;
        border: 1px solid rgba(236, 72, 153, 0.3) !important;
        color: #fbb6ce !important;
    }

    :global(.dark .data-toggle[data-state="off"]) {
        background: rgba(59, 130, 246, 0.2) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        color: #93c5fd !important;
    }

    :global(.dark .data-toggle:not([data-state="on"]):not([data-state="off"])) {
        background: rgba(30, 30, 30, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #f3f4f6 !important;
    }

    /* Dark mode hover effects */
    :global(.dark .data-toggle[data-state="on"]:hover) {
        background: rgba(236, 72, 153, 0.1) !important;
    }

    :global(.dark .data-toggle[data-state="off"]:hover) {
        background: rgba(59, 130, 246, 0.1) !important;
    }

    :global(.dark .data-toggle:not([data-state="on"]):not([data-state="off"]):hover) {
        background: rgba(30, 30, 30, 0.7) !important;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        :global(.data-toggle) {
            padding: 0.4rem 0.6rem !important;
            font-size: 0.75rem;
            gap: 0.5rem;
        }
        
        .toggle-switch {
            width: 1.8rem;
            height: 0.9rem;
        }
        
        .toggle-knob {
            width: 0.7rem;
            height: 0.7rem;
        }
        
        :global(.data-toggle[data-state="on"]) .toggle-knob {
            transform: translateX(0.9rem);
        }
    }
</style>