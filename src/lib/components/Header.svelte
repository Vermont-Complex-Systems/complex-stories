<!-- src/lib/components/Header.svelte -->
<script lang="ts">
	import { base } from '$app/paths';
	import { ModeWatcher, setMode } from "mode-watcher";
	import { Sun, Moon, Menu as MenuIcon } from "lucide-svelte";
	import Menu from "./Header.Menu.svelte";
	
	let isDark = $state(false);
	let isMenuOpen = $state(false);
	let menuButtonRef;
	
	$effect(() => {
		isDark = document.documentElement.classList.contains('dark');
	});
	
	function toggleTheme() {
		isDark = !isDark;
		setMode(isDark ? 'dark' : 'light');
	}

	function closeMenu(skipFocus = false) {
		isMenuOpen = false;
		if (!skipFocus) menuButtonRef?.focus();
	}

	function openMenu() {
		isMenuOpen = true;
	}
</script>

<ModeWatcher />

<header class="header">
	<div class="header-left">
		<a href="{base}/" class="title-link">
			<h1 class="site-title">Complex Stories</h1>
			<p class="site-subtitle">Describe, Explain, Create, Share.</p>
		</a>
	</div>

	<div class="logo-container">
		<a href="{base}/" class="logo-link">
			<img src="{base}/octopus-swim-right.png" alt="Home" class="logo" />
		</a>
	</div>

	<div class="header-right">
		<button onclick={toggleTheme} class="theme-toggle">
			{#if isDark}
				<Sun class="icon" />
			{:else}
				<Moon class="icon" />
			{/if}
			<span class="sr-only">Toggle theme</span>
		</button>

		<button 
			bind:this={menuButtonRef}
			onclick={openMenu} 
			class="menu-toggle"
			aria-label="Open menu"
		>
			<MenuIcon class="icon" />
			<span class="sr-only">Open menu</span>
		</button>
	</div>
</header>

<!-- Menu component -->
<Menu visible={isMenuOpen} close={closeMenu} />

<style>
	.header {
		position: sticky;
		top: 0;
		z-index: var(--z-overlay);
		width: 100%;
		background: var(--color-bg);
		padding: 1.5rem 0 0.5rem 0; /* Current padding */
		min-height: 7rem;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
		}
	
  .header-left {
    position: absolute;
    left: 2.5rem;
    top: 2.5rem; /* Fixed position from top instead of center */
  }
  
  .title-link {
    display: block;
    text-decoration: none;
    color: inherit;
    transition: transform var(--transition-medium) ease;
  }
  
  .title-link:hover {
    transform: translateY(-2px);
  }
  
  .site-title {
    font-family: var(--sans);
    font-weight: var(--font-weight-bold);
    font-size: clamp(1.5rem, 3vw, 2rem);
    margin: 0;
    line-height: 1.1;
    color: var(--color-fg);
  }
  
  .site-subtitle {
    font-family: var(--mono);
    font-size: var(--font-size-small);
    margin: 0.25rem 0 0 0;
    color: var(--color-secondary-gray);
    text-transform: uppercase;
    letter-spacing: 0.5px;
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
    height: auto; /* This is good */
    border-radius: var(--border-radius);
    max-height: 8rem;
    /* Add this to preserve aspect ratio */
    object-fit: contain;
  }
  
  .header-right {
    position: absolute;
    top: 2.5rem; /* Move down to give more space */
    right: 2.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
	
	.theme-toggle {
		display: flex;
		align-items: center;
		justify-content: center;
		/* Remove all background and border styles */
		background: transparent !important;
		border: none !important;
		/* Keep the icon color matching the foreground */
		color: var(--color-fg) !important;
		text-transform: none !important;
		cursor: pointer;
		padding: 0.5rem;
		border-radius: 0.5rem;
		transition: all var(--transition-medium);
		width: 2.5rem;
		height: 2.5rem;
		/* Remove box-shadow */
		box-shadow: none !important;
		backdrop-filter: none;
	}
	
	.menu-toggle {
		display: flex;
		align-items: center;
		justify-content: center;
		/* Override global button styles */
		background: rgba(255, 255, 255, 0.9) !important;
		/* border: 1px solid rgba(0, 0, 0, 0.08) !important; */
		color: #4a5568 !important;
		/* Reset global button styles */
		text-transform: none !important;
		cursor: pointer;
		padding: 0.5rem;
		border-radius: 0.5rem;
		transition: all var(--transition-medium);
		width: 2.5rem;
		height: 2.5rem;
		backdrop-filter: blur(12px);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}
	
	/* Dark mode styles */
	:global(.dark) .theme-toggle,
	:global(.dark) .menu-toggle {
		background: var(--color-bg) !important;
		border-color: var(--color-bg) !important;
		color: #e2e8f0 !important;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
	}
	
	.theme-toggle:hover,
	.menu-toggle:hover {
		background: rgba(247, 250, 252, 0.95) !important;
		border-color: rgba(0, 0, 0, 0.15) !important;
		transform: rotate(var(--right-tilt)) scale(1.05);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}
	
	:global(.dark) .theme-toggle:hover,
	:global(.dark) .menu-toggle:hover {
		background: rgba(74, 85, 104, 0.95) !important;
		border-color: rgba(255, 255, 255, 0.2) !important;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
	}
	
	 @media (max-width: 768px) {

	/* Hide theme toggle on mobile */
    .theme-toggle {
      display: none;
    }

    .header {
    	padding: 1rem 0 0 0; /* Reduced bottom padding from 1rem to 0.25rem */
    	min-height: 5rem;
    }
    
    .header-left {
      left: 2rem;
      top: 2rem;
    }
    
    .site-title {
      font-size: clamp(1.25rem, 4vw, 1.5rem);
    }
    
    .site-subtitle {
      font-size: var(--font-size-xsmall);
    }
    
    .logo-container {
      max-width: 150px;
      margin-left: 3.5rem;
      aspect-ratio: 1; /* Adjust this to match your logo's actual ratio */
    }
    
    .header-right {
      top: 1rem;
      right: 1rem;
    }
    
    .logo {
      max-height: 4rem;
      width: 100%;
      height: 100%;
      object-fit: contain;
    }
  }
  
	:global(.dark) .logo {
		filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
		padding: 4px;
		border-radius: var(--border-radius);
	}
</style>