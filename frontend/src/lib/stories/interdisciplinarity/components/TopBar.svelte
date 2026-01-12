<script>
	import { Avatar } from 'bits-ui'
	import { base } from '$app/paths'
	import { getCurrentUser } from '../data/data.remote'
	import HelpPopover from './HelpPopover.svelte'

	let {
		mode,
		generalQueueCount = 0,
		communityQueueCount = 0,
		myPapersCount = 0,
		myPapersQueueCount = 0,
		onModeChange = () => {}
	} = $props()

	// Get user initials helper
	function getUserInitials(username) {
		if (!username) return 'U'
		const parts = username.split('_')
		if (parts.length >= 2) {
			return (parts[1][0] + parts[0][0]).toUpperCase()
		}
		return username.slice(0, 2).toUpperCase()
	}
</script>

<div class="top-bar">
	<div class="top-row">
		<a href="{base}/" class="logo-link">
			<img src="{base}/octopus-swim-right.png" alt="Home" class="octopus-icon" />
		</a>
		<div class="right-section">
			<HelpPopover side="bottom" align="end" sideOffset={2} iconSize={30} />
			{#await getCurrentUser()}
				<!-- Loading auth state -->
			{:then user}
				{#if user}
					<a href="{base}/auth" class="avatar-button">
						<Avatar.Root class="avatar-root">
							<Avatar.Fallback class="avatar-fallback">
								{getUserInitials(user.username)}
							</Avatar.Fallback>
						</Avatar.Root>
					</a>
				{:else}
					<a href="{base}/auth" class="login-button">
						Log in
					</a>
				{/if}
			{:catch}
				<a href="{base}/auth" class="login-button">
					Log in
				</a>
			{/await}
		</div>
	</div>
	<div class="mode-switcher">
		<button
			class="mode-btn"
			class:active={mode === 'story'}
			onclick={() => onModeChange('story')}
		>
			Why
		</button>
		<button
			class="mode-btn"
			class:active={mode === 'overview'}
			onclick={() => onModeChange('overview')}
		>
			📊 Overview
		</button>
		<button
			class="mode-btn"
			class:active={mode === 'csv-queue'}
			onclick={() => onModeChange('csv-queue')}
			disabled={generalQueueCount === 0}
		>
			📝 General Queue ({generalQueueCount})
		</button>
		{#if communityQueueCount > 0}
			<button
				class="mode-btn"
				class:active={mode === 'community-queue'}
				onclick={() => onModeChange('community-queue')}
				disabled={communityQueueCount === 0}
			>
				🌐 Community ({communityQueueCount})
			</button>
		{/if}
		{#if myPapersCount > 0}
			<button
				class="mode-btn"
				class:active={mode === 'my-papers-queue'}
				onclick={() => onModeChange('my-papers-queue')}
				disabled={myPapersQueueCount === 0}
			>
				📄 My Papers ({myPapersQueueCount})
			</button>
		{/if}
		<button
			class="mode-btn"
			class:active={mode === 'stats'}
			onclick={() => onModeChange('stats')}
		>
			📈 Stats
		</button>
	</div>
</div>

<style>
	.top-bar {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		padding: 1rem 2rem;
		background: white;
		border-bottom: 1px solid #e0e0e0;
		position: sticky;
		top: 0;
		z-index: 100;
	}

	.top-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.logo-link {
		display: flex;
		align-items: center;
		text-decoration: none;
		transition: transform 0.2s;
		transform: translateY(5px);
	}

	.logo-link:hover {
		transform: translateY(-2px);
	}

	.octopus-icon {
		height: 4rem;
		object-fit: contain;
	}

	.right-section {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		font-size: 0.875rem;
	}

	.mode-switcher {
		display: flex;
		gap: 0.5rem;
		justify-content: flex-end;
		flex-wrap: wrap;
	}

	.mode-btn {
		padding: 0.5rem 1rem;
		border: 1px solid #e0e0e0;
		border-radius: 0.5rem;
		background: white;
		color: #666;
		font-size: 0.875rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	.mode-btn:hover {
		background: #f5f5f5;
		border-color: #ccc;
	}

	.mode-btn.active {
		background: #1a1a1a;
		color: white;
		border-color: #1a1a1a;
	}

	.mode-btn:disabled {
		opacity: 0.4;
		cursor: not-allowed;
		background: #f5f5f5;
	}

	.avatar-button,
	.login-button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		height: 2.5rem;
		padding: 0 0.75rem;
		border-radius: 0.5rem;
		background: transparent;
		color: #1a1a1a;
		text-decoration: none;
		font-weight: 500;
		font-size: 0.875rem;
		transition: all 0.2s;
		cursor: pointer;
	}

	.avatar-button:hover,
	.login-button:hover {
		background: rgba(0, 0, 0, 0.05);
		transform: scale(1.05);
	}

	:global(.avatar-root) {
		width: 2rem;
		height: 2rem;
	}

	:global(.avatar-fallback) {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 100%;
		height: 100%;
		background: #1a1a1a;
		color: white;
		border-radius: 50%;
		font-size: 0.75rem;
		font-weight: 600;
	}

	/* Mobile styles */
	@media (max-width: 768px) {
		.top-bar {
			padding: 0.75rem 1rem;
			gap: 0.75rem;
		}

		.octopus-icon {
			height: 2.5rem;
		}

		.mode-switcher {
			justify-content: flex-start;
		}

		.mode-btn {
			padding: 0.4rem 0.75rem;
			font-size: 0.75rem;
			flex: 0 1 auto;
		}
	}

	@media (max-width: 480px) {
		.mode-btn {
			font-size: 0.7rem;
			padding: 0.35rem 0.6rem;
		}

		.octopus-icon {
			height: 2rem;
		}

		.right-section {
			gap: 0.5rem;
		}
	}
</style>
