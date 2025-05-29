<script>
	import BouncingBalls from "./Bouncing.svelte";
	let numBalls = $state(50);
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
		<div class="centered-layout">
			<div class="text-side">
				<h1>Networks, Fast and Slow</h1>
				<div class="text-block">
					<p>
						By <a href="https://jstonge.vercel.app/about">Jonathan St-Onge</a> and
						<a href="https://www.uvm.edu/socks/node/38?rnd=0.8126330183365708#giulioburgio">Giulio Burgio</a>.
					</p>
					<p>
						During Covid-19, the Washington Post published the
						<a href="https://www.washingtonpost.com/graphics/2020/world/corona-simulator/">
							corona-simulator
						</a>. The animation took place in the quintessential simulation world; the billiard ball world. It examined how different public health measures influenced the dynamics of the system: what if people practiced social distancing, or quarantined when sick?
					</p>
					<p>
						With networks, we can represent how social structures shape the dynamics of contagion. Who talks to whom, who touches whom, who works or lives with whom — all of that matters.
					</p>
					<p>
						Some interactions are fleeting, like a conversation with a stranger on a train. Others are deeply persistent, like sharing a household or workplace. These differences matter — and they define two fundamentally different modeling regimes:
						<strong>
							<a href="https://en.wikipedia.org/wiki/Simulated_annealing">annealed</a>
						</strong>
						and
						<strong>
							<a href="https://en.wikipedia.org/wiki/Quenching">quenched</a>
						</strong>
						networks.
					</p>
				</div>
			</div>
			<div class="plot-side">
				<label class="ball-count">
					Ball count
					<input type="range" bind:value={numBalls} min="1" max="100" />
					{numBalls}
				</label>
				<div class="chart-container">
					<BouncingBalls width={350} height={350} {numBalls} />
				</div>
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