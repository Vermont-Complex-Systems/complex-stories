<script>
	import { authStore } from '$lib/auth-store.svelte'
	import { goto } from '$app/navigation'

	let username = $state('')
	let password = $state('')
	let error = $state('')

	async function handleLogin() {
		try {
			error = ''
			await authStore.login({ username, password })
			goto('/datasets/academic-research-groups')
		} catch (err) {
			error = err.message
		}
	}
</script>

<div class="login-container">
	<h1>Login</h1>

	{#if authStore.isLoggedIn}
		<div class="logged-in">
			<p>Welcome back, {authStore.user.username}!</p>
			<p>Role: {authStore.user.role}</p>
			<button onclick={() => authStore.logout()}>Logout</button>
		</div>
	{:else}
		<form class="login-form" onsubmit={(e) => { e.preventDefault(); handleLogin() }}>
			{#if error}
				<div class="error">{error}</div>
			{/if}

			<div class="field">
				<label for="username">Username:</label>
				<input
					id="username"
					type="text"
					bind:value={username}
					required
				/>
			</div>

			<div class="field">
				<label for="password">Password:</label>
				<input
					id="password"
					type="password"
					bind:value={password}
					required
				/>
			</div>

			<button type="submit" disabled={authStore.loading}>
				{authStore.loading ? 'Logging in...' : 'Login'}
			</button>
		</form>
	{/if}
</div>

<style>
	.login-container {
		max-width: 400px;
		margin: 2rem auto;
		padding: 2rem;
		border: 1px solid #ddd;
		border-radius: 8px;
	}

	.login-form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	label {
		font-weight: 600;
	}

	input {
		padding: 0.5rem;
		border: 1px solid #ccc;
		border-radius: 4px;
	}

	button {
		padding: 0.75rem;
		background: #0066cc;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
	}

	button:disabled {
		background: #ccc;
		cursor: not-allowed;
	}

	.error {
		color: red;
		font-size: 0.9rem;
	}

	.logged-in {
		text-align: center;
	}
</style>