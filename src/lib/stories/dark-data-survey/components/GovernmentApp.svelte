<script>
	let { onAnswer = () => {} } = $props();
	let selectedAnswer = $state('');

	function handleAnswerSelect(answer) {
		selectedAnswer = answer;
		onAnswer(answer);
	}
</script>

<div class="government-app">
	<!-- iOS Status bar -->
	<div class="status-bar">
		<div class="status-left">
			<span class="time">12:55</span>
		</div>
		<div class="status-center">
			<div class="notch"></div>
		</div>
		<div class="status-right">
			<div class="signal-bars">
				<div class="bar full"></div>
				<div class="bar full"></div>
				<div class="bar full"></div>
				<div class="bar"></div>
			</div>
			<svg class="wifi" width="15" height="11" viewBox="0 0 15 11" fill="currentColor">
				<path d="M1.5 3.5C3.5 1.5 6 0.5 7.5 0.5S11.5 1.5 13.5 3.5M4 6C5 5 6.2 4.5 7.5 4.5S10 5 11 6M6.5 8.5C7 8 7.2 7.5 7.5 7.5S8 8 8.5 8.5M7.5 10.5C7.5 10.5 7.5 10.5 7.5 10.5"/>
			</svg>
			<div class="battery">
				<div class="battery-level"></div>
			</div>
		</div>
	</div>

	<!-- Header with Canada branding -->
	<div class="header">
		<div class="header-content">
			<button class="back-button" aria-label="Go back">
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
					<path d="M19 12H5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					<path d="M12 19l-7-7 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</button>
		</div>
	</div>

	<!-- Main content -->
	<div class="content">
		<h1>Do your privacy preferences vary by institution type?</h1>
		<p class="subtitle">Select from one of the following.</p>

		<div class="options">
			<button class="option" class:selected={selectedAnswer === 'vary-greatly'} onclick={() => handleAnswerSelect('vary-greatly')}>
				<div class="radio-button">
					<div class="radio-inner" class:selected={selectedAnswer === 'vary-greatly'}></div>
				</div>
				<div class="option-content">
					<h3>Vary greatly</h3>
					<p>My privacy preferences change significantly between social media platforms, government services, police interactions, and other institutions based on their data handling practices and trustworthiness.</p>
				</div>
			</button>

			<button class="option" class:selected={selectedAnswer === 'mostly-same'} onclick={() => handleAnswerSelect('mostly-same')}>
				<div class="radio-button">
					<div class="radio-inner" class:selected={selectedAnswer === 'mostly-same'}></div>
				</div>
				<div class="option-content">
					<h3>Mostly the same</h3>
					<p>I maintain similar privacy preferences across most institutions including social media, government, and law enforcement, with only minor adjustments based on the specific service.</p>
				</div>
			</button>

			<button class="option" class:selected={selectedAnswer === 'depends-context'} onclick={() => handleAnswerSelect('depends-context')}>
				<div class="radio-button">
					<div class="radio-inner" class:selected={selectedAnswer === 'depends-context'}></div>
				</div>
				<div class="option-content">
					<h3>Depends on context</h3>
					<p>My privacy choices vary based on the specific context and purpose of data collection, whether it's social media platforms, government services, or police interactions, rather than the institution type alone.</p>
				</div>
			</button>
		</div>

		<div class="bottom-section">
			<button class="continue-button" disabled={!selectedAnswer}>
				Save & Close
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none">
					<path d="M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					<path d="M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</button>
		</div>
	</div>

	<div class="bottom-indicator">
		<div class="indicator-bar"></div>
	</div>
</div>

