<script>
	import { getCurrentUser } from '$lib/api/auth.remote';
	import { getYearlyStats } from './data.remote';
	import { Plot, BarY, RuleY, Text } from 'svelteplot';

	let selectedYear = $state(null);
	let selectedFormat = $state('ndjson');
	let isDownloading = $state(false);

	const availableYears = Array.from({length: 34}, (_, i) => 2024 - i); // 2024 down to 2000

	async function handleDownload() {
		isDownloading = true;
		try {
			// Create a form to trigger download with proper authentication
			const form = document.createElement('form');
			form.method = 'GET';
			form.action = '/datasets/s2orc-arxiv/download';
			form.target = '_blank';
			form.style.display = 'none';

			// Add format parameter
			const formatInput = document.createElement('input');
			formatInput.type = 'hidden';
			formatInput.name = 'format';
			formatInput.value = selectedFormat;
			form.appendChild(formatInput);

			// Add year parameter if selected
			if (selectedYear) {
				const yearInput = document.createElement('input');
				yearInput.type = 'hidden';
				yearInput.name = 'year';
				yearInput.value = selectedYear;
				form.appendChild(yearInput);
			}

			document.body.appendChild(form);
			form.submit();
			document.body.removeChild(form);
		} catch (error) {
			console.error('Failed to download dataset:', error);
		} finally {
			isDownloading = false;
		}
	}
</script>

<div class="dataset-header">
	<h1>S2ORC arXiv Full Text Dataset</h1>
	<p class="dataset-description">
		Complete arXiv papers with full text and structured annotations from the Semantic Scholar Open Research Corpus (S2ORC).
		This dataset provides access to over 700,000 arXiv papers with extracted text and bibliography references.
	</p>
</div>

