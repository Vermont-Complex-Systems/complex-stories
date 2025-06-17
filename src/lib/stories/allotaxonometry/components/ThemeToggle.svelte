<script>
    import { Button } from "bits-ui";
    
    let { isDarkMode = $bindable(false) } = $props();
    
    function toggleTheme() {
        isDarkMode = !isDarkMode;
        document.documentElement.classList.toggle('dark', isDarkMode);
    }
</script>

<div class="theme-toggle">
    <Button.Root onclick={toggleTheme} variant="outline" size="sm">
        {#if isDarkMode}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="5"/>
                <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
            </svg>
        {:else}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
        {/if}
        <span class="sr-only">Toggle theme</span>
    </Button.Root>
</div>

<style>
    .theme-toggle {
        position: absolute;
        top: 1rem;
        right: 1rem;
        z-index: 1001;
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