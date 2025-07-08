<script>
	import { reveal } from 'svelte-reveal';
	import Label from './Label.svelte';
	import { base } from "$app/paths";
</script>

<div class="slide">
	<div class="container">
		<div class="content-section" use:reveal={{ delay: 100 }}>
			<Label variant="secondary">Longer-term partnerships</Label>
			<p use:reveal={{ delay: 300 }}>Web-based platform for facilitating interdisciplinary research collaboration and knowledge sharing.</p>
			<ul>
				<li use:reveal={{ delay: 500, preset: 'slide', x: -20 }}><strong>Tailored projects</strong> that might be innovative in different ways, such as a data collection process that integrates a front-end (web interface) with a back-end (a database accessed through an API)</li>
				<li use:reveal={{ delay: 700, preset: 'slide', x: -20 }}>We work together setting up digital infrastructure and software libraries such that it is robust and secure in the foreseeable future.</li>
				<li use:reveal={{ delay: 900, preset: 'slide', x: -20 }}>We provide mentorships in those different aspects, teaching methods from industry that are rarely taught in academia.</li>
			</ul>
		</div>
		
		<div class="divider" use:reveal={{ delay: 800 }}>
			<div class="vertical-line"></div>
		</div>
		
		<div class="image-section" use:reveal={{ delay: 1200, preset: 'scale', scale: 0.9 }}>
			<a href="https://catalogresearch.uvm.edu/" target="_blank" rel="noopener">
			<img src="{base}/common/thumbnails/screenshots/explore-the-cat-project.jpg" alt="Explore the Cat Project" />
			</a>
		</div>
	</div>
</div>

<style>
	.slide {
		padding-bottom: 2rem;
	}
	
	.container {
		display: grid;
		grid-template-columns: 2fr auto 1fr;
		gap: 2rem;
		align-items: start;
	}
	
	.content-section {
		padding-right: 1rem;
	}
	
	.content-section p {
		font-size: 1rem;
		line-height: 1.5;
		margin-bottom: 1.5rem;
		color: #666;
	}
	
	.content-section ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	
	.content-section li {
		margin-bottom: 1rem;
		color: #555;
		position: relative;
		padding-left: 1.5rem;
		line-height: 1.4;
		font-size: 0.95rem;
	}
	
	.content-section li::before {
		content: "•";
		color: #667eea;
		font-weight: bold;
		position: absolute;
		left: 0;
		font-size: 1.2rem;
	}
	
	.divider {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 100%;
		min-height: 300px;
	}
	
	.vertical-line {
		width: 1px;
		height: 80%;
		background: linear-gradient(to bottom, transparent, rgba(0, 0, 0, 0.1), transparent);
	}
	
	.image-section {
		display: flex;
		justify-content: center;
		align-items: flex-start;
		padding-top: 1rem;
	}
	
	img {
		width: 100%;
		max-width: 300px;
		height: auto;
		border-radius: 8px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}
	
	/* Responsive design */
	@media (max-width: 1024px) {
		.container {
			grid-template-columns: 1fr;
			gap: 1.5rem;
		}
		
		.divider {
			display: none;
		}
		
		.image-section {
			order: -1;
			padding-top: 0;
		}
		
		.content-section {
			padding-right: 0;
		}
	}
	
	@media (max-width: 768px) {
		img {
			max-width: 250px;
		}
	}
</style>