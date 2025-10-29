<script lang="ts">
	import { getCurrentUser } from '$lib/api/auth.remote'

	type Props = {
		showDetails?: boolean
	}

	let { showDetails = false }: Props = $props()
</script>

{#await getCurrentUser()}
	<div class="auth-status loading">
		<span class="status-indicator">⟳</span>
		<span>Checking...</span>
	</div>
{:then user}
	{#if user}
		<div class="auth-status authenticated">
			<span class="status-indicator">✓</span>
			<span>
				Logged in as <strong>{user.username}</strong>
				{#if showDetails}
					<span class="role">({user.role})</span>
				{/if}
			</span>
		</div>
	{:else}
		<div class="auth-status not-authenticated">
			<span class="status-indicator">⚬</span>
			<span>Not logged in</span>
		</div>
	{/if}
{:catch error}
	<div class="auth-status error">
		<span class="status-indicator">⚠</span>
		<span>Auth error</span>
	</div>
{/await}

<style>
	.auth-status {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem;
		border-radius: 4px;
		font-size: 0.875rem;
		border: 1px solid;
	}

	.status-indicator {
		font-weight: bold;
		font-size: 1rem;
	}

	.loading {
		background: #f8f9fa;
		border-color: #dee2e6;
		color: #6c757d;
	}

	.authenticated {
		background: #d4edda;
		border-color: #c3e6cb;
		color: #155724;
	}

	.not-authenticated {
		background: #fff3cd;
		border-color: #ffeaa7;
		color: #856404;
	}

	.error {
		background: #f8d7da;
		border-color: #f5c6cb;
		color: #721c24;
	}

	.role {
		font-size: 0.8rem;
		opacity: 0.8;
	}

	strong {
		font-weight: 600;
	}
</style>