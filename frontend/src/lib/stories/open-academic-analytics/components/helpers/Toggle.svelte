<script>
    import { Toggle } from "bits-ui";

    let { isTrue = $bindable() } = $props();
</script>

<Toggle.Root bind:pressed={isTrue} class="simple-toggle">
    <span>{isTrue ? 'On' : 'Off'}</span>
    <div class="toggle-switch">
        <div class="toggle-knob"></div>
    </div>
</Toggle.Root>

<style>
    :global(.simple-toggle) {
        display: flex !important;
        align-items: center;
        gap: 0.5rem;
        padding: 0.25rem 0.5rem;
        border: 1px solid #ccc;
        border-radius: 0.25rem;
        background: white;
        cursor: pointer;
        font-size: 0.75rem;
    }

    :global(.simple-toggle[data-state="on"]) {
        background: #3b82f6;
        color: white;
        border-color: #3b82f6;
    }

    .toggle-switch {
        position: relative;
        width: 1.5rem;
        height: 0.75rem;
        background: #e5e7eb;
        border-radius: 9999px;
        transition: background-color 200ms;
    }

    :global(.simple-toggle[data-state="on"]) .toggle-switch {
        background: #1e40af;
    }

    .toggle-knob {
        position: absolute;
        top: 0.05rem;
        left: 0.05rem;
        width: 0.65rem;
        height: 0.65rem;
        background: white;
        border-radius: 50%;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        transition: transform 200ms;
    }

    :global(.simple-toggle[data-state="on"]) .toggle-knob {
        transform: translateX(0.75rem);
    }
</style>