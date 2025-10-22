<script lang="ts">
	import Spinner from "$lib/components/helpers/Spinner.svelte"
	import { loginUser, getCurrentUser, logoutUser, changePassword } from '$lib/api/auth.remote'

	let showPasswordChange = $state(false)

</script>

<svelte:head>
	<title>Authentication - Complex Stories</title>
</svelte:head>

<div class="auth-page">
	{#await getCurrentUser()}
		<Spinner text="loading data..." />
	{:then user}
		{#if user}
			<div class="auth-success">
				<h3>Welcome, {user.username}!</h3>
				<p>Role: {user.role}</p>
				<p>Email: {user.email}</p>

				<div class="user-actions">
					<button onclick={() => showPasswordChange = !showPasswordChange} class="change-password-btn">
						{showPasswordChange ? 'Cancel' : 'Change Password'}
					</button>
					<button onclick={() => logoutUser()} class="logout-btn">
						Logout
					</button>
				</div>

				{#if showPasswordChange}
					<div class="password-change-form">
						<h4>Change Password</h4>
						<form {...changePassword} onsubmit={() => showPasswordChange = false}>
							<div class="form-group">
								<label for="current_password">Current Password</label>
								<input name="current_password" type="password" required />
							</div>

							<div class="form-group">
								<label for="new_password">New Password</label>
								<input name="new_password" type="password" required minlength="8" />
							</div>

							<button type="submit" class="submit-btn">
								Update Password
							</button>
						</form>
					</div>
				{/if}
			</div>
		{:else}
			<div class="auth-form">
				<div class="form-header">
					<h2>Login</h2>
					<p>Welcome back to complex-stories!</p>
				</div>

				<form {...loginUser}>
					<div class="form-group">
						<label for="username">Username</label>
						<input name="username" type="text" required />
					</div>

					<div class="form-group">
						<label for="password">Password</label>
						<input name="password" type="password" required />
					</div>

					<button type="submit" class="submit-btn">
						Login
					</button>
				</form>
			</div>
		{/if}
	{:catch error}
		<div class="error-message">
			Failed to load user data: {error.message}
		</div>
	{/await}
</div>

<style>
	.auth-page {
		max-width: 600px;
		margin: 5rem auto;
		padding: 0 1rem;
		text-align: center;
	}


	.loading {
		text-align: left;
		padding: 2rem;
		color: #666;
	}

	.auth-form {
		max-width: 400px;
		margin: 0 auto;
		padding: 2rem;
		border-radius: 8px;
		background: white;
	}

	.auth-success {
		max-width: 400px;
		margin: 0 auto;
		padding: 2rem;
		border: 1px solid;
		border-radius: 8px;
		text-align: center;
	}

	.form-header {
		text-align: center;
		margin-bottom: 2rem;
	}

	.form-header h2 {
		margin: 0 0 1rem 0;
		color: #333;
	}


	.form-group {
		margin-bottom: 1rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 500;
		color: #333;
	}

	.form-group input {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 1rem;
		box-sizing: border-box;
	}

	.form-group input:focus {
		outline: none;
		border-color: #007bff;
		box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
	}

	.error-message {
		background: #f8d7da;
		border: 1px solid #f5c6cb;
		color: #721c24;
		padding: 0.75rem;
		border-radius: 4px;
		margin-bottom: 1rem;
		font-size: 0.9rem;
	}

	.field-error {
		color: #dc3545;
		font-size: 0.875rem;
		margin-top: 0.25rem;
	}

	.success-message {
		background: #d4edda;
		border: 1px solid #c3e6cb;
		color: #155724;
		padding: 0.75rem;
		border-radius: 4px;
		margin-bottom: 1rem;
		font-size: 0.9rem;
	}

	.submit-btn {
		width: 100%;
		padding: 0.75rem;
		background: #6c757d;
		color: white;
		border: none;
		border-radius: 4px;
		font-size: 1rem;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	.submit-btn:hover:not(:disabled) {
		background: #0056b3;
	}

	.submit-btn:disabled {
		background: #6c757d;
		cursor: not-allowed;
	}

	.user-actions {
		display: flex;
		gap: 0.5rem;
		margin-top: 1rem;
		justify-content: center;
	}

	.change-password-btn {
		background: #007bff;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.9rem;
	}

	.change-password-btn:hover {
		background: #0056b3;
	}

	.logout-btn {
		background: #6c757d;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.9rem;
	}

	.logout-btn:hover {
		background: #333;
	}

	.password-change-form {
		margin-top: 1.5rem;
		padding: 1.5rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		background: #f8f9fa;
	}

	.password-change-form h4 {
		margin: 0 0 1rem 0;
		color: #333;
		text-align: center;
	}
</style>