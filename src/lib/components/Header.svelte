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

<!-- Header.svelte - keep all your script the same, just update the styles -->
<style>
  .header {
    position: sticky;
    top: 0;
    z-index: var(--z-overlay);
    width: 100%;
    background: var(--color-bg);
    padding: 1.5rem 0 0.5rem 0;
    min-height: 7rem;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }

  /* All your existing .header-left, .title-link, etc. styles stay the same... */
  .header-left {
    position: absolute;
    left: 2.5rem;
    top: 2.5rem;
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
    height: auto;
    border-radius: var(--border-radius);
    max-height: 8rem;
    object-fit: contain;
  }
  
  .header-right {
    position: absolute;
    top: 2.5rem;
    right: 2.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  /* CLEAN button styles - no !important needed */
  .theme-toggle,
  .menu-toggle {
    /* Reset any browser defaults */
    border: none;
    background: none;
    padding: 0;
    cursor: pointer;
    font-family: inherit;
    
    /* Our component styling */
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 0.5rem;
    transition: all var(--transition-medium);
  }
  
  .theme-toggle {
    /* Theme toggle is transparent */
    background: transparent;
    color: var(--color-fg);
  }
  
  .menu-toggle {
    /* Menu toggle has a background */
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(0, 0, 0, 0.08);
    color: #4a5568;
    backdrop-filter: blur(12px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .theme-toggle:hover {
    transform: rotate(var(--right-tilt)) scale(1.05);
    background: rgba(0, 0, 0, 0.05);
  }
  
  .menu-toggle:hover {
    background: rgba(247, 250, 252, 0.95);
    border-color: rgba(0, 0, 0, 0.15);
    transform: rotate(var(--right-tilt)) scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  /* Dark mode - clean and simple */
  :global(.dark) .theme-toggle {
    color: var(--color-fg);
  }
  
  :global(.dark) .menu-toggle {
    background: rgba(74, 85, 104, 0.9);
    border-color: rgba(255, 255, 255, 0.1);
    color: #e2e8f0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }
  
  :global(.dark) .theme-toggle:hover {
    background: rgba(255, 255, 255, 0.1);
  }
  
  :global(.dark) .menu-toggle:hover {
    background: rgba(74, 85, 104, 0.95);
    border-color: rgba(255, 255, 255, 0.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  }

  /* Mobile styles */
  @media (max-width: 768px) {
    .theme-toggle {
      display: none;
    }

    .header {
      padding: 1rem 0 0 0;
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
    }
    
    .header-right {
      top: 1rem;
      right: 1rem;
    }
    
    .logo {
      max-height: 4rem;
    }
  }
  
  :global(.dark) .logo {
    filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
    padding: 4px;
    border-radius: var(--border-radius);
  }

  
</style>