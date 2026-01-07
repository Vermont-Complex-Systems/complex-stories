<script>
    import { Toggle } from "bits-ui";

    let { sex = $bindable('M') } = $props();

    // Convert between boolean and 'M'/'F' string
    const isFemale = $derived(sex === 'F');

    function handleToggle(pressed) {
        sex = pressed ? 'F' : 'M';
    }
</script>

<div class="sex-toggle-wrapper">
    <Toggle.Root pressed={isFemale} onPressedChange={handleToggle} class="sex-toggle">
        <span class="toggle-label">{isFemale ? 'Girls' : 'Boys'}</span>
        <div class="toggle-switch">
            <div class="toggle-knob"></div>
        </div>
    </Toggle.Root>
</div>

<style>
    .sex-toggle-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.5rem 0;
    }

    /* Modern toggle styling */
    :global(.sex-toggle) {
        display: flex !important;
        align-items: center;
        gap: 0.75rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        color: var(--color-text, #333) !important;
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
    :global(.sex-toggle[data-state="on"]) {
        background: rgba(236, 72, 153, 0.15) !important; /* Light pink background for girls */
        color: #be185d !important; /* Darker pink text */
    }

    :global(.sex-toggle[data-state="off"]) {
        background: rgba(59, 130, 246, 0.15) !important; /* Light blue background for boys */
        color: #6789f8 !important; /* Darker blue text */
    }

    /* Hover effects */
    :global(.sex-toggle[data-state="on"]:hover) {
        background: rgba(236, 72, 153, 0.25) !important;
    }

    :global(.sex-toggle[data-state="off"]:hover) {
        background: rgba(112, 163, 246, 0.833)tant;
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
    :global(.sex-toggle[data-state="on"]) .toggle-switch {
        background: #ec4899; /* Pink for girls */
    }

    :global(.sex-toggle[data-state="off"]) .toggle-switch {
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

    :global(.sex-toggle[data-state="on"]) .toggle-knob {
        transform: translateX(1.1rem);
    }

    .toggle-label {
        font-family: var(--sans, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif);
        white-space: nowrap;
        font-weight: 600;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        :global(.sex-toggle) {
            padding: 0.5rem 0.75rem !important;
            font-size: 0.875rem;
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

        :global(.sex-toggle[data-state="on"]) .toggle-knob {
            transform: translateX(0.9rem);
        }
    }
</style>
