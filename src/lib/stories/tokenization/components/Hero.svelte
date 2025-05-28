

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
		<div class="centered-layout">
			<div class="text-side">
				<h1>Tokenization: The Oft Overlooked Appetizer</h1>
				<div class="text-block">
					<p>
						By <a href="https://jstonge.vercel.app/about">Julia Zimmerman</a> and
						<a href="">Ben Cooley</a>.
					</p>
					<p>Language is a human skill. Computers were historically very bad at language...until LLMs came along.</p>
					
				</div>
			</div>
			<div class="plot-side">
				hello
			</div>
		</div>
	</div>
</div>

<style>
	.hero-banner {
		display: flex;
		justify-content: center;
		align-items: center;
		flex-direction: column;
		min-height: 100vh;
		padding: 2rem 0;
		position: relative;
		box-sizing: border-box;
	}

	.github-link {
		position: absolute;
		top: 1rem;
		right: 1rem;
		z-index: 3;
	}

	.github-link img {
		width: 40px;
		height: 40px;
		transition: transform 0.2s ease;
	}

	.github-link img:hover {
		transform: scale(1.1);
	}

	.hero-content {
		max-width: 1100px;
		width: 90%;
		margin: 0 auto;
	}

	.centered-layout {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 2rem;
	}

	.text-side {
		max-width: 600px;
		text-align: left;
	}

	.hero-content h1 {
		font-size: 3rem;
		font-weight: bold;
		color: #1a1a1a;
	}

	.text-block {
		margin-top: 3rem;
		color: #1a1a1a;
		font-size: 1.3rem;
		line-height: 1.3;
	}

	.text-block p {
		margin-top: 1rem;
	}

	.text-block a {
		color: #1a1a1a;
		text-decoration: underline;
	}

	.plot-side {
		transform: translateY(150px);
	}

	.ball-count {
		display: flex;
		justify-content: center;
		margin-bottom: 1rem;
		font-size: 1.1rem;
	}

	.chart-container {
		position: relative;
		margin: 1rem auto;
		border: 2px solid #000;
		border-radius: 6px;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
		max-height: 450px;
		max-width: 350px;
	}

	@media (max-width: 1200px) {
		.centered-layout {
			flex-direction: column;
			align-items: center;
			gap: 1rem;
		}

		.text-side {
			max-width: 90%;
			text-align: center;
		}

		.plot-side {
			transform: none;
		}

		.hero-content h1 {
			text-align: center;
		}

		.text-block p {
			text-align: left;
		}
	}
</style>