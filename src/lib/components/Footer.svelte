<script lang="ts">
	import { base } from '$app/paths';
	import { Youtube, Github, Linkedin, MessageCircle } from "@lucide/svelte";
</script>

<footer class="footer">
	<div class="footer-content">
		<div class="footer-section">
			<h3>About</h3>
			<ul>
				<li><a href="{base}/about">Our Team</a></li>
				<li><a href="{base}/blog">Blog</a></li>
			</ul>
		</div>
		
		<div class="footer-section">
			<h3>Follow Us</h3>
			<ul>
				<li>
					<a href="https://www.youtube.com/@UVMcomplexity" target="_blank" rel="noreferrer">
						<Youtube class="icon" size={16} />
						<span>YouTube</span>
					</a>
				</li>
				<li>
					<a href="https://github.com/Vermont-complex-systems" target="_blank" rel="noreferrer">
						<Github class="icon" size={16} />
						<span>GitHub</span>
					</a>
				</li>
				<li>
					<a href="https://linkedin.com/school/uvm-vcsc/" target="_blank" rel="noreferrer">
						<Linkedin class="icon" size={16} />
						<span>LinkedIn</span>
					</a>
				</li>
				<li>
					<a href="https://discord.gg/3VYnT5D4" target="_blank" rel="noreferrer">
						<MessageCircle class="icon" size={16} />
						<span>Discord</span>
					</a>
				</li>
			</ul>
		</div>
		
		<div class="footer-logo">
			<img src="{base}/Roboctopus_transparent.png" alt="Logo" class="footer-logo-img" />
		</div>
	</div>
</footer>

<style>
	.footer {
		margin-top: auto;
		background-color: var(--color-uvm-green);
		border-top: 1px solid var(--color-border);
		padding: 3rem 2rem 2rem;
	}
	
	:global(.dark) .footer {
		background-color: var(--color-gray-800);
		border-top-color: var(--color-gray-700);
	}
	
	.footer-content {
		max-width: var(--width-column-wide); /* Use design system width */
		margin: 0 auto;
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 2rem;
	}
	
	.footer-section {
		flex: 1;
	}
	
	.footer-section h3 {
		font-family: var(--mono);
		font-weight: var(--font-weight-bold);
		text-transform: uppercase;
		font-size: var(--font-size-xsmall);
		margin-bottom: 1rem;
		color: var(--color-uvm-gold);
	}
	
	:global(.dark) .footer-section h3 {
		color: var(--color-gray-100);
	}
	
	.footer-section ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	
	.footer-section li {
		margin-bottom: 0.5rem;
	}
	
	.footer-section a {
		color: var(--color-white);
		text-decoration: underline;
		font-weight: 500;
		transition: color var(--transition-medium);
		display: flex;
		align-items: center;
		gap: 0.5rem; /* Space between icon and text */
	}
	
	:global(.dark) .footer-section a {
		color: var(--color-gray-300);
	}
	
	.footer-section a:hover {
		color: var(--color-uvm-gold);
	}
	
	:global(.dark) .footer-section a:hover {
		color: var(--color-gray-100);
	}
	
	.footer-logo {
		display: flex;
		align-items: center;
		justify-content: center;
		max-width: 10rem; /* Convert 160px to rem */
	}
	
	.footer-logo-img {
		width: 100%;
		height: auto;
		max-height: 7.5rem; /* Convert 120px to rem */
		border-radius: var(--border-radius);
		transform: rotate(var(--left-tilt));
		transition: transform var(--transition-medium);
	}
	
	.footer-logo-img:hover {
		transform: rotate(0deg);
	}

	
	/* Mobile adjustments */
	@media (max-width: 768px) {
		.footer {
			padding: 2rem 1rem 1.5rem;
		}
		
		.footer-content {
			gap: 1rem;
		}
		
		.footer-section h3 {
			font-size: var(--font-size-xsmall); /* Use design system instead of hardcoded 10px */
			margin-bottom: 0.75rem;
		}
		
		.footer-section a {
			font-size: var(--font-size-xsmall); /* Use design system instead of hardcoded 12px */
		}
		
		.footer-section li {
			margin-bottom: 0.3rem;
		}
		
		.footer-logo {
			max-width: 6.25rem; /* Convert 100px to rem */
		}
		
		.footer-logo-img {
			max-height: 5rem; /* Convert 80px to rem */
		}
	
	}
</style>