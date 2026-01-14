<script>
    import { base } from "$app/paths";
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

    <!-- Center: Empty for now -->
    <div class="header-center">
    </div>

    <!-- Right side: Empty for now, but could add controls -->
    <div class="header-right">
    </div>
</header>

<style>
   header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 2rem;
        position: sticky;
        top: 0;
        background: rgba(43, 43, 43, 0.85); /* Dark background to match story theme */
        backdrop-filter: blur(15px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 1000;
        transition: all 300ms ease;
        min-height: 1rem;
        width: 100vw;
        margin-left: calc(-50vw + 50%);
        box-sizing: border-box;
        overflow: visible;
    }

    header:hover {
        background: rgba(43, 43, 43, 0.95);
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

    .logo-container {
        max-width: 12rem;
        transition: transform var(--transition-medium) ease;
        margin: 0;
        position: relative;
        z-index: 10;
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
        max-height: 4.5rem;
        object-fit: contain;
        transform: translateY(0.6rem);
    }

    @media (max-width: 768px) {
        header {
            padding: 0.5rem 1rem;
            min-height: 3rem;
            background: rgba(43, 43, 43, 0.95); /* More opaque on mobile */
        }

        .logo {
            max-height: 3rem;
        }
    }

    @media (max-width: 480px) {
        .logo-container {
            max-width: 5rem;
        }
    }
</style>
