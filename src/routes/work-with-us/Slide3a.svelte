<script>
	import { reveal } from 'svelte-reveal';
	import Label from './Label.svelte';
	import { base } from "$app/paths";
</script>

<div class="slide">
	<div class="container">
		<div class="content-section" use:reveal={{ delay: 100 }}>
			<Label variant="secondary">"1-2" months projects</Label>
			<p use:reveal={{ delay: 300 }}>We can write code for you to accomplish particular tasks. This can be funded via fee-for-service mechanisms or through grants.</p>
			<ul>
				<li use:reveal={{ delay: 500, preset: 'slide', x: -20 }}>Projects with <strong>clear established goals</strong>.</li>
				<li use:reveal={{ delay: 700, preset: 'slide', x: -20 }}>We have <strong>prior experience</strong> in leading those projects, with known open source technologies.</li>
				<li use:reveal={{ delay: 900, preset: 'slide', x: -20 }}>Most often, <strong>the data is familiar</strong> ground, meaning that it is data that you have already collected and know the limitations of</li>
				<li use:reveal={{ delay: 1100, preset: 'slide', x: -20 }}>It might be dashboards to share the data, or story telling to highlight some key (published) ideas to the broader public</li>
			</ul>
		</div>
		
		<div class="divider" use:reveal={{ delay: 800 }}>
			<div class="vertical-line"></div>
		</div>
		
		<div class="image-section" use:reveal={{ delay: 1200, preset: 'scale', scale: 0.9 }}>
			<a href="{base}/networks-fast-and-slow" target="_blank" rel="noopener">
				<img src="{base}/common/thumbnails/screenshots/networks-fast-and-slow.jpg" alt="Networks Fast and Slow Project">
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