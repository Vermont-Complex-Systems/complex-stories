<script>
    import ThemeToggle from './ThemeToggle.svelte';
    import { base } from "$app/paths";
    let { isDarkMode = $bindable(false) } = $props();
</script>

<div class="sticky-header">
    <div class="header-controls">
        <div class="logo-container">
            <a href="{base}/" class="logo-link">
                <img src="{base}/octopus-swim-left.png" alt="Home" class="logo" />
            </a>
        </div>
        
        <ThemeToggle bind:isDarkMode />
    </div>
</div>

<style>
     .sticky-header :global(button) {
        background: transparent !important;
        color: var(--dash-text-primary) !important;
        border: 1px solid var(--dash-border-color) !important;
        padding: 0.5rem !important;
    }

    .sticky-header :global(button:hover) {
        background: var(--dash-bg-secondary) !important;
    }

    .sticky-header {
        position: sticky;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        pointer-events: none;
        width: 100vw; /* Full viewport width */
        margin-left: calc(-50vw + 50%); /* Break out of any container */
        height: auto; /* Let content determine height */
    }

    .header-controls {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 1rem;
        pointer-events: auto;
        padding: 1rem 3.4rem 1rem 1rem;
        width: 100%;
        /* Removed absolute positioning */
    }

    .logo-container {
        max-width: 250px;
        transition: transform var(--transition-medium) ease;
        flex-shrink: 0; /* Prevent logo from shrinking */
    }

    .logo-container:hover {
        transform: rotate(var(--left-tilt)) scale(1.05);
    }

    .logo-link {
        display: block;
        border: none;
    }
    
    .logo {
        width: 100%;
        height: auto;
        border-radius: var(--border-radius);
        max-height: 3rem;
    }

    @media (max-width: 768px) {
        .header-controls {
            padding: 0.5rem;
            gap: 0.5rem;
        }
        
        .logo {
            max-height: 2.5rem;
        }
    }
</style>