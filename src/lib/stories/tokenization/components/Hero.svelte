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
						By <a href="https://jstonge.vercel.app/about">Julia Zimmerman</a> and
						<a href="">Ben Cooley</a>.
					</p>
					<p>Language is a human skill. Computers were historically very bad at language...until LLMs came along.</p>
				</div>
			</div>
			<div class="hero-visual">
				<div class="placeholder-content">
					<!-- Your visualization component will go here -->
					hello
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
	   VISUAL ELEMENTS
	   ============================================================================= */

	.placeholder-content {
		background: rgba(255, 255, 255, 0.1);
		border: 2px solid var(--color-border);
		border-radius: var(--border-radius);
		padding: 2rem;
		text-align: center;
		backdrop-filter: blur(5px);
		box-shadow: 0 4px 20px rgba(59, 47, 30, 0.1);
		min-height: 200px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-family: var(--font-body);
		color: var(--color-secondary-gray);
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

		.placeholder-content {
			padding: 1.5rem;
			min-height: 150px;
		}
	}
</style>