<script>
    import ThemeToggle from './ThemeToggle.svelte';
    import { base } from "$app/paths";
    let { isDark = $bindable(false) } = $props();
</script>

<header class="header">
    <!-- Remove utility classes -->
    <div class="logo-container">
        <a href="{base}/" class="logo-link">
            <img src="{base}/octopus-swim-right.png" alt="Home" class="logo" />
        </a>
    </div>
    
    <!-- Desktop theme toggle -->
    <div class="theme-container">
        <ThemeToggle bind:isDark hideOnMobile={true} />
    </div>
    
    <!-- Mobile author info -->
    <div class="mobile-author">
        <span class="author-name">By <a href="{base}/author/jonathan-st-onge">Jonathan St-Onge</a></span>
    </div>
</header>

<style>
     .header {
        z-index: var(--z-overlay);
        width: 100%;
        background: var(--color-bg);
        padding: 1.5rem 0 0.5rem 0;
        min-height: 5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        /* Keep it as a normal block element */
        position: relative; /* Only need this for absolute positioning of children */
        top: 1.5rem;
    }

     .theme-container {
        position: absolute;
        top: 2.5rem;
        right: 2.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .logo-container {
        max-width: 10.625rem;
        transition: transform var(--transition-medium) ease;
        position: absolute; /* Relative to header */
        top: 0.5rem;
        left: 0.5rem;
        margin: 0;
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
        max-height: 8rem;
        object-fit: contain;
    }

    .mobile-author {
        display: none;
    }

    @media (max-width: 768px) {
        

        .logo {
            max-height: 2.5rem;
        }

        .theme-container {
            display: none;
        }

        .mobile-author {
            display: block;
            position: absolute; /* Relative to header */
            top: 0.5rem;
            right: 0.5rem;
        }

        .author-name {
            font-family: var(--mono);
            font-size: var(--font-size-xsmall);
            color: var(--color-secondary-gray);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
            white-space: nowrap;
        }
    }

    @media (max-width: 480px) {
        .logo-container {
            top: 0.25rem;
            left: -5px;
            max-width: 5rem;
        }

        .mobile-author {
            top: 0.25rem;
            right: 1rem;
        }

        .author-name {
            font-size: var(--font-size-xsmall);
        }
    }
</style>