<style>
	.government-app {
		width: 375px;
		height: 812px;
		margin: 0 auto;
		background-color: #ffffff;
		font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', system-ui, sans-serif;
		color: #000000;
		overflow: hidden;
		border: 8px solid #1a1a1a;
		border-radius: 40px;
		box-shadow: 0 0 0 2px #333, 0 20px 60px rgba(0, 0, 0, 0.4);
		position: relative;
		display: flex;
		flex-direction: column;
	}

	.government-app::before {
		content: '';
		position: absolute;
		top: 15px;
		left: 50%;
		transform: translateX(-50%);
		width: 140px;
		height: 6px;
		background: #1a1a1a;
		border-radius: 3px;
		z-index: 1000;
	}

	@media (max-width: 768px) {
		.government-app {
			width: 100vw;
			height: 100vh;
			margin: 0;
			border: none;
			border-radius: 0;
			box-shadow: none;
		}

		.government-app::before {
			display: none;
		}

		.status-bar {
			padding-top: 8px;
			position: fixed;
			top: 0;
			left: 0;
			right: 0;
			width: 100vw;
			z-index: 999;
		}

		.header {
			position: fixed;
			top: 52px;
			left: 0;
			right: 0;
			width: 100vw;
			z-index: 998;
		}

		.content {
			padding-top: 100px;
			padding-bottom: 60px;
			padding-left: 12px;
			padding-right: 12px;
		}

		h1 {
			font-size: 18px !important;
			line-height: 1.1 !important;
		}

		.subtitle {
			font-size: 13px !important;
			margin-bottom: 16px !important;
		}

		.options {
			gap: 8px !important;
			margin-bottom: 16px !important;
		}

		.option {
			padding: 10px !important;
			gap: 8px !important;
		}

		.option-content h3 {
			font-size: 14px !important;
			margin-bottom: 3px !important;
		}

		.option-content p {
			font-size: 12px !important;
			line-height: 1.2 !important;
		}

		.continue-button {
			padding: 10px 16px !important;
			font-size: 13px !important;
			min-width: 100px !important;
		}

		.bottom-section {
			margin-top: 12px !important;
		}

		.bottom-indicator {
			position: fixed;
			bottom: 0;
			left: 0;
			right: 0;
			width: 100vw;
			z-index: 1000;
		}
	}

	/* Status bar */
	.status-bar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 8px 20px 0 20px;
		font-size: 14px;
		font-weight: 600;
		color: #ffffff;
		background: linear-gradient(135deg, #1E4A5F 0%, #2B5A6B 100%);
		padding-top: 32px;
		min-height: 44px;
	}


	.status-left .time {
		font-weight: 600;
	}

	.status-center .notch {
		width: 120px;
		height: 2px;
		background: rgba(255, 255, 255, 0.3);
		border-radius: 1px;
	}

	.status-right {
		display: flex;
		align-items: center;
		gap: 4px;
	}

	.signal-bars {
		display: flex;
		gap: 2px;
		align-items: flex-end;
	}

	.bar {
		width: 3px;
		height: 4px;
		background: rgba(255, 255, 255, 0.5);
		border-radius: 1px;
	}

	.bar.full {
		background: #ffffff;
		height: 6px;
	}

	.wifi {
		color: #ffffff;
	}

	.battery {
		width: 22px;
		height: 11px;
		border: 1px solid #ffffff;
		border-radius: 2px;
		position: relative;
		display: flex;
		align-items: center;
	}

	.battery::after {
		content: '';
		position: absolute;
		right: -3px;
		top: 3px;
		width: 2px;
		height: 5px;
		background: #ffffff;
		border-radius: 0 1px 1px 0;
	}

	.battery-level {
		height: 7px;
		background: #ffffff;
		border-radius: 1px;
		margin: 1px;
		width: 70%;
	}

	/* Header */
	.header {
		background: linear-gradient(135deg, #1E4A5F 0%, #2B5A6B 100%);
		padding: 12px 20px;
	}

	.header-content {
		display: flex;
		align-items: center;
	}

	.back-button {
		background: none;
		border: none;
		color: #ffffff;
		cursor: pointer;
		padding: 8px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.back-button:hover {
		background: rgba(255, 255, 255, 0.1);
	}

	/* Content */
	.content {
		flex: 1;
		padding: 16px 16px;
		background: #ffffff;
		overflow-y: auto;
	}

	h1 {
		font-size: 22px;
		font-weight: 700;
		margin: 0 0 6px 0;
		color: rgb(57, 57, 57);
		line-height: 1.1;
	}

	.subtitle {
		font-size: 14px;
		color: #666666;
		margin: 0 0 20px 0;
		line-height: 1.2;
	}

	.options {
		display: flex;
		flex-direction: column;
		gap: 12px;
		margin-bottom: 20px;
	}

	.option {
		display: flex;
		align-items: flex-start;
		gap: 10px;
		padding: 12px;
		background: #ffffff;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.2s ease;
		text-align: left;
	}

	.option:hover {
		border-color: #2B5A6B;
		box-shadow: 0 2px 8px rgba(44, 95, 94, 0.1);
	}

	.option.selected {
		border-color: #2B5A6B;
		background: #f0f8f8;
		box-shadow: 0 2px 8px rgba(44, 95, 94, 0.15);
	}

	.radio-button {
		width: 20px;
		height: 20px;
		border: 2px solid #c7c7cc;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-top: 2px;
		flex-shrink: 0;
		transition: border-color 0.2s ease;
	}

	.option.selected .radio-button {
		border-color: #2B5A6B;
	}

	.radio-inner {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		background: transparent;
		transition: background-color 0.2s ease;
	}

	.radio-inner.selected {
		background: #2B5A6B;
	}

	.option-content {
		flex: 1;
	}

	.option-content h3 {
		font-size: 16px;
		font-weight: 600;
		margin: 0 0 4px 0;
		color: rgb(57, 57, 57);
		line-height: 1.2;
	}

	.option-content p {
		font-size: 13px;
		line-height: 1.25;
		color: #666666;
		margin: 0;
	}

	.bottom-section {
		display: flex;
		justify-content: center;
		margin-top: 16px;
	}

	.continue-button {
		background: #2B5A6B;
		color: #ffffff;
		border: none;
		padding: 12px 20px;
		border-radius: 20px;
		font-size: 14px;
		font-weight: 600;
		cursor: pointer;
		display: flex;
		align-items: center;
		gap: 6px;
		transition: all 0.2s ease;
		min-width: 120px;
		justify-content: center;
	}

	.continue-button:hover:not(:disabled) {
		background: #1e4544;
		transform: translateY(-1px);
	}

	.continue-button:disabled {
		background: #c7c7cc;
		cursor: not-allowed;
		transform: none;
	}


	/* Bottom indicator */
	.bottom-indicator {
		background: linear-gradient(135deg, #ffffff 0%, #ffffff 100%);
		padding: 8px 20px;
		display: flex;
		justify-content: center;
	}

	.indicator-bar {
		width: 134px;
		height: 5px;
		background: rgba(255, 255, 255, 0.3);
		border-radius: 3px;
	}

	@media (prefers-color-scheme: dark) {
		.content {
			background: #1c1c1e;
		}

		h1 {
			color: #4a8b8a;
		}

		.subtitle {
			color: #8e8e93;
		}

		.option {
			background: #2c2c2e;
			border-color: #48484a;
		}

		.option.selected {
			background: #1e3432;
			border-color: #4a8b8a;
		}

		.option-content h3 {
			color: #4a8b8a;
		}

		.option-content p {
			color: #8e8e93;
		}

		.radio-button {
			border-color: #8e8e93;
		}

		.option.selected .radio-button {
			border-color: #4a8b8a;
		}

		.radio-inner.selected {
			background: #4a8b8a;
		}
	}
</style>