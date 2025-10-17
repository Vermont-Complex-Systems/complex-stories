<script>
    import { Sun, Moon } from "@lucide/svelte";
    import { ModeWatcher, setMode } from "mode-watcher";

    let { isDark = $bindable(false) } = $props();
    
    $effect(() => {
        isDark = document.documentElement.classList.contains('dark');
    });
    
    function toggleTheme() {
        isDark = !isDark;
        setMode(isDark ? 'dark' : 'light');
    }
</script>

<ModeWatcher />

<!-- Use a regular button instead of Bits UI for simpler styling -->
<button onclick={toggleTheme} class="theme-toggle">
    {#if isDark}
        <Sun size={25}/>
    {:else}
        <Moon size={25}/>
    {/if}
</button>

<style>
    .theme-toggle {
        /* Reset button defaults */
        border: none;
        background: none;
        padding: 0;
        cursor: pointer;
        font-family: inherit;
        
        /* Component styling */
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 50%;
        color: var(--color-fg);
        transition: all var(--transition-medium);
    }
    
    .theme-toggle:hover {
        background: rgba(0, 0, 0, 0.05);
        transform: rotate(var(--right-tilt)) scale(1.05);
    }

    :global(.dark) .theme-toggle:hover {
        background: rgba(255, 255, 255, 0.1);
    }
    
</style>