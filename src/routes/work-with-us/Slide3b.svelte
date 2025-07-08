<script>
	import { reveal } from 'svelte-reveal';
	import Label from './Label.svelte';
	import { base } from "$app/paths";
</script>

<div class="slide">
	<div class="container">
		<div class="content-section" use:reveal={{ delay: 100 }}>
			<Label variant="secondary">"6" months projects</Label>
			<p use:reveal={{ delay: 300 }}>Collection of reusable software components and libraries for academic research workflows.</p>
			<ul>
				<li use:reveal={{ delay: 500, preset: 'slide', x: -20 }}>You might have an idea for a project that is based on others' work. We might need to collect <strong>new data</strong>, or <strong>deploying an online platform</strong> with dashboards.</li>
				<li use:reveal={{ delay: 700, preset: 'slide', x: -20 }}>We can work together to <strong>adopt sustainable programming practices from the outset</strong>, saving time and effort in the long run.</li>
				<li use:reveal={{ delay: 900, preset: 'slide', x: -20 }}>We can use prior digital infrastructure that we have already developed at VERSO, such as deploying a virtual machine to host dashboards, or sharing data through an Application Programming Interface (API).</li>
			</ul>
		</div>
		
		<div class="divider" use:reveal={{ delay: 800 }}>
			<div class="vertical-line"></div>
		</div>
		
		<div class="image-section" use:reveal={{ delay: 1200, preset: 'scale', scale: 0.9 }}>
			<div class="image-stack">
				<!-- Primary image (top/front) -->
				<a href="{base}/open-academic-analytics" target="_blank" rel="noopener" class="image-link primary">
					<img src="{base}/common/thumbnails/screenshots/open-academic-analytics.jpg" alt="Open Academic Analytics Project" />
				</a>
				
				<a href="https://verso-uvm.github.io/Vermont-Livability-Map/" target="_blank" rel="noopener" class="image-link secondary">
					<img src="{base}/common/thumbnails/screenshots/vermont-livability-map.jpg" alt="Project 2" />
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
		max-width: 300px; /* Increased from 300px */
		min-height: 280px; /* Added min-height to accommodate spread */
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
		transform: translateX(102px) translateY(0) rotateY(0deg);
	}
	
	.image-link.secondary {
		z-index: 2;
		transform: translateX(-40px) translateY(25px) rotateY(-12deg);
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
			max-width: 280px; /* Increased from 250px */
		}
		
		/* Keep some spread even on mobile */
		.image-link.secondary {
			transform: translateX(-15px) translateY(12px) rotateY(-5deg);
		}
		
	}
</style>