<!-- src/lib/components/Header.Menu.svelte -->
<script>
	import { base } from "$app/paths";
	import { afterNavigate } from "$app/navigation";
	import { X } from "lucide-svelte";
	
	// Props
	let { visible, close } = $props();
	
	// Element references
	let mainEl;
	let closeBtnEl;
	
	// Methods
	export const open = () => {
		closeBtnEl?.focus();
		mainEl?.setAttribute("aria-hidden", true);
	};
	
	const onClose = async (e) => {
		if (e?.type === "keyup" && e?.key !== "Escape") return;
		mainEl?.removeAttribute("aria-hidden");
		close(e === "skip");
	};
	
	// Setup
	$effect(() => {
		mainEl = document.querySelector("main");
	});
	
	afterNavigate(() => {
		onClose("skip");
	});
</script>

<svelte:window on:keyup={onClose} />

<nav id="nav-menu" class:visible aria-hidden={!visible}>
	<div class="nav-content" class:visible>
		<button 
			class="btn-close" 
			aria-label="close menu" 
			bind:this={closeBtnEl} 
			onclick={onClose}
		>
			<X class="icon" />
		</button>
		
		<div class="nav-links">
			<h4>Navigate</h4>
			<ul>
				<li><a href="{base}/">Home</a></li>
				<li><a href="{base}/about">About</a></li>
				<li><a href="{base}/blog">Blog</a></li>
			</ul>
		</div>
		
		<div class="social-links">
			<h4>Connect</h4>
			<ul>
				<li><a href="https://twitter.com/example" target="_blank" rel="noreferrer">Twitter</a></li>
				<li><a href="https://github.com/example" target="_blank" rel="noreferrer">GitHub</a></li>
				<li><a href="https://discord.gg/example" target="_blank" rel="noreferrer">Discord</a></li>
			</ul>
		</div>
	</div>
</nav>

<style>
	nav {
		position: fixed;
		top: 0;
		right: 0;
		width: 100%;
		max-width: min(280px, 85vw);
		height: 100svh;
		z-index: calc(var(--z-overlay) + 1);
		visibility: hidden;
		transform: translateX(100%);
		transition: transform var(--transition-medium);
		overflow-y: auto;
		
		/* Default: Light mode = Dark menu */
		background: var(--color-gray-900);
		color: var(--color-gray-100);
		border-left: 1px solid var(--color-gray-700);
		box-shadow: -4px 0 24px rgba(0, 0, 0, 0.3);
	}
	
	/* Dark mode = Light menu */
	:global(.dark) nav {
		background: var(--color-gray-200) !important;
		color: var(--color-gray-800) !important;
		border-left: 1px solid var(--color-gray-300) !important;
		box-shadow: -4px 0 24px rgba(0, 0, 0, 0.2) !important;
	}
	
	nav.visible {
		visibility: visible;
		transform: translateX(0);
	}
	
	.nav-content {
		padding: 2rem 1.5rem;
		height: 100%;
		display: flex;
		flex-direction: column;
	}
	
	/* Close button - default (light mode = dark menu) */
	.btn-close {
		background: transparent !important;
		border: 1px solid var(--color-gray-700) !important;
		color: var(--color-gray-100) !important;
		text-transform: none !important;
		font-size: 1rem;
		display: flex;
		justify-content: center;
		align-items: center;
		width: 2.5rem;
		height: 2.5rem;
		border-radius: 0.5rem;
		cursor: pointer;
		padding: 0.5rem;
		margin-bottom: 2rem;
		transition: all var(--transition-medium);
		align-self: flex-start;
	}
	
	.btn-close:hover {
		background: var(--color-gray-800) !important;
		transform: rotate(var(--right-tilt)) scale(1.05);
	}
	
	/* Close button in dark mode (light menu) */
	:global(.dark) .btn-close {
		border: 1px solid var(--color-gray-400) !important;
		color: var(--color-gray-800) !important;
	}
	
	:global(.dark) .btn-close:hover {
		background: var(--color-gray-300) !important;
	}
	
	.nav-links,
	.social-links {
		margin-bottom: 2rem;
	}
	
	/* Headers - default (dark menu) */
	h4 {
		font-family: var(--mono);
		font-size: var(--font-size-small);
		text-transform: uppercase;
		color: var(--color-gray-400);
		margin: 0 0 1rem 0;
		letter-spacing: 0.5px;
	}
	
	/* Headers in dark mode (light menu) */
	:global(.dark) h4 {
		color: var(--color-gray-600) !important;
	}
	
	ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	
	li {
		margin-bottom: 0.75rem;
	}
	
	/* Links - default (dark menu) */
	a {
		font-family: var(--sans);
		font-size: var(--font-size-medium);
		font-weight: 500;
		color: var(--color-gray-100);
		text-decoration: none;
		transition: all var(--transition-medium);
		display: block;
		padding: 0.5rem 0;
	}
	
	a:hover {
		color: var(--color-white);
		transform: translateX(4px);
	}
	
	/* Links in dark mode (light menu) */
	:global(.dark) a {
		color: var(--color-gray-800) !important;
	}
	
	:global(.dark) a:hover {
		color: var(--color-gray-900) !important;
	}
	
	/* Focus trap styles */
	nav:focus-within {
		outline: none;
	}
</style>