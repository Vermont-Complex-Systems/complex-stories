<script>
    import { base } from '$app/paths';
    import ThemeToggle from './ThemeToggle.svelte';
</script>

<nav class="nav">
    <div class="logo-container">
        <a href="{base}/" class="logo-link">
            <img src="{base}/octopus-swim-left.png" alt="Home" class="logo" />
        </a>
    </div>
    
    <div class="nav-controls">
        <ThemeToggle class="nav-theme-toggle"
        />
    </div>
</nav>

<style>
    .nav {
        display: flex;
        justify-content: flex-end;  /* Pushes content to the right */
        align-items: center;
    }

    .logo-container {
        transition: transform var(--transition-medium) ease;
    }

    .logo-container:hover {
        transform: rotate(var(--left-tilt)) scale(1.05);
    }

    .logo-link {
        display: block;
        border: none;
    }
    
    .logo {
        height: 3.5rem;
        transform: translateY(0.3rem); /* Moves logo up slightly */
        width: auto;
        border-radius: var(--border-radius);
    }

    .nav-controls {
        display: flex;
        align-items: center;
    }

    /* Only style the nav-specific theme toggle to be larger */
    :global(.nav-theme-toggle) {
        width: 3rem !important;
        height: 3rem !important;
        border-radius: var(--border-radius) !important;
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
    }

    :global(.nav-theme-toggle:hover) {
        background: var(--bg-tertiary) !important;
    }

    :global(.nav-theme-toggle .icon) {
        width: 1.5rem !important;
        height: 1.5rem !important;
    }


    /* Responsive adjustments */
    @media (max-width: 768px) {
        .nav {
            display: flex;
            justify-content: flex-end;  /* Pushes content to the right */
            align-items: center;
        }

        .logo {
            height: 3rem;
        }

        :global(.nav-theme-toggle) {
            width: 2.5rem !important;
            height: 2.5rem !important;
        }

        :global(.nav-theme-toggle .icon) {
            width: 1.25rem !important;
            height: 1.25rem !important;
        }
    }
</style>