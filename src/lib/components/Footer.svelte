<script lang="ts">
	import { base } from '$app/paths';
</script>

<footer class="footer">
	<div class="footer-content">
		<div class="footer-section">
			<h3>About</h3>
			<ul>
				<li><a href="{base}/about">Our Team</a></li>
				<li><a href="{base}/mission">Our Mission</a></li>
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
		background-color: #f7fafc; /* Softer light background */
		border-top: 1px solid #e2e8f0; /* Softer border */
		padding: 3rem 2rem 2rem;
	}
	
	:global(.dark) .footer {
		background-color: #2d3748; /* Warmer dark background */
		border-top-color: #4a5568; /* Softer border in dark mode */
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
		font-family: monospace;
		font-weight: 400;
		text-transform: uppercase;
		font-size: 0.875rem;
		margin-bottom: 1rem;
		color: #718096; /* Softer gray */
	}
	
	:global(.dark) .footer-section h3 {
		color: #a0aec0; /* Softer light gray */
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
		color: #4a5568; /* Softer text color */
		text-decoration: underline;
		font-weight: 500;
		transition: color 0.2s;
	}
	
	:global(.dark) .footer-section a {
		color: #e2e8f0; /* Softer white */
	}
	
	.footer-section a:hover {
		color: #3182ce; /* Nice blue instead of harsh blue */
	}
	
	:global(.dark) .footer-section a:hover {
		color: #63b3ed; /* Softer blue in dark mode */
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
		border-radius: 0.375rem;
		transform: rotate(-2deg);
		transition: transform 0.25s;
	}
	
	.footer-logo-img:hover {
		transform: rotate(0deg);
	}
	
	/* Responsive adjustments */
	@media (max-width: 768px) {
		.footer-content {
			flex-direction: column;
			text-align: center;
		}
		
		.footer-logo {
			order: -1;
			margin-bottom: 2rem;
		}
	}
</style>