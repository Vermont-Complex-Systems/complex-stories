<script lang="ts">
	import { base } from '$app/paths';
	import { ModeWatcher, setMode } from "mode-watcher";
	import { Sun, Moon } from "lucide-svelte";
	
	let isDark = $state(false);
	
	$effect(() => {
		isDark = document.documentElement.classList.contains('dark');
	});
	
	function toggleTheme() {
		isDark = !isDark;
		setMode(isDark ? 'dark' : 'light');
	}
</script>

<ModeWatcher />

<header class="header">
	<div class="logo-container">
		<a href="{base}/" class="logo-link">
			<img src="{base}/octopus-swim-right.png" alt="Home" class="logo" />
		</a>
	</div>

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
		z-index: var(--z-overlay);
		width: 100%;
		background: var(--color-bg);
		padding: 2rem 0 0.5rem 0;
		min-height: 8.5rem;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
	}
	
	.logo-container {
		max-width: 250px;
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
		width: 100%;
		height: auto;
		border-radius: var(--border-radius);
		max-height: 8rem;
	}
	
	.theme-toggle {
		position: absolute;
		top: 2rem;
		right: 1.5rem;
		display: flex;
		align-items: center;
		justify-content: center;
		/* Override global button styles */
		background: rgba(255, 255, 255, 0.9) !important;
		border: 1px solid rgba(0, 0, 0, 0.08) !important;
		color: #4a5568 !important;
		/* Reset global button styles */
		text-transform: none !important;
		cursor: pointer;
		padding: 0.5rem;
		border-radius: 0.5rem; /* Override global border-radius */
		transition: all var(--transition-medium);
		width: 2.5rem;
		height: 2.5rem;
		backdrop-filter: blur(12px);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}
	
	/* Dark mode styles */
	:global(.dark) .theme-toggle {
		background: rgba(45, 55, 72, 0.9) !important;
		border-color: rgba(255, 255, 255, 0.1) !important;
		color: #e2e8f0 !important;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
	}
	
	.theme-toggle:hover {
		background: rgba(247, 250, 252, 0.95) !important;
		border-color: rgba(0, 0, 0, 0.15) !important;
		transform: rotate(var(--right-tilt)) scale(1.05);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}
	
	:global(.dark) .theme-toggle:hover {
		background: rgba(74, 85, 104, 0.95) !important;
		border-color: rgba(255, 255, 255, 0.2) !important;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
	}
	
	.icon {
		width: 1.125rem;
		height: 1.125rem;
	}
	
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