<script lang="ts">
	import { base } from '$app/paths';
	import { ModeWatcher, setMode } from "mode-watcher";
	import { Sun, Moon } from "lucide-svelte";
	
	let isDark = $state(false);
	
	$effect(() => {
		// Check if dark mode is currently active
		isDark = document.documentElement.classList.contains('dark');
	});
	
	function toggleTheme() {
		isDark = !isDark;
		setMode(isDark ? 'dark' : 'light');
	}
</script>

<ModeWatcher />

<!-- Invisible sticky header container -->
<header class="header">
	<!-- Centered logo -->
	<div class="logo-container">
		<a href="{base}/" class="logo-link">
			<img src="{base}/octopus-swim-right.png" alt="Home" class="logo" />
		</a>
	</div>

	<!-- Top right theme toggle -->
	<button onclick={toggleTheme} class="theme-toggle">
		{#if isDark}
			<Sun class="icon" />
		{:else}
			<Moon class="icon" />
		{/if}
		<span class="sr-only">Toggle theme</span>
	</button>
</header>

<style>
	.header {
        position: sticky;
        top: 0;
        z-index: 50;
        width: 100%;
        background: #fefefe;
        padding: 2rem 0 0.5rem 0; /* Even less bottom padding */
        min-height: 8.5rem; /* Adjusted height */
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
	
	:global(.dark) .header {
		background: #1a202c;
	}
	
	.logo-container {
		max-width: 250px;
		transition: transform 0.25s ease;
		/* Remove absolute positioning, let it center naturally */
	}
	
	.logo-container:hover {
		transform: rotate(-2deg) scale(1.05);
	}
	
	.logo-link {
		display: block;
		border: none;
	}
	
	.logo {
		width: 100%;
		height: auto;
		border-radius: 0.5rem;
		max-height: 8rem;
	}
	
	.theme-toggle {
		position: absolute;
		top: 2rem; /* Align with the logo's top position */
		right: 1.5rem;
		display: flex;
		align-items: center;
		justify-content: center;
		background: rgba(255, 255, 255, 0.9);
		border: 1px solid rgba(0, 0, 0, 0.08);
		cursor: pointer;
		padding: 0.5rem;
		border-radius: 0.5rem;
		transition: all 0.2s;
		color: #4a5568;
		width: 2.5rem;
		height: 2.5rem;
		backdrop-filter: blur(12px);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}
	
	:global(.dark) .theme-toggle {
		background: rgba(45, 55, 72, 0.9);
		border-color: rgba(255, 255, 255, 0.1);
		color: #e2e8f0;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
	}
	
	.theme-toggle:hover {
		background: rgba(247, 250, 252, 0.95);
		border-color: rgba(0, 0, 0, 0.15);
		transform: rotate(2deg) scale(1.05);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}
	
	:global(.dark) .theme-toggle:hover {
		background: rgba(74, 85, 104, 0.95);
		border-color: rgba(255, 255, 255, 0.2);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
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
	
	/* Responsive adjustments */
	@media (max-width: 768px) {
		.header {
			padding: 1.5rem 0;
			min-height: 6rem;
		}
		
		.logo-container {
			max-width: 150px;
		}
		
		.theme-toggle {
			top: 1.5rem;
			right: 1rem;
		}
		
		.logo {
			max-height: 4rem;
		}
	}
</style>