<div class="content-wrapper">
	<!-- Dataset Stats -->
		{#await getYearlyStats()}
			<div class="stats-section">
				<h2>Dataset Statistics</h2>
				<p>Loading statistics...</p>
			</div>
		{:then datasetStats}
			{@const chartData = Object.entries(datasetStats.yearly_stats)
				.sort(([a], [b]) => a.localeCompare(b))
				.map(([year, stats]) => ({
					year: year,
					papers: stats.papers,
					size_gb: Number(((stats.papers * stats.avg_text_length * 1.2) / (1024 ** 3)).toFixed(1))
				}))}

			<div class="stats-section">
				<h2>Dataset Statistics</h2>
				<div class="stats-grid">
					<div class="stat-card">
						<div class="stat-value">{datasetStats.total_papers.toLocaleString()}</div>
						<div class="stat-label">Total Papers</div>
					</div>
					<div class="stat-card">
						<div class="stat-value">{datasetStats.estimated_size.gb.toFixed(1)}GB</div>
						<div class="stat-label">Estimated Size</div>
					</div>
					<div class="stat-card">
						<div class="stat-value">{(datasetStats.avg_text_length / 1000).toFixed(1)}k</div>
						<div class="stat-label">Avg Text Length (chars)</div>
					</div>
					<div class="stat-card">
						<div class="stat-value">NDJSON</div>
						<div class="stat-label">Format</div>
					</div>
				</div>
			</div>

			<div class="stats-section">
				<h2>Papers by Year</h2>
				<Plot
					y={{ grid: true }}
					x={{ tickRotate: 25, label: 'Year' }}
					marginTop={40}
					marginRight={25}
					height={350}
				>
					<BarY
						data={chartData}
						x="year"
						y="papers"
						fill="#2563eb"
						stroke="grey"
					/>

					<Text
						data={chartData}
						x="year"
						y="papers"
						text={(d) => `${d.size_gb}GB`}
						fill="white"
						fontSize={8}
						fontWeight="bold"
						textAnchor="middle"
						dy={8}
					/>

					<RuleY data={[0]} />
				</Plot>
			</div>
		{:catch error}
			<div class="error-section">
				<h2>Error Loading Statistics</h2>
				<p>{error.message}</p>
			</div>
		{/await}

		{#await getCurrentUser()}
			<div class="loading-section">
				<h2>Loading...</h2>
				<p>Checking authentication...</p>
			</div>
		{:then currentUser}
			{#if !currentUser}
				<div class="auth-section">
					<div class="auth-message">
						<h2>Authentication Required</h2>
						<p>Please log in to access the S2ORC arXiv dataset.</p>
					</div>
					<a href="/auth" class="login-button">Log In</a>
				</div>
			{:else}
				<!-- Download Section -->
				<div class="download-section">
					<h2>Download Dataset</h2>

					<div class="download-form">
						<div class="input-group">
							<label for="year">Filter by Year (optional):</label>
							<select id="year" bind:value={selectedYear}>
								<option value={null}>All Years</option>
								{#each availableYears as year}
									<option value={year}>{year}</option>
								{/each}
							</select>
						</div>

						<button
							class="btn btn-primary btn-large"
							onclick={handleDownload}
							disabled={isDownloading}
						>
							{#if isDownloading}
								Downloading...
							{:else}
								Download Dataset
								{#if selectedYear}
									({selectedYear})
								{/if}
							{/if}
						</button>
					</div>

				</div>

				<!-- Data Schema -->
				<div class="schema-section">
					<h2>Data Schema</h2>
					<p>Each record contains the following fields:</p>

					<div class="schema-table">
						<table>
							<thead>
								<tr>
									<th>Field</th>
									<th>Type</th>
									<th>Description</th>
								</tr>
							</thead>
							<tbody>
								<tr>
									<td><code>corpusid</code></td>
									<td>integer</td>
									<td>Semantic Scholar corpus ID</td>
								</tr>
								<tr>
									<td><code>year</code></td>
									<td>integer</td>
									<td>Publication year</td>
								</tr>
								<tr>
									<td><code>arxiv_id</code></td>
									<td>string</td>
									<td>arXiv identifier</td>
								</tr>
								<tr>
									<td><code>text</code></td>
									<td>string</td>
									<td>Full extracted paper text</td>
								</tr>
								<tr>
									<td><code>annotations</code></td>
									<td>object</td>
									<td>Structured annotations including bibliography references</td>
								</tr>
								<tr>
									<td><code>text_length</code></td>
									<td>integer</td>
									<td>Length of extracted text in characters</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>
				
				<!-- User Info -->
				<div class="user-section">
					<p>Authenticated as: {currentUser.payroll_name || currentUser.email}</p>
					<p>Role: {currentUser.role}</p>
				</div>

			{/if}
		{:catch error}
			<div class="error-section">
				<h2>Authentication Error</h2>
				<p>{error.message}</p>
				<a href="/auth" class="login-button">Try Logging In</a>
			</div>
		{/await}
</div>

<style>
	:global(main#content:has(.dataset-header)) {
		max-width: none;
		padding: 0 !important;
	}

	.dataset-header {
		padding: 7rem var(--margin-left) 0.5rem var(--margin-left);
		text-align: left;
		margin-bottom: 2rem;
	}

	.dataset-header h1 {
		font-family: var(--mono);
		font-size: clamp(1.5rem, 3vw, 2rem);
		font-weight: var(--font-weight-bold);
		color: var(--color-fg);
		margin: 0 0 1rem 0;
	}

	.dataset-description {
		font-family: var(--mono);
		font-size: var(--font-size-medium);
		color: var(--color-secondary-gray);
		margin-bottom: 1.5rem;
		line-height: 1.6;
	}

	.content-wrapper {
		padding: 0 var(--margin-left);
	}

	/* Mobile responsive */
	@media (max-width: 768px) {
		.dataset-header {
			padding: 1.5rem var(--margin-left-mobile);
			text-align: left;
		}

		.content-wrapper {
			padding: 0 var(--margin-left-mobile);
		}
	}

	.stats-section,
	.loading-section,
	.auth-section,
	.error-section,
	.download-section,
	.schema-section,
	.user-section {
		margin-bottom: 3rem;
		padding: 2rem;
		background: rgba(255, 255, 255, 0.8);
		border: 1px solid var(--color-border);
		border-radius: 8px;
	}

	.loading-section, .auth-section, .error-section {
		text-align: center;
	}

	.auth-message h2, .error-section h2, .loading-section h2 {
		color: #333;
		margin-bottom: 1rem;
	}

	.auth-message p, .error-section p, .loading-section p {
		color: #666;
		margin-bottom: 1.5rem;
	}

	.error-section {
		background: #ffebee;
		border-color: #e57373;
	}

	.error-section h2 {
		color: #d32f2f;
	}

	.error-section p {
		color: #c62828;
	}

	.login-button {
		display: inline-block;
		background: #2196f3;
		color: white;
		padding: 0.75rem 1.5rem;
		border-radius: 4px;
		text-decoration: none;
		font-weight: 500;
		transition: background 0.2s;
	}

	.login-button:hover {
		background: #1976d2;
	}

	.stats-section h2,
	.download-section h2,
	.schema-section h2 {
		font-family: var(--sans);
		font-size: var(--font-size-large);
		font-weight: var(--font-weight-bold);
		color: var(--color-fg);
		margin: 0 0 1.5rem 0;
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: 1rem;
	}

	.stat-card {
		text-align: center;
		padding: 1rem;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: 6px;
	}

	.stat-value {
		font-family: var(--mono);
		font-size: var(--font-size-xlarge);
		font-weight: var(--font-weight-bold);
		color: var(--color-fg);
		margin-bottom: 0.5rem;
	}

	.stat-label {
		font-family: var(--sans);
		font-size: var(--font-size-small);
		color: var(--color-secondary-gray);
	}

	.download-form {
		margin-bottom: 2rem;
	}


	.input-group {
		margin-bottom: 1rem;
	}

	.input-group label {
		display: block;
		font-family: var(--sans);
		font-size: var(--font-size-small);
		font-weight: var(--font-weight-medium);
		color: var(--color-fg);
		margin-bottom: 0.5rem;
	}

	.input-group select {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid var(--color-border);
		border-radius: 4px;
		font-family: var(--mono);
		font-size: var(--font-size-small);
		background: var(--color-bg);
		color: var(--color-fg);
	}

	.btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 0.75rem 1.5rem;
		border-radius: 4px;
		font-family: var(--sans);
		font-size: var(--font-size-small);
		font-weight: var(--font-weight-medium);
		text-decoration: none;
		cursor: pointer;
		border: none;
		transition: all var(--transition-medium);
	}

	.btn-primary {
		background: var(--color-button-bg);
		color: var(--color-button-fg);
	}

	.btn-primary:hover:not(:disabled) {
		background: var(--color-button-hover);
		transform: translateY(-1px);
	}

	.btn-large {
		padding: 1rem 2rem;
		font-size: var(--font-size-medium);
	}

	.btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}



	.schema-table table {
		width: 100%;
		border-collapse: collapse;
		margin-top: 1rem;
	}

	.schema-table th,
	.schema-table td {
		padding: 0.75rem;
		text-align: left;
		border-bottom: 1px solid var(--color-border);
	}

	.schema-table th {
		background: var(--color-bg-alt);
		font-weight: var(--font-weight-semibold);
		color: var(--color-fg);
	}

	.schema-table code {
		background: var(--color-bg-alt);
		padding: 0.25rem 0.5rem;
		border-radius: 3px;
		font-family: var(--mono);
		font-size: var(--font-size-xsmall);
	}


	.user-section {
		margin-top: 2rem;
		padding: 1rem;
		background: #f5f5f5;
		border-radius: 8px;
		border: 1px solid #ddd;
	}

	.user-section p {
		margin: 0.5rem 0;
		color: #666;
		font-size: 0.9rem;
	}

	@media (max-width: 768px) {
		.stats-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	/* Dark mode */
	:global(.dark) .stats-section,
	:global(.dark) .loading-section,
	:global(.dark) .auth-section,
	:global(.dark) .download-section,
	:global(.dark) .schema-section,
	:global(.dark) .user-section {
		background: rgba(30, 30, 30, 0.8);
		border-color: rgba(255, 255, 255, 0.1);
	}

	:global(.dark) .stat-card {
		background: rgba(20, 20, 20, 0.8);
		border-color: rgba(255, 255, 255, 0.1);
	}
</style>