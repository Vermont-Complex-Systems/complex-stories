<script>
    import ThemeToggle from './ThemeToggle.svelte';
    import ToggleSex from './ToggleSex.svelte';
    import { base } from "$app/paths";
    
    let { 
        isDark = $bindable(false),
        isGirls = $bindable(true)
    } = $props();
</script>

<header class="header">
    <!-- Left side: Logo -->
    <div class="header-left">
        <div class="logo-container">
            <a href="{base}/" class="logo-link">
                <img src="{base}/octopus-swim-right.png" alt="Home" class="logo" />
            </a>
        </div>
    </div>
    
    <!-- Center: Could be used for navigation items if needed -->
    <div class="header-center">
        <!-- Empty for now, but could contain nav items -->
    </div>
    
    <!-- Right side: Toggles and author info -->
    <div class="header-right">
        <!-- Toggles - always show gender toggle, hide theme toggle on mobile -->
        <div class="toggles-container">
            <ToggleSex bind:isGirls />
            <ThemeToggle bind:isDark hideOnMobile={true} />
        </div>
    </div>
</header>

<style>
   header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 2rem; /* Much smaller vertical padding */
        position: sticky;
        top: 0;
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(15px);
        border-bottom: 1px solid rgba(0, 0, 0, 0.03);
        z-index: 1000;
        transition: all 300ms ease;
        min-height: 1rem; /* Much shorter header */
        width: 100vw;
        margin-left: calc(-50vw + 50%);
        box-sizing: border-box;
        overflow: visible; /* Allow logo to overflow */
    }

    /* Dark mode with more transparency */
    :global(.dark) header {
        background: rgba(30, 30, 30, 0.7); /* More transparent - was 0.95 */
        border-bottom: 1px solid rgba(255, 255, 255, 0.03); /* More subtle border */
    }

    /* Optional: Even more transparent on hover/scroll */
    header:hover {
        background: rgba(255, 255, 255, 0.8); /* Slightly less transparent on hover */
    }

    :global(.dark) header:hover {
        background: rgba(30, 30, 30, 0.8);
    }

    /* Header sections */
    .header-left {
        display: flex;
        align-items: center;
        flex: 0 0 auto;
    }

    .header-center {
        display: flex;
        align-items: center;
        justify-content: center;
        flex: 1;
    }

    .header-right {
        display: flex;
        align-items: center;
        flex: 0 0 auto;
    }

    /* Fix the logo positioning - remove absolute positioning */
    .logo-container {
        max-width: 12rem; /* Increased from 10.625rem */
        transition: transform var(--transition-medium) ease;
        margin: 0;
        position: relative;
        z-index: 10; /* Ensure it stays above other content */
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
        max-height: 4.5rem; /* Increased from 3rem */
        object-fit: contain;
        /* Allow logo to extend above header */
        transform: translateY(0.6rem); /* Moves logo up slightly */
    }

    .toggles-container {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    @media (max-width: 768px) {
        header {
            padding: 0.5rem 1rem;
            min-height: 3rem;
            background: rgba(255, 255, 255, 0.8); /* Less transparent on mobile for readability */
        }

        :global(.dark) header {
            background: rgba(30, 30, 30, 0.8);
        }

        .logo {
            max-height: 2rem;
        }

        .toggles-container {
            gap: 0.5rem; /* Smaller gap on mobile */
        }
    }

    @media (max-width: 480px) {
        .logo-container {
            max-width: 5rem;
        }

        .author-name {
            font-size: var(--font-size-xsmall);
        }
    }
    
</style>