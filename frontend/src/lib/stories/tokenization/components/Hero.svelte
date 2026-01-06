<script>
	import { base } from '$app/paths';
	import imgUrl from '../assets/julia-illos/Tbook1.png?url'
</script>

<div class="hero-banner">
	<a
		class="github-link"
		href="https://github.com/Vermont-Complex-Systems/complex-stories"
		target="_blank"
		rel="noopener noreferrer"
	>
		<img
			src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
			alt="GitHub Logo"
		/>
	</a>

	<div class="hero-content">
		<div class="hero-layout">
			<div class="hero-text">
				<h1>Tokenization: The Oft Overlooked Appetizer</h1>
				<h3 class="construction-note">Note: this story is still under construction!</h3>
				<div class="hero-description">
					<p>
						By <a href="{base}/author/julia-witte-zimmerman">Julia Zimmerman</a> and
						<a href="{base}/author/ben-dexter-cooley">Ben Cooley</a>.
					</p>
					<p>Language is a human skill. Computers were historically very bad at language...until LLMs came along.</p>
				</div>
			</div>
			<div class="hero-visual">
				<div>
					<!-- Your visualization component will go here -->
					<img src={imgUrl} alt="Hero Visual" />
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	/* =============================================================================
	   HERO LAYOUT
	   
	   Uses design tokens from the parent story theme
	   ============================================================================= */
	
	.hero-banner {
		display: flex;
		justify-content: center;
		align-items: center;
		flex-direction: column;
		min-height: 100vh;
		width: 100%;
		padding: 2rem 0;
		position: relative;
		box-sizing: border-box;
		/* Inherit background from parent story theme */
	}

	.github-link {
		position: absolute;
		top: 1rem;
		right: 1rem;
		z-index: var(--z-top);
		transition: transform var(--transition-fast);
	}

	.github-link:hover {
		transform: scale(1.1);
	}

	.github-link img {
		width: 40px;
		height: 40px;
		border-radius: var(--border-radius);
		box-shadow: 0 2px 8px rgba(59, 47, 30, 0.2);
	}

	.hero-content {
		max-width: var(--width-column-wide);
		width: 90%;
		margin: 0 auto;
		padding: 0 1rem;
	}

	.hero-layout {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 3rem;
	}

	.hero-text {
		flex: 1;
		max-width: 600px;
	}

	.hero-visual {
		flex: 0 0 350px;
		transform: translateY(150px);
		/* Apply blending to the container */
		mix-blend-mode: multiply;
		opacity: 0.8;
		filter: sepia(0.15) brightness(0.95) contrast(1.05);
		/* Ensure the container doesn't create a new stacking context that blocks blending */
		isolation: auto;
	}

	.hero-visual img {
		width: 100%;
		height: auto;
		display: block;
	}

	/* =============================================================================
	   TYPOGRAPHY
	   
	   Uses semantic design tokens with story-specific overrides
	   ============================================================================= */

	.hero-banner h1 {
		font-size: var(--font-size-giant);
		font-family: var(--sans);
		font-weight: var(--font-weight-bold);
		color: var(--color-fg);
		line-height: 1.1;
		margin: 0 0 1rem 0;
		text-wrap: balance;
	}

	.construction-note {
		font-size: var(--font-size-medium);
		color: #d21e1e; /* Brownish-orange that fits parchment */
		font-style: italic;
		font-weight: var(--font-weight-normal);
		margin: 0 0 2rem 0;
	}

	.hero-description {
		font-size: var(--font-size-medium);
		line-height: 1.6;
		color: var(--color-fg);
	}

	.hero-description p {
		margin: 1rem 0;
	}

	.hero-description a {
		color: var(--color-link);
		text-decoration: underline;
		text-decoration-color: var(--color-link);
		transition: all var(--transition-fast);
	}

	.hero-description a:hover {
		color: var(--color-link-hover);
		text-decoration-color: var(--color-link-hover);
	}


	/* =============================================================================
	   RESPONSIVE DESIGN
	   ============================================================================= */

	@media (max-width: 1200px) {
		.hero-layout {
			flex-direction: column;
			align-items: center;
			gap: 2rem;
			text-align: center;
		}

		.hero-text {
			max-width: 90%;
		}

		.hero-visual {
			transform: none;
			flex: 0 0 auto;
			width: 100%;
			max-width: 400px;
		}

		.hero-description {
			text-align: left;
		}
	}

	@media (max-width: 768px) {
		.hero-banner {
			padding: 1rem 0;
			min-height: 90vh;
		}

		.hero-content {
			width: 95%;
		}

		.hero-banner h1 {
			font-size: var(--font-size-xlarge);
		}

		.construction-note {
			font-size: var(--font-size-small);
		}

		.hero-description {
			font-size: var(--font-size-small);
		}

		.github-link {
			top: 0.5rem;
			right: 0.5rem;
		}

		.github-link img {
			width: 32px;
			height: 32px;
		}
	}

	@media (max-width: 480px) {
		.hero-layout {
			gap: 1.5rem;
		}

		.hero-banner h1 {
			font-size: var(--font-size-large);
		}

		.hero-description {
			font-size: var(--font-size-smallish);
		}

	}
</style>