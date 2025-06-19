<script lang="ts">
	import { base } from '$app/paths';
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
				<li><a href="https://www.youtube.com/@example" target="_blank" rel="noreferrer">YouTube</a></li>
				<li><a href="https://twitter.com/example" target="_blank" rel="noreferrer">Twitter</a></li>
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
		background-color: var(--color-uvm-green); /* UVM green in light mode */
		border-top: 1px solid var(--color-border);
		padding: 3rem 2rem 2rem;
	}
	
	/* Keep dark background in dark mode */
	:global(.dark) .footer {
		background-color: var(--color-gray-800);
		border-top-color: var(--color-gray-700);
	}
	
	.footer-content {
		max-width: 1200px;
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
		color: var(--color-uvm-gold); /* UVM gold in light mode */
	}
	
	/* Keep light text in dark mode */
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
		color: var(--color-white); /* White text on green background */
		text-decoration: underline;
		font-weight: 500;
		transition: color var(--transition-medium);
	}
	
	:global(.dark) .footer-section a {
		color: var(--color-gray-300);
	}
	
	.footer-section a:hover {
		color: var(--color-uvm-gold); /* Gold on hover in light mode */
	}
	
	:global(.dark) .footer-section a:hover {
		color: var(--color-gray-100);
	}
	
	.footer-logo {
		display: flex;
		align-items: center;
		justify-content: center;
		max-width: 160px;
	}
	
	.footer-logo-img {
		width: 100%;
		height: auto;
		max-height: 120px;
		border-radius: var(--border-radius);
		transform: rotate(var(--left-tilt));
		transition: transform var(--transition-medium);
	}
	
	.footer-logo-img:hover {
		transform: rotate(0deg);
	}
	
	/* Mobile adjustments - keep same layout but make it fit */
	@media (max-width: 768px) {
		.footer {
			padding: 2rem 1rem 1.5rem; /* Reduce padding */
		}
		
		.footer-content {
			gap: 1rem; /* Reduce gap between sections */
		}
		
		.footer-section h3 {
			font-size: 10px; /* Smaller headings */
			margin-bottom: 0.75rem;
		}
		
		.footer-section a {
			font-size: 12px; /* Smaller links */
		}
		
		.footer-section li {
			margin-bottom: 0.3rem; /* Tighter spacing */
		}
		
		.footer-logo {
			max-width: 100px; /* Smaller logo */
		}
		
		.footer-logo-img {
			max-height: 80px; /* Smaller max height */
		}
	}
</style>