<script>
    import { Button } from "bits-ui";
    import { Sun, Moon } from "@lucide/svelte";
    import { ModeWatcher, setMode } from "mode-watcher";

    let { 
        isDark = $bindable(false),
        class: className = "",
        hideOnMobile = true
    } = $props();
    
    // Build the class string inside the component
    let buttonClass = $derived(`theme-toggle ${className} ${hideOnMobile ? 'hide-mobile' : ''}`);
    
    $effect(() => {
        isDark = document.documentElement.classList.contains('dark');
    });
    
    function toggleTheme() {
        isDark = !isDark;
        setMode(isDark ? 'dark' : 'light');
    }
</script>

<ModeWatcher />

<Button.Root 
    onclick={toggleTheme}  
    class={buttonClass}
>
    {#if isDark}
        <Sun class="icon" />
    {:else}
        <Moon class="icon" />
    {/if}
    <span class="sr-only">Toggle theme</span>
</Button.Root>

<style>
    :global(.theme-toggle) {
        display: flex;
        align-items: center;
        justify-content: center;
        background: transparent !important;
        border: none !important;
        color: var(--color-fg) !important;
        cursor: pointer;
        padding: 0.5rem !important;
        border-radius: 0.5rem;
        transition: all var(--transition-medium);
        width: 2.5rem;
        height: 2.5rem;
    }


    :global(.theme-toggle:hover) {
        background: rgba(0, 0, 0, 0.05) !important;
        transform: rotate(var(--right-tilt)) scale(1.05);
    }
    
    :global(.dark .theme-toggle:hover) {
        background: rgba(255, 255, 255, 0.1) !important;
    }

    @media (max-width: 768px) {
        :global(.theme-toggle.hide-mobile) {
            display: none !important;
        }
    }

    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }
</style>