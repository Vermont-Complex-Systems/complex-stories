<script lang="ts">
	import { base } from '$app/paths';
	import { ModeWatcher, setMode } from "mode-watcher";
	import { Sun, Moon, Menu as MenuIcon, User } from "@lucide/svelte";
  // import ConstructionBanner from '$lib/components/helpers/ConstructionBanner.svelte'
	import Menu from "./Header.Menu.svelte";
	import { getCurrentUser } from '$lib/api/auth.remote';
	import { Avatar } from "bits-ui";

	// Function to get user initials from username
	function getUserInitials(username) {
		if (!username) return 'U';
		const parts = username.split('_');
		if (parts.length >= 2) {
			return (parts[1][0] + parts[0][0]).toUpperCase();
		}
		return username.slice(0, 2).toUpperCase();
	}
	
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

		<a href="{base}/datasets" class="text-button">
			Datasets
		</a>
		
    <a href="{base}/research-at-uvm" class="text-button">
			Groups@UVM
		</a>

		{#await getCurrentUser()}
			<!-- Loading auth state -->
		{:then user}
			{#if user}
				<a href="{base}/auth" class="avatar-button">
					<Avatar.Root class="avatar-root">
						<Avatar.Fallback class="avatar-fallback">
							{getUserInitials(user.username)}
						</Avatar.Fallback>
					</Avatar.Root>
				</a>
			{:else}
				<a href="{base}/auth" class="text-button">
					Log in
				</a>
			{/if}
		{:catch}
			<a href="{base}/auth" class="text-button">
				Log in
			</a>
		{/await}

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
    padding: 1.5rem var(--margin-left) 0.5rem var(--margin-left);
    min-height: 7rem;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    box-sizing: border-box;
  }

  .header-left {
    padding-top: 1rem;
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
    flex-shrink: 0;
  }
  
  .logo-container:hover {
    transform: rotate(var(--right-tilt)) scale(1.05);
  }
  
  .logo-link {
    display: block;
    border: none;
  }
  
  .logo {
    width: auto;
    height: auto;
    border-radius: var(--border-radius);
    max-height: 2rem;
    object-fit: contain;
  }
  
  .header-right {
    padding-top: 1rem;
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

  .avatar-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
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

  .avatar-button:hover {
    transform: rotate(var(--right-tilt)) scale(1.05);
    background: rgba(0, 0, 0, 0.05);
  }

  :global(.avatar-root) {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    overflow: hidden;
    flex-shrink: 0;
  }

  :global(.avatar-fallback) {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-fg);
    color: var(--color-bg);
    font-family: var(--sans);
    font-weight: var(--font-weight-bold);
    font-size: 0.75rem;
    text-transform: uppercase;
  }

  .username {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 8rem;
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
  :global(.dark) .icon-button,
  :global(.dark) .avatar-button {
    color: var(--color-fg);
  }

  :global(.dark) .text-button:hover,
  :global(.dark) .icon-button:hover,
  :global(.dark) .avatar-button:hover {
    background: rgba(255, 255, 255, 0.1);
  }
  
  /* Mobile styles */
  @media (max-width: 960px) {
    .icon-button,
    .text-button,
    .avatar-button {
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
      padding: 1rem var(--margin-left-mobile) 0 var(--margin-left-mobile);
      min-height: 5rem;
    }
    
    .header-left {
      padding-top: 1rem;
    }
    
    .site-title {
        font-size: clamp(2rem, 3.5vw, 1.25rem) !important;
    }
    
    .site-subtitle {
      font-size: var(--font-size-xsmall);
    }
    
    .header-right {
      padding-top: 1rem;
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