<script lang="ts">
	import { base } from '$app/paths';
	import { Youtube, Github, Linkedin, MessageCircle, ExternalLink } from "@lucide/svelte";
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
			<img src="{base}/UVM_Logo_Primary_Horiz_W_PunchOut.png" alt="UVM Logo" class="uvm-logo-img" />
			<img src="{base}/Roboctopus_2024.png" alt="Roboctopus Logo" class="roboctopus-logo-img" />
			<a class="cc-footer-copy" href="https://www.uvm.edu/equal-opportunity/americans-disabilities-act-and-reasonable-accommodations" target="_blank" rel="noreferrer">
				<span class="link-text">Accessibility <ExternalLink class="icon" size={14} /></span>
			</a>
			<a class="cc-footer-copy" href="https://www.uvm.edu/compliance/website-privacy-policy/terms-use" target="_blank" rel="noreferrer">
				<span class="privacy-text">Privacy/<br>Terms of Use <ExternalLink class="icon" size={14} /></span>
			</a>
			<div class="cc-footer-copy">© 2025, Vermont Complex Systems Institute at UVM</div>
		</div>
	</div>
</footer>

<style>
	.footer {
		margin-top: auto;
		background-color: var(--color-uvm-green);
		border-top: 1px solid var(--color-border);
		padding: 3rem 1rem 2rem;
		width: 100%;
		box-sizing: border-box;
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
		gap: 1rem;
		width: 100%;
		box-sizing: border-box;
	}
	
	.footer-section {
		flex: 1;
	}
	
	.footer-section h3 {
		font-family: var(--mono);
		font-weight: var(--font-weight-bold);
		text-transform: uppercase;
		font-size: var(--font-size-small) !important;
		margin-bottom: 0.75rem;
		color: var(--color-uvm-gold);
		margin-top: 0;
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
		font-size: 0.95rem !important;
		transition: color var(--transition-medium);
		display: flex;
		align-items: center;
		gap: 0.5rem; /* Space between icon and text */
	}
	
	:global(.dark) .footer-section a {
		color: var(--color-gray-gold);
	}
	
	.footer-section a:hover {
		color: var(--color-uvm-gold);
	}
	
	:global(.dark) .footer-section a:hover {
		color: var(--color-gray-100);
	}
	
	.footer-logo {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		justify-content: flex-start;
		max-width: 12rem;
		min-width: 0;
		gap: 0.5rem;
		flex-shrink: 1;
		overflow: hidden;
	}

	.footer-logo a {
		color: var(--color-uvm-gold);
	}
	
	.uvm-logo-img {
		width: 100%;
		height: auto;
		max-height: 4rem; /* Smaller for UVM logo */
		border-radius: var(--border-radius);
		transition: transform var(--transition-medium);
	}
	
	.roboctopus-logo-img {
		width: auto;
		max-width: 100%;
		height: auto;
		max-height: 8rem;
		border-radius: var(--border-radius);
		transition: transform var(--transition-medium);
		object-fit: contain;
		align-self: flex-start; /* Force left alignment */
	}
	
	.roboctopus-logo-img:hover {
		transform: rotate(var(--left-tilt));
	}
	
	.cc-footer-copy {
		color: var(--color-white);
		font-weight: 500;
		font-size: 1rem;
		transition: color var(--transition-medium);
		text-align: left;
		display: block;
		max-width: 100%;
	}

	.link-text {
		display: inline-flex;
		align-items: center;
		gap: 0.25rem;
		flex-wrap: nowrap;
	}

	.link-text :global(.icon),
	.privacy-text :global(.icon) {
		width: 14px !important;
		height: 14px !important;
		flex-shrink: 0;
		transform: translateY(-0.1rem); 
	}

	.privacy-text {
		display: inline-flex;
		align-items: flex-end;
		gap: 0.25rem;
		flex-wrap: nowrap;
		line-height: 1.2;
	}
	
	:global(.dark) .cc-footer-copy {
		color: var(--color-gray-300);
	}
	
	.cc-footer-copy:hover {
		color: var(--color-gray-300);
	}
	
	:global(.dark) .cc-footer-copy:hover {
		color: var(--color-gray-100);
	}
	
	/* Copyright div styling - no hover effects, no yellow color */
	.cc-footer-copy:not(a) {
		color: var(--color-white);
		text-decoration: none;
		justify-content: flex-start;
	}
	
	:global(.dark) .cc-footer-copy:not(a) {
		color: var(--color-gray-300);
	}

	
	/* Mobile adjustments */
	@media (max-width: 768px) {
		.footer {
			padding: 2rem 1rem 1.5rem;
		}
		
		.footer-content {
			gap: 1rem;
			justify-content: space-between;
			align-items: flex-start;
		}
		
		.footer-section {
			flex: 1;
			min-width: 0;
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
			max-width: 6.5rem; /* Give more space for accessibility links */
			min-width: 0;
			margin-right: 0.5rem; Move content left by adding right margin
		}

		.cc-footer-copy {
			font-size: 0.95rem;
		}
	
	}
</style>