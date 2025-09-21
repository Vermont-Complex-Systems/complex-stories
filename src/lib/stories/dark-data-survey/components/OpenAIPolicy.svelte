<script>
	let { onAnswer = () => {} } = $props();
	let selectedAnswer = $state('');

	function handleAnswerSelect(answer) {
		selectedAnswer = answer;
		onAnswer(answer);
	}
</script>

<div class="openai-policy">
	<!-- Mobile Safari status bar -->
	<div class="status-bar">
		<div class="status-left">
			<div class="signal-bars">
				<div class="bar"></div>
				<div class="bar"></div>
				<div class="bar full"></div>
				<div class="bar full"></div>
			</div>
			<span class="carrier">Fido</span>
			<svg class="wifi" width="15" height="15" viewBox="0 0 24 24" fill="none">
				<path d="M1.42 9C4.15 6.42 7.84 5 12 5s7.85 1.42 10.58 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
				<path d="M5 13c2.12-1.6 4.77-2.5 7-2.5s4.88.9 7 2.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
				<path d="M8.5 16.5c1.61-1.21 3.64-1.9 5.5-1.9s3.89.69 5.5 1.9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
				<circle cx="12" cy="20" r="1" fill="currentColor"/>
			</svg>
		</div>
		
		<div class="status-center">
			<svg class="lock-icon" width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
				<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
				<circle cx="12" cy="16" r="1"/>
				<path d="M7 11V7a5 5 0 0 1 10 0v4"/>
			</svg>
			<span class="time">9:19 PM</span>
		</div>
		
		<div class="status-right">
			<svg class="bluetooth" width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
				<path d="M6.5 6.5L17.5 17.5L12 23L12 1L17.5 6.5L6.5 17.5"/>
			</svg>
			<span class="battery-percent">3%</span>
			<div class="battery">
				<div class="battery-level low"></div>
				<svg class="charging" width="10" height="10" viewBox="0 0 24 24" fill="currentColor">
					<polygon points="13,2 3,14 12,14 11,22 21,10 12,10"/>
				</svg>
			</div>
		</div>
	</div>

	<!-- Safari toolbar -->
	<div class="safari-toolbar">
		<div class="toolbar-left">
			<svg class="openai-logo" width="24" height="24" viewBox="0 0 24 24" fill="none">
				<path d="M12 2L13.09 8.26L22 9L13.09 9.74L12 16L10.91 9.74L2 9L10.91 8.26L12 2Z" stroke="currentColor" stroke-width="1.5" fill="none"/>
			</svg>
		</div>
		<div class="toolbar-right">
			<svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
				<circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
				<path d="M21 21L16.65 16.65" stroke="currentColor" stroke-width="2"/>
			</svg>
			<svg class="tabs-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
				<rect x="3" y="3" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
				<rect x="7" y="7" width="10" height="10" rx="1" ry="1" stroke="currentColor" stroke-width="1.5"/>
			</svg>
		</div>
	</div>

	<!-- Page content -->
	<div class="content">
		<div class="scroll-indicator"></div>
		
		<h1>1. Personal Data we collect</h1>
		
		<p class="intro-text">
			We collect personal data relating to you ("Personal Data") as follows:
		</p>
		
		<div class="section">
			<p class="section-title">Personal Data You Provide:</p>
			<p class="section-text">Does the platform matter for your privacy decisions?</p>
		</div>

		<div class="data-points">
			<button class="data-point" class:selected={selectedAnswer === 'yes'} onclick={() => handleAnswerSelect('yes')}>
				<span class="bullet">•</span>
				<div class="point-content">
					<span class="point-text"><strong class="survey-answer">Yes, platform matters</strong> - When you create an account with us, we will collect information associated with your account, including your name, contact information, account credentials, date of birth, payment info, transaction history, (collectively, "Account Information").</span>
				</div>
			</button>

			<button class="data-point" class:selected={selectedAnswer === 'no'} onclick={() => handleAnswerSelect('no')}>
				<span class="bullet">•</span>
				<div class="point-content">
					<span class="point-text"><strong class="survey-answer">No, same across platforms</strong> - Information you provide when you interact with our Services, including through our website, mobile applications, or other interfaces we may offer.</span>
				</div>
			</button>

			<button class="data-point" class:selected={selectedAnswer === 'sometimes'} onclick={() => handleAnswerSelect('sometimes')}>
				<span class="bullet">•</span>
				<div class="point-content">
					<span class="point-text"><strong class="survey-answer">Sometimes</strong> - Data we collect from third-party services when you choose to connect your account with those services, subject to your privacy settings and the privacy policies of such third parties.</span>
				</div>
			</button>
		</div>

		<!-- ChatGPT prompt overlay -->
		<div class="chatgpt-overlay">
			<div>
				<span class="chatgpt-prompt">Ask ChatGPT</span>
				<div class="chatgpt-arrow">
					<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
						<path d="M7 14l5-5 5 5z"/>
					</svg>
				</div>
			</div>
		</div>
	</div>

	<!-- Safari bottom toolbar -->
	<div class="safari-bottom">
		<div class="url-bar">
			<span class="text-size">aA</span>
			<div class="url-section">
				<svg class="lock-small" width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
					<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
					<circle cx="12" cy="16" r="1"/>
					<path d="M7 11V7a5 5 0 0 1 10 0v4"/>
				</svg>
				<span class="url">openai.com</span>
			</div>
			<svg class="refresh" width="16" height="16" viewBox="0 0 24 24" fill="none">
				<path d="M1 4v6h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				<path d="M23 20v-6h-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				<path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
			</svg>
		</div>
		
		<div class="nav-controls">
			<svg class="nav-back" width="24" height="24" viewBox="0 0 24 24" fill="none">
				<path d="M19 12H5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				<path d="M12 19l-7-7 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
			</svg>
			<svg class="nav-forward" width="24" height="24" viewBox="0 0 24 24" fill="none">
				<path d="M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				<path d="M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
			</svg>
			<svg class="share" width="24" height="24" viewBox="0 0 24 24" fill="none">
				<path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				<polyline points="16,6 12,2 8,6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				<line x1="12" y1="2" x2="12" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
			</svg>
			<svg class="bookmarks" width="24" height="24" viewBox="0 0 24 24" fill="none">
				<path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
			</svg>
			<svg class="tabs" width="24" height="24" viewBox="0 0 24 24" fill="none">
				<rect x="3" y="3" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
				<rect x="7" y="7" width="10" height="10" rx="1" ry="1" stroke="currentColor" stroke-width="1.5"/>
			</svg>
		</div>
	</div>
