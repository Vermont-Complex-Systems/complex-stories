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
			<div class="image-stack">
				<!-- Primary image (top/front) -->
				<a href="{base}/networks-fast-and-slow" class="image-link primary">
					<img src="{base}/common/thumbnails/screenshots/networks-fast-and-slow.jpg" alt="Networks Fast and Slow Project" />
				</a>
				
				<!-- Secondary images (stacked behind) -->
				<a href="{base}/allotax-scrolly" class="image-link secondary">
					<img src="{base}/common/thumbnails/screenshots/allotax-scrolly.jpg" alt="Analytics Project" />
				</a>
				
			</div>
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
	
	/* Image stacking with CSS Grid - WIDER CONTAINER */
	.image-stack {
		display: grid;
		grid-template-areas: "stack";
		max-width: 300px;
		min-height: 280px;
		perspective: 1000px; /* For 3D effect */
	}
	
	.image-link {
		grid-area: stack;
		display: block;
		transition: all 0.3s ease;
		transform-style: preserve-3d;
	}
	
	.image-link img {
		width: 100%;
		height: auto;
		border-radius: 8px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		display: block;
	}
	
	/* Stacking order and positioning - MORE SPREAD */
	.image-link.primary {
		z-index: 2;
		transform: translateX(70px) translateY(0) rotateY(0deg);
	}
	
	.image-link.secondary {
		z-index: 2;
		transform: translateX(-70px) translateY(25px) rotateY(-12deg);
	}
	
	/* Hover effects - MORE DRAMATIC */
	.image-stack:hover .image-link.primary {
		transform: translateX(20px) translateY(-10px) rotateY(8deg);
	}
	
	.image-stack:hover .image-link.secondary {
		transform: translateX(-20px) translateY(15px) rotateY(-5deg);
	}
	
	
	/* Individual image hover */
	.image-link:hover {
		z-index: 10 !important;
		transform: translateX(0) translateY(-10px) rotateY(0deg) scale(1.05) !important;
		opacity: 1 !important;
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
		
		/* Simplify stack on smaller screens but keep spread */
		.image-link.secondary {
			transform: translateX(-25px) translateY(15px) rotateY(-8deg);
		}
		

	}
	
	@media (max-width: 768px) {
		.image-stack {
			max-width: 280px;
		}
		
		/* Keep some spread even on mobile */
		.image-link.secondary {
			transform: translateX(-15px) translateY(12px) rotateY(-5deg);
		}
		
	}
</style>