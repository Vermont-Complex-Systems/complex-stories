<script lang="ts">
	import { base } from '$app/paths';
	import { ModeWatcher, setMode } from "mode-watcher";
	import { Sun, Moon, Menu as MenuIcon } from "@lucide/svelte";
  // import ConstructionBanner from '$lib/components/helpers/ConstructionBanner.svelte'
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
</script>

<ModeWatcher />

<header class="header">
	<div class="header-left">
		<a href="{base}/" class="title-link">
			<div class="title-container">
				<div class="title-with-octopus">
					<h1 class="site-title">Complex Stories</h1>
					<img src="{base}/octopus-swim-right.png" alt="Octopus" class="octopus-icon" />
				</div>
				<p class="site-subtitle">Describe, Explain, Create, Share.</p>
			</div>
		</a>
	</div>

	<div class="header-right">
		<a href="{base}/blog" class="text-button">
			Blog
		</a>

		<a href="https://vermont-complex-systems.github.io/datasets/" class="text-button">
			Datasets
		</a>
		
    <a href="{base}/research-at-uvm" class="text-button">
			Groups@UVM
		</a>

    <a 
			href="https://github.com/Vermont-Complex-Systems/complex-stories" 
			class="icon-button"
			target="_blank"
		>
			<svg fill="currentColor" viewBox="0 0 24 24">
				<path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
			</svg>
		</a>

		<button onclick={toggleTheme} class="icon-button">
			{#if isDark}
				<Sun class="icon" size={20} />
			{:else}
				<Moon class="icon" size={20} />
			{/if}
			<span class="sr-only">Toggle theme</span>
		</button>

		<div class="logo-container">
			<a href="{base}/" class="logo-link">
				<img src="{base}/vcsi-bumper-sticker-horizontal.jpg" alt="Home" class="logo" />
			</a>
		</div>

    		<!-- Mobile hamburger menu -->
		<button 
			onclick={() => isMenuOpen = !isMenuOpen}
			bind:this={menuButtonRef}
			class="icon-button mobile-menu-button"
		>
			<MenuIcon class="icon" size={28} />
			<span class="sr-only">Open menu</span>
		</button>

	</div>
</header>

<Menu visible={isMenuOpen} close={closeMenu} />

<!-- <ConstructionBanner /> -->

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

  .header-left {
    position: absolute;
    left: var(--margin-left);
    top: 2.5rem;
  }
  
  .title-link {
    display: block;
    text-decoration: none;
    color: inherit;
    transition: transform var(--transition-medium) ease;
  }
  
  .title-link:hover {
    transform: translateY(-0.125rem);
  }

  .title-container {
    display: flex;
    flex-direction: column;
  }

  .title-with-octopus {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .octopus-icon {
    height: 2.5rem;
    object-fit: contain;
    transition: transform var(--transition-medium) ease;
    transform: translateY(0.5rem);
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
    margin: 0.25rem 0 0 0.25rem;
    color: var(--color-secondary-gray);
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }
  
  .logo-container {
    transition: transform var(--transition-medium) ease;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .logo-container:hover {
    transform: rotate(var(--right-tilt)) scale(1.05);
  }
  
  .logo-link {
    display: block;
    border: none;
  }
  
  .logo {
    width: 100%;
    height: auto;
    border-radius: var(--border-radius);
    max-height: 2rem;
    object-fit: contain;
  }
  
  .header-right {
    position: absolute;
    top: 2.5rem;
    right: var(--margin-left);
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

   /* Hide mobile menu button on desktop */
  .mobile-menu-button {
    display: none !important;
  }
  
  /* Only show on mobile */
  @media (max-width: 960px) {
    .mobile-menu-button {
      display: flex !important;
    }
  }

  /* Text buttons (Blog and Datasets) */
  .text-button {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 2.5rem;
    padding: 0 0.75rem;
    border-radius: 0.5rem;
    background: transparent;
    color: var(--color-fg);
    text-decoration: none;
    font-family: var(--sans);
    font-weight: var(--font-weight-medium);
    font-size: var(--font-size-small);
    letter-spacing: 0.05em;
    transition: all var(--transition-medium);
    cursor: pointer;
  }

  .text-button:hover {
    transform: rotate(var(--right-tilt)) scale(1.05);
    background: rgba(0, 0, 0, 0.05);
  }

  /* Button styles */
  .icon-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 0.5rem;
    background: transparent;
    color: var(--color-fg);
    text-decoration: none;
    border: none;
    cursor: pointer;
    transition: all var(--transition-medium);
  }

  .icon-button svg {
    width: 1.25rem;  /* w-5 = 20px */
    height: 1.25rem; /* h-5 = 20px */
    fill: currentColor;
  }

  .icon-button:hover {
    transform: rotate(var(--right-tilt)) scale(1.05);
    background: rgba(0, 0, 0, 0.05);
  }
  
  /* Dark mode */
  :global(.dark) .text-button,
  :global(.dark) .icon-button {
    color: var(--color-fg);
  }

  :global(.dark) .text-button:hover,
  :global(.dark) .icon-button:hover {
    background: rgba(255, 255, 255, 0.1);
  }
  
  /* Mobile styles */
  @media (max-width: 960px) {
    .icon-button,
    .text-button {
      display: none;
    }

    /* Hide logo on mobile */
    .logo-container {
      display: none;
    }

    .octopus-icon {
      display: none;
    }


    .header {
      padding: 1rem 0 0 0;
      min-height: 5rem;
    }
    
    .header-left {
      left: var(--margin-left-mobile);
      top: 2rem;
    }
    
    .site-title {
        font-size: clamp(2rem, 3.5vw, 1.25rem) !important;
    }
    
    .site-subtitle {
      font-size: var(--font-size-xsmall);
    }
    
    .header-right {
      top: 2rem;
      right: var(--margin-left-mobile);
    }
  }
  
  :global(.dark) .logo {
    padding: 0.25rem;
    border-radius: var(--border-radius);
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