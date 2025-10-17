<script>
	import { base } from "$app/paths";
	import { afterNavigate } from "$app/navigation";
	import { X, Youtube, Github, MessageCircle, Linkedin } from "@lucide/svelte";
	
	let { visible, close } = $props();
	
	let mainEl;
	let closeBtnEl;
	
	export const open = () => {
		closeBtnEl?.focus();
		mainEl?.setAttribute("aria-hidden", true);
	};
	
	const onClose = async (e) => {
		if (e?.type === "keyup" && e?.key !== "Escape") return;
		mainEl?.removeAttribute("aria-hidden");
		close(e === "skip");
	};
	
	$effect(() => {
		mainEl = document.querySelector("main");
	});
	
	afterNavigate(() => {
		onClose("skip");
	});
</script>

<svelte:window on:keyup={onClose} />

<nav id="nav-menu" class:visible aria-hidden={!visible}>
	<div class="nav-content">
		<button 
			class="btn-close" 
			aria-label="close menu" 
			bind:this={closeBtnEl} 
			onclick={onClose}
		>
			<X class="icon" size={20} />
		</button>
		
		<div class="nav-links">
			<h4>Navigate</h4>
			<ul>
				<li><a href="{base}/">Home</a></li>
				<li><a href="{base}/about">About</a></li>
				<li><a href="{base}/blog">Blog</a></li>
				<li><a href="https://vermont-complex-systems.github.io/datasets/" target="_blank" rel="noreferrer">Datasets</a></li>
				<li><a href="{base}/research-at-uvm">Groups@UVM</a></li>
			</ul>
		</div>
		
		<div class="social-links">
			<h4>Connect</h4>
			<ul>
				<li>
					<a href="https://www.youtube.com/@UVMcomplexity" target="_blank" rel="noreferrer">
						<Youtube class="icon" size={18} />
						<span>YouTube</span>
					</a>
				</li>
				<li>
					<a href="https://github.com/Vermont-complex-systems" target="_blank" rel="noreferrer">
						<Github class="icon" size={18} />
						<span>GitHub</span>
					</a>
				</li>
				<li>
					<a href="https://linkedin.com/school/uvm-vcsc/" target="_blank" rel="noreferrer">
						<Linkedin class="icon" size={18} />
						<span>LinkedIn</span>
					</a>
				</li>
				<li>
					<a href="https://discord.gg/3VYnT5D4" target="_blank" rel="noreferrer">
						<MessageCircle class="icon" size={18} />
						<span>Discord</span>
					</a>
				</li>
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
		max-width: min(17.5rem, 85vw);
		height: 100svh;
		z-index: calc(var(--z-overlay) + 1);
		visibility: hidden;
		transform: translateX(100%);
		transition: transform var(--transition-medium);
		overflow-y: auto;
		
		/* Light mode = Dark menu */
		background: var(--color-gray-900);
		color: var(--color-gray-100);
		border-left: 1px solid var(--color-gray-700);
		box-shadow: -0.25rem 0 1.5rem rgba(0, 0, 0, 0.3);
	}
	
	/* Dark mode = Light menu */
	:global(.dark) nav {
		background: var(--color-gray-200);
		color: var(--color-gray-800);
		border-left: 1px solid var(--color-gray-300);
		box-shadow: -0.25rem 0 1.5rem rgba(0, 0, 0, 0.2);
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
	
	.btn-close {
		/* Reset button defaults */
		border: none;
		background: none;
		padding: 0;
		cursor: pointer;
		font-family: inherit;
		
		/* Our styling */
		display: flex;
		justify-content: center;
		align-items: center;
		width: 2.5rem;
		height: 2.5rem;
		border: 1px solid var(--color-gray-700);
		border-radius: 0.5rem;
		background: transparent;
		color: var(--color-gray-100);
		margin-bottom: 2rem;
		transition: all var(--transition-medium);
		align-self: flex-start;
	}
	
	.btn-close:hover {
		background: var(--color-gray-800);
		transform: rotate(var(--right-tilt)) scale(1.05);
	}
	
	/* Dark mode close button */
	:global(.dark) .btn-close {
		border-color: var(--color-gray-400);
		color: var(--color-gray-800);
	}
	
	:global(.dark) .btn-close:hover {
		background: var(--color-gray-300);
	}
	
	.nav-links,
	.social-links {
		margin-bottom: 2rem;
	}
	
	h4 {
		font-family: var(--mono);
		font-size: var(--font-size-small);
		text-transform: uppercase;
		color: var(--color-gray-400);
		margin: 0 0 1rem 0;
		letter-spacing: 0.03em;
	}
	
	:global(.dark) h4 {
		color: var(--color-gray-600);
	}
	
	ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	
	li {
		margin-bottom: 0.75rem;
	}
	
	a {
		font-family: var(--sans);
		font-size: var(--font-size-medium);
		font-weight: 500;
		color: var(--color-gray-100);
		text-decoration: none;
		transition: all var(--transition-medium);
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.5rem 0;
	}
	
	a:hover {
		color: var(--color-white);
		transform: translateX(0.25rem);
	}
	
	:global(.dark) a {
		color: var(--color-gray-800);
	}
	
	:global(.dark) a:hover {
		color: var(--color-gray-900);
	}

</style>