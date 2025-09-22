<script>
	let { scrollyIndex = 0, onAnswer = () => {} } = $props();
	let answers = $state({
		step0: '',
		step1: '',
		step2: '',
		step3: ''
	});

	function handleAnswer(step, answer) {
		answers[step] = answer;
		onAnswer(step, answer);
	}

	// Import the individual content components (we'll extract content from existing components)
</script>

<div class="unified-phone">
	<!-- Phone frame - renders all content with transitions -->
	
	<!-- Facebook Settings Content -->
	<div class="phone-content facebook-content" class:active={scrollyIndex === 0}>
			<!-- iOS Status bar -->
			<div class="status-bar">
				<div class="status-left">
					<span class="time">9:41</span>
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

			<!-- Facebook header -->
			<header class="header">
				<button class="back-btn" aria-label="Go back">
					<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
						<path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
				</button>
				<h1 class="title">Settings & privacy</h1>
				<button class="search-btn" aria-label="Search">
					<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
						<circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
						<path d="M21 21L16.65 16.65" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
				</button>
			</header>

			<!-- Facebook content -->
			<div class="content">
				<div class="search-bar">
					<input type="text" placeholder="Search settings" />
				</div>

				<div class="card">
					<div class="card-header">
						<div class="meta-logo">
							<svg width="20" height="20" viewBox="0 0 24 24" fill="none">
								<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="#1877F2"/>
							</svg>
							<span>The Book of faces platform</span>
						</div>
					</div>
					
					<h2 class="card-title">Privacy Settings</h2>
					<p class="card-description">
						How do you typically set your social media privacy?
					</p>

					<div class="menu-items">
						<button class="menu-item" class:selected={answers.step0 === 'private'} onclick={() => handleAnswer('step0', 'private')}>
							<div class="menu-icon">
								<svg width="20" height="20" viewBox="0 0 24 24" fill="none">
									<rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" stroke-width="1.5"/>
									<circle cx="12" cy="16" r="1" stroke="currentColor" stroke-width="1.5"/>
									<path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
							</div>
							<span>Private</span>
							<div class="chevron">
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none">
									<path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
							</div>
						</button>

						<button class="menu-item" class:selected={answers.step0 === 'mixed'} onclick={() => handleAnswer('step0', 'mixed')}>
							<div class="menu-icon">
								<svg width="20" height="20" viewBox="0 0 24 24" fill="none">
									<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
									<circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
							</div>
							<span>Mixed</span>
							<div class="chevron">
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none">
									<path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
							</div>
						</button>

						<button class="menu-item" class:selected={answers.step0 === 'public'} onclick={() => handleAnswer('step0', 'public')}>
							<div class="menu-icon">
								<svg width="20" height="20" viewBox="0 0 24 24" fill="none">
									<circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5"/>
									<path d="M2 12h20" stroke="currentColor" stroke-width="1.5"/>
									<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" stroke="currentColor" stroke-width="1.5"/>
								</svg>
							</div>
							<span>Public</span>
							<div class="chevron">
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none">
									<path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
							</div>
						</button>

						<button class="menu-item" class:selected={answers.step0 === 'depends'} onclick={() => handleAnswer('step0', 'depends')}>
							<div class="menu-icon">
								<svg width="20" height="20" viewBox="0 0 24 24" fill="none">
									<circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.5"/>
									<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1 1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" stroke="currentColor" stroke-width="1.5"/>
								</svg>
							</div>
							<span>It depends</span>
							<div class="chevron">
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none">
									<path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
							</div>
						</button>
					</div>
				</div>

				<div class="separator"></div>

				<div class="section">
					<h2 class="section-title">Tools and resources</h2>
					<p class="section-description">
						Our tools help you control and manage your privacy.
					</p>

					<div class="menu-items">
						<div class="menu-item-static">
							<div class="menu-icon">
								<svg width="20" height="20" viewBox="0 0 24 24" fill="none">
									<rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" stroke-width="1.5"/>
									<circle cx="12" cy="16" r="1" stroke="currentColor" stroke-width="1.5"/>
									<path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
							</div>
							<span>Privacy Checkup</span>
						</div>

						<div class="menu-item-static">
							<div class="menu-icon">
								<svg width="20" height="20" viewBox="0 0 24 24" fill="none">
									<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
									<circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
									<path d="M23 21v-2a4 4 0 0 0-3-3.87" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
									<path d="M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
							</div>
							<span>Family Center</span>
						</div>
					</div>
				</div>
			</div>

			<!-- Facebook bottom nav -->
			<nav class="bottom-nav">
				<div class="nav-item">
					<div class="nav-icon">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
							<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" stroke="currentColor" stroke-width="1.5"/>
							<polyline points="9,22 9,12 15,12 15,22" stroke="currentColor" stroke-width="1.5"/>
						</svg>
					</div>
					<span class="nav-label">Home</span>
				</div>

				<div class="nav-item">
					<div class="nav-icon">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
							<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="1.5"/>
							<circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="1.5"/>
							<path d="M23 21v-2a4 4 0 0 0-3-3.87" stroke="currentColor" stroke-width="1.5"/>
							<path d="M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" stroke-width="1.5"/>
						</svg>
					</div>
					<span class="nav-label">Friends</span>
					<div class="nav-badge">1</div>
				</div>

				<div class="nav-item">
					<div class="nav-icon">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
							<path d="M7 4V2a1 1 0 0 1 1-1h8a1 1 0 0 1 1 1v2" stroke="currentColor" stroke-width="1.5"/>
							<path d="M5 7h14l-1 10a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 7z" stroke="currentColor" stroke-width="1.5"/>
						</svg>
					</div>
					<span class="nav-label">Marketplace</span>
				</div>

				<div class="nav-item">
					<div class="nav-icon">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
							<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="1.5"/>
							<circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="1.5"/>
						</svg>
					</div>
					<span class="nav-label">Profile</span>
				</div>

				<div class="nav-item">
					<div class="nav-icon">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
							<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="currentColor" stroke-width="1.5"/>
							<path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" stroke-width="1.5"/>
						</svg>
					</div>
					<span class="nav-label">Notifications</span>
					<div class="nav-badge">5</div>
				</div>

				<div class="nav-item active">
					<div class="nav-icon">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
							<line x1="3" y1="6" x2="21" y2="6" stroke="currentColor" stroke-width="2"/>
							<line x1="3" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2"/>
							<line x1="3" y1="18" x2="21" y2="18" stroke="currentColor" stroke-width="2"/>
						</svg>
					</div>
					<span class="nav-label">Menu</span>
				</div>
			</nav>
	</div>
	
	<!-- Safari/OpenAI Content -->
	<div class="phone-content safari-content" class:active={scrollyIndex === 1}>
			<!-- iOS Status bar -->
			<div class="status-bar safari-status">
				<div class="status-left">
					<span class="time">9:41</span>
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

			<!-- Safari UI -->
			<div class="safari-header">
				<div class="address-bar">
					<div class="url-container">
						<div class="lock-icon">
							<svg width="12" height="12" viewBox="0 0 24 24" fill="none">
								<rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
								<circle cx="12" cy="16" r="1" stroke="currentColor" stroke-width="2"/>
								<path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="currentColor" stroke-width="2"/>
							</svg>
						</div>
						<span class="url">openai.com/policies/privacy-policy</span>
					</div>
					<button class="refresh-btn" aria-label="Refresh page">
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none">
							<polyline points="23,4 23,10 17,10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
							<polyline points="1,20 1,14 7,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
							<path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</button>
				</div>
			</div>

			<!-- OpenAI Content -->
			<div class="safari-content">
				<div class="openai-header">
					<h1>Artifical General Intelligence Co. Privacy Policy</h1>
					<p class="last-updated">Last updated: March 14, 2023</p>
				</div>

				<div class="privacy-section">
					<h2>Platform Privacy Preferences</h2>
					<p class="question-text">Does the platform matter for your privacy decisions?</p>
					
					<div class="bullet-options">
						<button class="bullet-option" class:selected={answers.step1 === 'yes'} onclick={() => handleAnswer('step1', 'yes')}>
							<span class="bullet">•</span>
							<div class="text-content">
								<strong>Yes, platform matters</strong>
								<span>Different platforms have varying data policies and trustworthiness levels</span>
							</div>
						</button>

						<button class="bullet-option" class:selected={answers.step1 === 'no'} onclick={() => handleAnswer('step1', 'no')}>
							<span class="bullet">•</span>
							<div class="text-content">
								<strong>No, same across platforms</strong>
								<span>I maintain consistent privacy preferences regardless of platform</span>
							</div>
						</button>

						<button class="bullet-option" class:selected={answers.step1 === 'sometimes'} onclick={() => handleAnswer('step1', 'sometimes')}>
							<span class="bullet">•</span>
							<div class="text-content">
								<strong>Sometimes</strong>
								<span>Context and specific features matter more than the platform itself</span>
							</div>
						</button>
					</div>

					<div class="ask-chatgpt">
						<button class="chatgpt-btn">Ask friendlyGPT</button>
					</div>
				</div>
			</div>

			<!-- Safari bottom indicator -->
			<div class="bottom-indicator">
				<div class="indicator-bar"></div>
			</div>
	</div>
	
	<!-- Government App Content -->
	<div class="phone-content government-content" class:active={scrollyIndex === 2}>
			<!-- Government status bar -->
			<div class="status-bar government-status">
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

			<!-- Government header -->
			<div class="government-header">
				<div class="header-content">
					<button class="back-button" aria-label="Go back">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
							<path d="M19 12H5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
							<path d="M12 19l-7-7 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</button>
				</div>
			</div>

			<!-- Government content -->
			<div class="government-main-content">
				<h1>Do your privacy preferences vary by institution type?</h1>
				<p class="subtitle">Select from one of the following.</p>

				<div class="gov-options">
					<button class="gov-option" class:selected={answers.step2 === 'vary-greatly'} onclick={() => handleAnswer('step2', 'vary-greatly')}>
						<div class="radio-button">
							<div class="radio-inner" class:selected={answers.step2 === 'vary-greatly'}></div>
						</div>
						<div class="option-content">
							<h3>Vary greatly</h3>
							<p>My privacy preferences change significantly between social media platforms, government services, police interactions, and other institutions based on their data handling practices and trustworthiness.</p>
						</div>
					</button>

					<button class="gov-option" class:selected={answers.step2 === 'mostly-same'} onclick={() => handleAnswer('step2', 'mostly-same')}>
						<div class="radio-button">
							<div class="radio-inner" class:selected={answers.step2 === 'mostly-same'}></div>
						</div>
						<div class="option-content">
							<h3>Mostly the same</h3>
							<p>I maintain similar privacy preferences across most institutions including social media, government, and law enforcement, with only minor adjustments based on the specific service.</p>
						</div>
					</button>

					<button class="gov-option" class:selected={answers.step2 === 'depends-context'} onclick={() => handleAnswer('step2', 'depends-context')}>
						<div class="radio-button">
							<div class="radio-inner" class:selected={answers.step2 === 'depends-context'}></div>
						</div>
						<div class="option-content">
							<h3>Depends on context</h3>
							<p>My privacy choices vary based on the specific context and purpose of data collection, whether it's social media platforms, government services, or police interactions, rather than the institution type alone.</p>
						</div>
					</button>
				</div>

				<div class="bottom-section">
					<button class="continue-button" disabled={!answers.step2}>
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

	<!-- Step 3: Demographics question -->
	<div class="phone-content demographics-content" class:active={scrollyIndex >= 3}>
			<div class="content">
				<h1>Personal Demographics</h1>
				<p class="subtitle">Do demographics (who you are) influence your privacy preferences?</p>

				<div class="demo-options">
					<button class="demo-option" class:selected={answers.step3 === 'yes'} onclick={() => handleAnswer('step3', 'yes')}>
						<div class="option-content">
							<h3>Yes, who I am matters</h3>
							<p>My background, identity, and circumstances significantly influence my privacy decisions</p>
						</div>
					</button>

					<button class="demo-option" class:selected={answers.step3 === 'no'} onclick={() => handleAnswer('step3', 'no')}>
						<div class="option-content">
							<h3>No, preferences are universal</h3>
							<p>Privacy preferences are consistent regardless of personal demographics</p>
						</div>
					</button>

					<button class="demo-option" class:selected={answers.step3 === 'somewhat'} onclick={() => handleAnswer('step3', 'somewhat')}>
						<div class="option-content">
							<h3>Somewhat</h3>
							<p>Some aspects of who I am influence certain privacy decisions but not others</p>
						</div>
					</button>
				</div>
			</div>
	</div>
