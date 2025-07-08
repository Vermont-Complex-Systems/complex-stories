<script>
	import { reveal } from 'svelte-reveal';
	import Label from './Label.svelte';
</script>

<div class="container">
	<div class="docs" use:reveal={{ delay: 1000 }}>
		<Label variant="success">Our community</Label>
		<ul>
            <li use:reveal={{ delay: 1200, preset: 'slide', x: -20 }}><a href="https://curioss.org/" target="_blank" rel="noopener noreferrer">
                Community for University and Research Institution OSPOs (CURIOSS)
            </a>
            </li>
			<li use:reveal={{ delay: 1400, preset: 'fly', y: -20 }}>
				<a href="https://numfocus.org/" target="_blank" rel="noopener noreferrer">
					NumFOCUS - Supporting open source scientific computing
				</a>
			</li>
			<li use:reveal={{ delay: 1600, preset: 'slide', x: -20 }}>
				<a href="https://pydata.org/vermont2024/" target="_blank" rel="noopener noreferrer">
					PyData Vermont 2024 Conference
				</a>
			</li>
			<li use:reveal={{ delay: 1800, preset: 'slide', x: -20 }}>
				<a href="https://www.cscce.org/" target="_blank" rel="noopener noreferrer">
					CSCCE - Center for Scientific Collaboration and Community Engagement
				</a>
			</li>
		</ul>	
	</div>
	
	<div class="image-container" use:reveal={{ delay: 2000, preset: 'scale', scale: 0.7 }}>
	<div class="image-wrapper">
		<img src="{base}/community-69fc3b40333659ebf12e64e787bf03e4.jpg" alt="community" />
		<div class="copyright" use:reveal={{ delay: 2100, preset: 'fade' }}>
			<p>
				<em>The Turing Way</em> community illustrated as a garden. 
				<em>The Turing Way</em> project illustration by Scriberia. 
				Used under a CC-BY 4.0 licence. 
				DOI: The Turing Way Community & Scriberia (2024).
			</p>
		</div>
	</div>
	</div>
</div>

<style>
	.container {
		display: grid;
		grid-template-columns: 0.7fr 1fr;
		gap: 2rem;
		align-items: start;
	}
	
	.docs {
		display: block;
		padding-bottom: 1rem;
	}
	
	.image-container {
		display: flex;
		justify-content: center;
		align-items: flex-start;
		padding-top: 2rem;
	}
	
	img {
		width: 100%;
		min-width: 300px;
		height: auto;
		border-radius: 8px;
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	}
	
	li {
		line-height: 1.5;
		margin-bottom: 0.75rem;
	}
	
	/* Link styling */
	a {
		color: #667eea;
		text-decoration: none;
		font-weight: 500;
		border-bottom: 2px solid transparent;
		transition: all 0.2s ease;
		display: inline-block;
	}
	
	a:hover {
		color: #5a67d8;
		border-bottom-color: #667eea;
		transform: translateY(-1px);
	}
	
	a:active {
		transform: translateY(0);
	}
	
	/* External link icon */
	a[target="_blank"]::after {
		content: " ↗";
		font-size: 0.8em;
		opacity: 0.7;
		margin-left: 0.2em;
	}
	
	/* Responsive design */
	@media (max-width: 768px) {
		.container {
			grid-template-columns: 1fr;
			gap: 1rem;
		}
		
		.image-container {
			order: -1;
			padding-top: 0;
		}
		
		img {
			min-width: 250px;
		}
		
		li {
			margin-bottom: 1rem;
		}
	}
</style>