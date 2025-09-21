<script>
	import { onMount } from 'svelte';

	let { title = "Settings & privacy", onAnswer = () => {} } = $props();
	let selectedAnswer = $state('');

	function handleAnswerSelect(answer) {
		selectedAnswer = answer;
		onAnswer(answer);
	}
</script>

<div class="mobile-settings">
	<header class="header">
		<button class="back-btn" aria-label="Go back">
			<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
				<path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
			</svg>
		</button>
		<h1 class="title">{title}</h1>
		<button class="search-btn" aria-label="Search">
			<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
				<circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
				<path d="M21 21L16.65 16.65" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
			</svg>
		</button>
	</header>

	<div class="content">
		<div class="search-bar">
			<input type="text" placeholder="Search settings" />
		</div>

		<div class="card">
			<div class="card-header">
				<div class="meta-logo">
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="#1877F2"/>
					</svg>
					<span>Meta</span>
				</div>
			</div>
			
			<h2 class="card-title">Privacy Settings</h2>
			<p class="card-description">
				How do you typically set your social media privacy?
			</p>

			<div class="menu-items">
				<button class="menu-item" class:selected={selectedAnswer === 'private'} onclick={() => handleAnswerSelect('private')}>
					<div class="menu-icon">
						<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" stroke-width="1.5"/>
							<circle cx="12" cy="16" r="1" stroke="currentColor" stroke-width="1.5"/>
							<path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</div>
					<span>Private</span>
					<div class="chevron">
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</div>
				</button>

				<button class="menu-item" class:selected={selectedAnswer === 'mixed'} onclick={() => handleAnswerSelect('mixed')}>
					<div class="menu-icon">
						<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
							<circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</div>
					<span>Mixed</span>
					<div class="chevron">
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</div>
				</button>

				<button class="menu-item" class:selected={selectedAnswer === 'public'} onclick={() => handleAnswerSelect('public')}>
					<div class="menu-icon">
						<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5"/>
							<path d="M2 12h20" stroke="currentColor" stroke-width="1.5"/>
							<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" stroke="currentColor" stroke-width="1.5"/>
						</svg>
					</div>
					<span>Public</span>
					<div class="chevron">
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</div>
				</button>

				<button class="menu-item" class:selected={selectedAnswer === 'depends'} onclick={() => handleAnswerSelect('depends')}>
					<div class="menu-icon">
						<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.5"/>
							<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1 1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" stroke="currentColor" stroke-width="1.5"/>
						</svg>
					</div>
					<span>It depends</span>
					<div class="chevron">
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
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
						<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" stroke-width="1.5"/>
							<circle cx="12" cy="16" r="1" stroke="currentColor" stroke-width="1.5"/>
							<path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</div>
					<span>Privacy Checkup</span>
				</div>

				<div class="menu-item-static">
					<div class="menu-icon">
						<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
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

	<nav class="bottom-nav">
		<div class="nav-item">
			<div class="nav-icon">
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
					<polyline points="9,22 9,12 15,12 15,22" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</div>
			<span class="nav-label">Home</span>
		</div>

		<div class="nav-item">
			<div class="nav-icon">
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
					<circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
					<path d="M23 21v-2a4 4 0 0 0-3-3.87" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
					<path d="M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</div>
			<span class="nav-label">Friends</span>
			<div class="nav-badge">1</div>
		</div>

		<div class="nav-item">
			<div class="nav-icon">
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M7 4V2a1 1 0 0 1 1-1h8a1 1 0 0 1 1 1v2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
					<path d="M5 7h14l-1 10a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 7z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
					<path d="M10 11v6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
					<path d="M14 11v6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</div>
			<span class="nav-label">Marketplace</span>
		</div>

		<div class="nav-item">
			<div class="nav-icon">
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
					<circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</div>
			<span class="nav-label">Profile</span>
		</div>

		<div class="nav-item">
			<div class="nav-icon">
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
					<path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</div>
			<span class="nav-label">Notifications</span>
			<div class="nav-badge">5</div>
		</div>

		<div class="nav-item active">
			<div class="nav-icon">
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<line x1="3" y1="6" x2="21" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					<line x1="3" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					<line x1="3" y1="18" x2="21" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</div>
			<span class="nav-label">Menu</span>
		</div>
	</nav>
</div>