</div>

<style>
	.openai-policy {
		width: 375px;
		height: 812px;
		margin: 0 auto;
		background-color: #ffffff;
		font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
		color: #000000;
		overflow: hidden;
		border: 8px solid #1a1a1a;
		border-radius: 40px;
		box-shadow: 0 0 0 2px #333, 0 20px 60px rgba(0, 0, 0, 0.4);
		position: relative;
	}

	.openai-policy::before {
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
		.openai-policy {
			width: 100vw;
			height: 100vh;
			margin: 0;
			border: none;
			border-radius: 0;
			box-shadow: none;
		}

		.openai-policy::before {
			display: none;
		}
	}

	/* Status bar */
	.status-bar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 8px 20px 4px 20px;
		font-size: 14px;
		font-weight: 600;
		color: #000000;
		background: #ffffff;
		padding-top: 32px;
	}

	@media (max-width: 768px) {
		.status-bar {
			padding-top: 8px;
		}
	}

	.status-left {
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
		background: #000000;
		border-radius: 1px;
	}

	.bar.full {
		height: 6px;
	}

	.carrier {
		font-size: 14px;
		margin-left: 4px;
	}

	.wifi {
		color: #000000;
	}

	.status-center {
		display: flex;
		align-items: center;
		gap: 4px;
	}

	.lock-icon {
		color: #000000;
	}

	.time {
		font-size: 14px;
		font-weight: 600;
	}

	.status-right {
		display: flex;
		align-items: center;
		gap: 4px;
	}

	.bluetooth {
		color: #000000;
	}

	.battery-percent {
		font-size: 14px;
	}

	.battery {
		width: 24px;
		height: 12px;
		border: 1px solid #000000;
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
		height: 6px;
		background: #000000;
		border-radius: 0 1px 1px 0;
	}

	.battery-level {
		height: 8px;
		background: #ff3b30;
		border-radius: 1px;
		margin: 1px;
		width: 20%;
	}

	.battery-level.low {
		background: #ff3b30;
	}

	.charging {
		position: absolute;
		right: 2px;
		color: #ffffff;
		z-index: 1;
	}

	/* Safari toolbar */
	.safari-toolbar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 8px 20px;
		background: #f8f9fa;
		border-bottom: 1px solid #e5e5e7;
	}

	.toolbar-left .openai-logo {
		color: #000000;
	}

	.toolbar-right {
		display: flex;
		gap: 16px;
	}

	.search-icon, .tabs-icon {
		color: #007aff;
	}

	/* Content */
	.content {
		padding: 24px 20px;
		background: #ffffff;
		height: calc(100% - 200px);
		overflow-y: auto;
		position: relative;
	}

	.scroll-indicator {
		position: absolute;
		right: 2px;
		top: 20px;
		width: 3px;
		height: 60px;
		background: #c7c7cc;
		border-radius: 2px;
		opacity: 0.8;
	}

	h1 {
		font-size: 28px;
		font-weight: 700;
		margin: 0 0 20px 0;
		line-height: 1.2;
		color: #000000;
	}

	.intro-text {
		font-size: 16px;
		line-height: 1.5;
		margin: 0 0 20px 0;
		color: #888888;
		opacity: 0.6;
	}

	.section {
		margin: 20px 0;
	}

	.section-title {
		font-size: 16px;
		font-weight: 600;
		margin: 0 0 8px 0;
		color: #888888;
		opacity: 0.6;
	}

	.section-text {
		font-size: 16px;
		line-height: 1.5;
		margin: 0;
		color: #000000;
		font-weight: 600;
	}

	.data-points {
		margin: 20px 0;
	}

	.data-point {
		display: flex;
		align-items: flex-start;
		gap: 12px;
		margin: 16px 0;
		background: none;
		border: none;
		text-align: left;
		width: 100%;
		cursor: pointer;
		padding: 12px;
		border-radius: 8px;
		transition: background-color 0.2s;
	}

	.data-point:hover {
		background-color: #f0f0f0;
	}

	.data-point.selected {
		background-color: #e3f2fd;
		border: 2px solid #007aff;
	}

	.bullet {
		font-size: 16px;
		color: #000000;
		margin-top: 2px;
		min-width: 8px;
	}

	.point-content {
		flex: 1;
	}


	.point-text {
		font-size: 16px;
		line-height: 1.5;
		color: #888888;
		opacity: 0.6;
	}

	.survey-answer {
		color: #000000 !important;
		opacity: 1 !important;
		font-weight: 700;
	}

	/* ChatGPT overlay */
	.chatgpt-overlay {
		margin-top: 40px;
		margin-bottom: 20px;
		display: flex;
		justify-content: center;
		align-items: center;
	}

	.chatgpt-overlay > div {
		background: rgba(0, 0, 0, 0.8);
		color: #ffffff;
		padding: 8px 16px;
		border-radius: 20px;
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 14px;
		font-weight: 500;
	}

	.chatgpt-prompt {
		white-space: nowrap;
	}

	.chatgpt-arrow {
		color: #ffffff;
	}

	/* Safari bottom toolbar */
	.safari-bottom {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		background: #f8f9fa;
		border-top: 1px solid #e5e5e7;
		padding: 8px 20px 12px 20px;
	}

	.url-bar {
		display: flex;
		align-items: center;
		background: #ffffff;
		border: 1px solid #e5e5e7;
		border-radius: 8px;
		padding: 8px 12px;
		margin-bottom: 8px;
		gap: 8px;
	}

	.text-size {
		font-size: 16px;
		font-weight: 600;
		color: #000000;
	}

	.url-section {
		flex: 1;
		display: flex;
		align-items: center;
		gap: 6px;
		justify-content: center;
	}

	.lock-small {
		color: #34c759;
	}

	.url {
		font-size: 14px;
		color: #000000;
	}

	.refresh {
		color: #007aff;
	}

	.nav-controls {
		display: flex;
		justify-content: space-around;
		align-items: center;
	}

	.nav-back, .nav-forward, .share, .bookmarks, .tabs {
		color: #007aff;
		cursor: pointer;
	}

	.nav-back {
		opacity: 0.3;
	}

	@media (prefers-color-scheme: dark) {
		.openai-policy {
			background-color: #000000;
			color: #ffffff;
		}

		.status-bar {
			background: #000000;
			color: #ffffff;
		}

		.bar, .wifi, .lock-icon, .bluetooth, .battery::after {
			background: #ffffff;
			color: #ffffff;
		}

		.safari-toolbar, .safari-bottom {
			background: #1c1c1e;
			border-color: #38383a;
		}

		.content {
			background: #000000;
		}

		h1, .intro-text, .section-title, .section-text, .point-text {
			color: #ffffff;
		}

		.bullet {
			color: #ffffff;
		}

		.data-point:hover {
			background-color: #1c1c1e;
		}

		.data-point.selected {
			background-color: #1a3a5c;
			border-color: #0a84ff;
		}

		.url-bar {
			background: #2c2c2e;
			border-color: #38383a;
		}

		.text-size, .url {
			color: #ffffff;
		}
	}
</style>