</div>

<style>
	.unified-phone {
		width: 375px;
		height: 812px;
		margin: 0 auto;
		background-color: #f8f9fa;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		color: #1c1e21;
		overflow: hidden;
		border: 8px solid #1a1a1a;
		border-radius: 40px;
		box-shadow: 0 0 0 2px #333, 0 20px 60px rgba(0, 0, 0, 0.4);
		position: relative;
	}

	.unified-phone::before {
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
		.unified-phone {
			width: 100vw;
			height: 100vh;
			margin: 0;
			border: none;
			border-radius: 0;
			box-shadow: none;
		}

		.unified-phone::before {
			display: none;
		}
	}

	/* Base phone styles */
	.phone-content {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		display: flex;
		flex-direction: column;
		background: #f8f9fa;
		opacity: 0;
		transform: translateX(100%);
		transition: all 0.8s cubic-bezier(0.25, 0.1, 0.25, 1);
		pointer-events: none;
		will-change: transform, opacity;
		overflow: hidden; /* Prevent any scrolling within phone */
	}
	
	.phone-content.active {
		opacity: 1;
		transform: translateX(0);
		pointer-events: auto;
	}
	
	/* Specific entrance animations for different content types */
	.facebook-content {
		transform: translateX(-100%);
		transition-delay: 0.1s;
	}
	
	.safari-content {
		transform: scale(0.9) translateY(-50px);
		transition: all 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94);
	}
	
	.government-content {
		transform: translateX(100%);
		transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
	}
	
	.demographics-content {
		transform: translateY(100%) scale(0.95);
		transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
	}
	
	.facebook-content.active,
	.safari-content.active,
	.government-content.active,
	.demographics-content.active {
		transform: translateX(0) translateY(0) scale(1);
	}
	
	/* Add a subtle loading/transition effect */
	.phone-content {
		overflow: hidden;
	}
	
	.phone-content::before {
		content: '';
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 100%;
		background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
		transition: left 0.8s;
		z-index: 1000;
		pointer-events: none;
	}
	
	.phone-content.active::before {
		left: 100%;
	}

	/* Status bar styles */
	.status-bar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 8px 20px 0 20px;
		font-size: 14px;
		font-weight: 600;
		color: #000000;
		background: #ffffff;
		padding-top: 32px;
		min-height: 44px;
		transition: all 0.4s ease;
	}

	.safari-status {
		background: #f6f6f6;
	}

	.government-status {
		background: linear-gradient(135deg, #1E4A5F 0%, #2B5A6B 100%);
		color: #ffffff;
	}

	.status-left .time {
		font-weight: 600;
	}

	.status-center .notch {
		width: 120px;
		height: 2px;
		background: rgba(0, 0, 0, 0.3);
		border-radius: 1px;
	}

	.government-status .notch {
		background: rgba(255, 255, 255, 0.3);
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
		background: rgba(0, 0, 0, 0.5);
		border-radius: 1px;
	}

	.government-status .bar {
		background: rgba(255, 255, 255, 0.5);
	}

	.bar.full {
		background: #000000;
		height: 6px;
	}

	.government-status .bar.full {
		background: #ffffff;
	}

	.wifi {
		color: #000000;
	}

	.government-status .wifi {
		color: #ffffff;
	}

	.battery {
		width: 22px;
		height: 11px;
		border: 1px solid #000000;
		border-radius: 2px;
		position: relative;
		display: flex;
		align-items: center;
	}

	.government-status .battery {
		border-color: #ffffff;
	}

	.battery::after {
		content: '';
		position: absolute;
		right: -3px;
		top: 3px;
		width: 2px;
		height: 5px;
		background: #000000;
		border-radius: 0 1px 1px 0;
	}

	.government-status .battery::after {
		background: #ffffff;
	}

	.battery-level {
		height: 7px;
		background: #000000;
		border-radius: 1px;
		margin: 1px;
		width: 70%;
	}

	.government-status .battery-level {
		background: #ffffff;
	}

	/* Facebook content styles */
	.facebook-content .header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 12px 16px;
		background-color: #ffffff;
		border-bottom: 1px solid #e4e6ea;
	}

	.back-btn, .search-btn {
		background: none;
		border: none;
		padding: 8px;
		cursor: pointer;
		color: #1c1e21;
		border-radius: 50%;
		transition: background-color 0.2s;
	}

	.back-btn:hover, .search-btn:hover {
		background-color: #f2f3f5;
	}

	.title {
		font-size: 20px;
		font-weight: 600;
		margin: 0;
		flex: 1;
		text-align: center;
	}

	.facebook-content .content {
		padding: 8px 12px;
		gap: 8px;
		display: flex;
		flex-direction: column;
		flex: 1;
		overflow: hidden;
		max-height: calc(100% - 60px - 56px); /* Account for header and bottom nav */
	}

	.search-bar {
		background-color: #f0f2f5;
		border-radius: 20px;
		padding: 8px 12px;
	}

	.search-bar input {
		background: none;
		border: none;
		width: 100%;
		font-size: 16px;
		color: #65676b;
		outline: none;
	}

	.card {
		background-color: #ffffff;
		border-radius: 12px;
		padding: 12px;
		box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
		flex: 1;
		min-height: 0; /* Allow flex shrinking */
	}

	.meta-logo {
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 14px;
		font-weight: 600;
		color: #1877f2;
	}

	.card-title {
		font-size: 17px;
		font-weight: 600;
		margin: 6px 0;
		color: #1c1e21;
		text-align: left;
	}

	.card-description {
		font-size: 14px;
		color: #65676b;
		margin: 0 0 16px 0;
		line-height: 1.3;
		text-align: left;
	}

	.menu-items {
		display: flex;
		flex-direction: column;
		gap: 1px;
		flex: 1;
		overflow: hidden;
	}

	.menu-item {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 8px 0;
		font-size: 15px;
		color: #1c1e21;
		background: none;
		border: none;
		width: 100%;
		text-align: left;
		cursor: pointer;
		border-radius: 6px;
		transition: background-color 0.2s;
		justify-content: space-between;
		min-height: 36px;
		flex-shrink: 0;
	}

	.menu-item:hover {
		background-color: #f2f3f5;
	}

	.menu-item.selected {
		background-color: #e3f2fd;
		color: #1877f2;
	}

	.menu-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 20px;
		height: 20px;
		color: #65676b;
	}

	.chevron {
		opacity: 0.6;
	}

	.menu-item.selected .chevron {
		opacity: 1;
		color: #1877f2;
	}

	.separator {
		height: 1px;
		background-color: #e4e6ea;
		margin: 16px;
	}

	.section {
		margin: 0 16px 16px 16px;
	}

	.section-title {
		font-size: 17px;
		font-weight: 600;
		margin: 0 0 6px 0;
		color: #1c1e21;
		text-align: left;
		opacity: 0.2;
	}

	.section-description {
		font-size: 14px;
		color: #65676b;
		margin: 0 0 16px 0;
		line-height: 1.3;
		text-align: left;
		opacity: 0.2;
	}

	.menu-item-static {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 10px 0;
		font-size: 16px;
		color: #1c1e21;
		min-height: 44px;
		opacity: 0.2;
	}

	.bottom-nav {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		background-color: #ffffff;
		border-top: 1px solid #e4e6ea;
		display: flex;
		justify-content: space-around;
		align-items: center;
		padding: 8px 0 12px 0;
		height: 60px;
	}

	.nav-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 4px;
		flex: 1;
		cursor: pointer;
		position: relative;
		padding: 4px;
	}

	.nav-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 24px;
		height: 24px;
		color: #65676b;
	}

	.nav-label {
		font-size: 10px;
		color: #65676b;
		font-weight: 400;
		text-align: center;
	}

	.nav-item.active .nav-icon {
		color: #1877f2;
	}

	.nav-item.active .nav-label {
		color: #1877f2;
		font-weight: 500;
	}

	.nav-badge {
		position: absolute;
		top: -2px;
		right: 8px;
		background-color: #e41e3f;
		color: white;
		border-radius: 10px;
		padding: 2px 6px;
		font-size: 10px;
		font-weight: 600;
		min-width: 16px;
		height: 16px;
		display: flex;
		align-items: center;
		justify-content: center;
		border: 2px solid #ffffff;
	}

	/* Safari content styles */
	.safari-content {
		background: #ffffff;
		flex: 1;
		display: flex;
		flex-direction: column;
		height: 100%;
		overflow: hidden;
	}

	.safari-header {
		background: #f6f6f6;
		padding: 8px 16px;
		border-bottom: 1px solid #e5e5e7;
		margin: 0;
		flex-shrink: 0;
		position: relative;
		z-index: 1;
	}

	.address-bar {
		display: flex;
		align-items: center;
		gap: 8px;
		background: #ffffff;
		border-radius: 10px;
		padding: 8px 12px;
		border: 1px solid #d1d1d6;
	}

	.url-container {
		display: flex;
		align-items: center;
		gap: 6px;
		flex: 1;
	}

	.lock-icon {
		color: #34c759;
	}

	.url {
		font-size: 14px;
		color: #1c1c1e;
		font-weight: 400;
	}

	.refresh-btn {
		background: none;
		border: none;
		color: #007aff;
		cursor: pointer;
		padding: 4px;
	}

	.phone-content.safari-content .safari-content {
		flex: 1;
		overflow: hidden;
		padding: 16px;
		display: flex;
		flex-direction: column;
		justify-content: flex-start;
		position: relative;
	}

	.openai-header {
		margin-top: 4rem;
		opacity: 0.2;
	}

	.openai-header h1 {
		font-size: 24px;
		font-weight: 700;
		color: #1a1a1a;
		margin: 0 0 4px 0;
	}

	.last-updated {
		font-size: 13px;
		color: #666666;
		margin-bottom: 12px;
	}

	.privacy-section {
		flex: 1;
		display: flex;
		flex-direction: column;
		overflow: hidden;
		justify-content: space-between;
	}

	.privacy-section h2 {
		font-size: 19px;
		font-weight: 600;
		color: #1a1a1a;
		margin: 0 0 8px 0;
	}

	.question-text {
		color: #1a1a1a;
		margin-bottom: 12px;
		line-height: 1.4;
	}

	.bullet-options {
		display: flex;
		flex-direction: column;
		font-size: 22px;
		flex: 1;
		overflow: hidden;
	}

	.bullet-option {
		display: flex;
		align-items: flex-start;
		gap: 10px;
		padding: 14px;
		background: white;
		border: 2px solid transparent;
		border-radius: 8px;
		cursor: pointer;
		text-align: left;
		transition: all 0.2s ease;
		flex-shrink: 0;
	}

	.bullet-option:hover {
		background: #e9ecef;
	}

	.bullet-option.selected {
		background: #e3f2fd;
		border-color: #007aff;
	}

	.bullet {
		font-size: 20px;
		color: black;
		font-weight: bold;
		margin-top: 1px;
		flex-shrink: 0;
	}

	.text-content {
		display: block;
		line-height: 1.4;
	}

	.text-content strong {
		font-size: 15px;
		font-weight: normal;
		font-style: italic;
		color: #1a1a1a;
	}

	.text-content span {
		font-size: 15px;
		color: #1a1a1a;
		font-weight: normal;
	}
	
	.text-content span::before {
		content: ": ";
		color: #1a1a1a;
	}

	.ask-chatgpt {
		display: flex;
		justify-content: center;
		margin-top: 16px;
		flex-shrink: 0;
	}

	.chatgpt-btn {
		background: lightgrey;
		color: white;
		border: none;
		padding: 14px 28px;
		border-radius: 8px;
		font-size: 15px;
		font-weight: 600;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	/* Government content styles */
	.government-content {
		background-color: #ffffff;
		color: #000000;
	}

	.government-header {
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

	.government-main-content {
		flex: 1;
		padding: 12px;
		overflow: hidden;
		display: flex;
		flex-direction: column;
		max-height: calc(100% - 44px - 56px - 20px); /* Account for status bar, header, bottom indicator */
	}

	.government-main-content h1 {
		font-size: 18px;
		font-weight: 700;
		margin: 0 0 4px 0;
		color: rgb(57, 57, 57);
		line-height: 1.1;
	}

	.subtitle {
		font-size: 13px;
		color: #666666;
		margin: 0 0 12px 0;
		line-height: 1.2;
	}

	.gov-options {
		display: flex;
		flex-direction: column;
		gap: 8px;
		flex: 1;
		overflow: hidden;
	}

	.gov-option {
		display: flex;
		align-items: flex-start;
		gap: 8px;
		padding: 10px;
		background: #ffffff;
		border: 1px solid #e5e5e7;
		border-radius: 6px;
		cursor: pointer;
		transition: all 0.2s ease;
		text-align: left;
		flex-shrink: 0;
	}

	.gov-option:hover {
		border-color: #2B5A6B;
		box-shadow: 0 2px 8px rgba(44, 95, 94, 0.1);
	}

	.gov-option.selected {
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

	.gov-option.selected .radio-button {
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
		font-size: 14px;
		font-weight: 600;
		margin: 0 0 2px 0;
		color: rgb(57, 57, 57);
		line-height: 1.2;
	}

	.option-content p {
		font-size: 11px;
		line-height: 1.2;
		color: #666666;
		margin: 0;
	}

	.bottom-section {
		display: flex;
		justify-content: center;
		margin-top: 8px;
		flex-shrink: 0;
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
		background: #ffffff;
		padding: 8px 20px;
		display: flex;
		justify-content: center;
		margin: 0;
	}

	.safari-content .bottom-indicator {
		background: #f6f6f6;
		margin: 0;
	}

	.government-content .bottom-indicator {
		background: linear-gradient(135deg, #ffffff 0%, #ffffff 100%);
	}

	.indicator-bar {
		width: 134px;
		height: 5px;
		background: rgba(0, 0, 0, 0.3);
		border-radius: 3px;
	}

	.government-content .indicator-bar {
		background: rgba(255, 255, 255, 0.3);
	}

	/* Demographics content styles */
	.demographics-content .content {
		flex: 1;
		padding: 16px;
		overflow: hidden;
		display: flex;
		flex-direction: column;
		max-height: calc(100% - 44px); /* Account for status bar */
	}

	.demographics-content h1 {
		font-size: 18px;
		font-weight: 700;
		margin: 0 0 4px 0;
		color: #1c1e21;
	}

	.demographics-content .subtitle {
		font-size: 13px;
		color: #666666;
		margin: 0 0 12px 0;
		line-height: 1.2;
	}

	.demo-options {
		display: flex;
		flex-direction: column;
		gap: 8px;
		flex: 1;
		overflow: hidden;
	}

	.demo-option {
		padding: 12px;
		background: #ffffff;
		border: 2px solid #e5e5e7;
		border-radius: 8px;
		cursor: pointer;
		text-align: left;
		transition: all 0.2s ease;
		flex-shrink: 0;
	}

	.demo-option:hover {
		border-color: #1877f2;
		box-shadow: 0 2px 8px rgba(24, 119, 242, 0.1);
	}

	.demo-option.selected {
		border-color: #1877f2;
		background: #f0f8ff;
		box-shadow: 0 2px 8px rgba(24, 119, 242, 0.15);
	}

	.demo-option h3 {
		font-size: 14px;
		font-weight: 600;
		margin: 0 0 4px 0;
		color: #1877f2;
	}

	.demo-option p {
		font-size: 12px;
		line-height: 1.3;
		color: #666666;
		margin: 0;
	}

	/* Mobile responsive styles */
	@media (max-width: 768px) {
		.unified-phone {
			width: 100vw;
			height: 100vh;
			margin: 0;
			border: none;
			border-radius: 0;
			box-shadow: none;
		}

		.unified-phone::before {
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
		
		.title {
			font-size: 16px !important;
		}

		.government-main-content {
			padding-top: 60px;
			padding-bottom: 60px;
			padding-left: 12px;
			padding-right: 12px;
		}

		.government-main-content h1 {
			font-size: 18px !important;
			line-height: 1.1 !important;
		}

		.subtitle {
			font-size: 13px !important;
			margin-bottom: 16px !important;
		}

		.gov-options {
			gap: 8px !important;
			margin-bottom: 16px !important;
		}

		.gov-option {
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
</style>