<style>
	.mobile-settings {
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

	.mobile-settings::before {
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
		.mobile-settings {
			width: 100vw;
			height: 100vh;
			margin: 0;
			border: none;
			border-radius: 0;
			box-shadow: none;
		}

		.mobile-settings::before {
			display: none;
		}

		.bottom-nav {
			position: fixed;
			bottom: 0;
			left: 0;
			right: 0;
			width: 100vw;
			z-index: 1000;
		}
	}

	.header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 12px 16px;
		background-color: #ffffff;
		border-bottom: 1px solid #e4e6ea;
		position: sticky;
		top: 0;
		z-index: 10;
		padding-top: 32px;
	}

	@media (max-width: 768px) {
		.header {
			padding: 8px 12px;
			position: fixed;
			top: 0;
			left: 0;
			right: 0;
			width: 100vw;
			z-index: 999;
			height: 44px;
		}

		.title {
			font-size: 25px !important;
			white-space: nowrap;
			overflow: hidden;
			text-overflow: ellipsis;
			font-weight: 600;
		}

		.back-btn, .search-btn {
			padding: 6px;
		}

		.back-btn svg, .search-btn svg {
			width: 20px;
			height: 20px;
		}

		.content {
			padding-top: 60px;
			padding-bottom: 80px;
			padding-left: 8px;
			padding-right: 8px;
		}

		.search-bar {
			padding: 6px 10px;
			margin: 16px 0;
		}

		.search-bar input {
			font-size: 14px;
		}

		.card {
			padding: 12px;
		}

		.card-title {
			font-size: 20px !important;
		}

		.card-description {
			font-size: 20px !important;
		}

		.section-title {
			font-size: 15px;
		}

		.section-description {
			font-size: 13px;
		}

		.menu-item {
			font-size: 15px;
			padding: 8px 0;
		}

		.menu-item-static {
			font-size: 15px;
			padding: 8px 0;
		}
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
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.content {
		padding: 12px;
		padding-bottom: 80px;
		gap: 12px;
		display: flex;
		flex-direction: column;
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

	.search-bar input::placeholder {
		color: #65676b;
	}

	.card {
		background-color: #ffffff;
		border-radius: 12px;
		padding: 16px;
		box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
	}

	.card-header {
		margin-bottom: 6px;
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
		margin: 0 0 6px 0;
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
		gap: 2px;
		margin-bottom: 0;
	}

	.menu-item {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 10px 0;
		font-size: 16px;
		color: #1c1e21;
		background: none;
		border: none;
		width: 100%;
		text-align: left;
		cursor: pointer;
		border-radius: 6px;
		transition: background-color 0.2s;
		justify-content: space-between;
		min-height: 44px;
	}

	.menu-item:hover {
		background-color: #f2f3f5;
	}

	.menu-item.selected {
		background-color: #e3f2fd;
		color: #1877f2;
	}

	.menu-item .chevron {
		opacity: 0.6;
	}

	.menu-item.selected .chevron {
		opacity: 1;
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
	}

	.section-description {
		font-size: 14px;
		color: #65676b;
		margin: 0 0 16px 0;
		line-height: 1.3;
		text-align: left;
	}

	.menu-item-static {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 10px 0;
		font-size: 16px;
		color: #1c1e21;
		min-height: 44px;
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


	@media (prefers-color-scheme: dark) {
		.mobile-settings {
			background-color: #18191a;
			color: #e4e6ea;
		}

		.header {
			background-color: #242526;
			border-bottom-color: #3e4042;
		}

		.back-btn, .search-btn {
			color: #e4e6ea;
		}

		.back-btn:hover, .search-btn:hover {
			background-color: #3a3b3c;
		}

		.search-bar {
			background-color: #3a3b3c;
		}

		.search-bar input {
			color: #e4e6ea;
		}

		.search-bar input::placeholder {
			color: #b0b3b8;
		}

		.card {
			background-color: #242526;
		}

		.card-title {
			color: #e4e6ea;
		}

		.card-description {
			color: #b0b3b8;
		}

		.menu-item {
			color: #e4e6ea;
		}

		.menu-item:hover {
			background-color: #3a3b3c;
		}

		.menu-item.selected {
			background-color: #1e3a5f;
			color: #58a6ff;
		}

		.menu-item.selected .chevron {
			color: #58a6ff;
		}

		.menu-icon {
			color: #b0b3b8;
		}

		.separator {
			background-color: #3e4042;
		}

		.section-title {
			color: #e4e6ea;
		}

		.section-description {
			color: #b0b3b8;
		}

		.menu-item-static {
			color: #e4e6ea;
		}

		.bottom-nav {
			background-color: #242526;
			border-top-color: #3e4042;
		}

		.nav-icon {
			color: #b0b3b8;
		}

		.nav-label {
			color: #b0b3b8;
		}

		.nav-item.active .nav-icon {
			color: #58a6ff;
		}

		.nav-item.active .nav-label {
			color: #58a6ff;
		}
	}
</style>