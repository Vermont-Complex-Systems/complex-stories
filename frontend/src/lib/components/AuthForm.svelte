<script lang="ts">
	import { loginUser, registerUser, getCurrentUser, logoutUser } from '$lib/api/auth.remote'

	type Props = {
		mode?: 'login' | 'register'
	}

	let { mode = 'login' }: Props = $props()
	let showRegister = $state(mode === 'register')

	// Clear form when switching modes
	const toggleMode = () => {
		showRegister = !showRegister
	}
</script>

{#await getCurrentUser()}
	<div class="loading">Loading...</div>
{:then user}
	{#if user}
		<div class="auth-success">
			<h3>Welcome, {user.username}!</h3>
			<p>Role: {user.role}</p>
			<p>Email: {user.email}</p>
			<button onclick={() => logoutUser()} class="logout-btn">
				Logout
			</button>
		</div>
	{:else}
		<div class="auth-form">
			<div class="form-header">
				<h2>{showRegister ? 'Register' : 'Login'}</h2>
				<button onclick={toggleMode} class="toggle-mode">
					{showRegister ? 'Already have an account? Login' : 'Need an account? Register'}
				</button>
			</div>

			<form {...showRegister ? registerUser : loginUser}>
				<div class="form-group">
					<label for="username">Username</label>
					<input name="username" type="text" required />
				</div>

				{#if showRegister}
					<div class="form-group">
						<label for="email">Email</label>
						<input name="email" type="email" required />
					</div>
				{/if}

				<div class="form-group">
					<label for="password">Password</label>
					<input name="password" type="password" required />
				</div>

				{#if showRegister}
					<div class="form-group">
						<label for="role">Role</label>
						<select name="role">
							<option value="annotator">Annotator</option>
							<option value="admin">Admin</option>
						</select>
					</div>
				{/if}

				<button type="submit" class="submit-btn">
					{showRegister ? 'Register' : 'Login'}
				</button>
			</form>
		</div>
	{/if}
{:catch error}
	<div class="error-message">
		Failed to load user data: {error.message}
	</div>
{/await}

<style>
	.loading {
		text-align: center;
		padding: 2rem;
		color: #666;
	}

	.auth-form {
		max-width: 400px;
		margin: 0 auto;
		padding: 2rem;
		border: 1px solid #ddd;
		border-radius: 8px;
		background: white;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	.auth-success {
		max-width: 400px;
		margin: 0 auto;
		padding: 2rem;
		border: 1px solid #28a745;
		border-radius: 8px;
		background: #d4edda;
		color: #155724;
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

	.toggle-mode {
		background: none;
		border: none;
		color: #007bff;
		text-decoration: underline;
		cursor: pointer;
		font-size: 0.9rem;
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

	.form-group input,
	.form-group select {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 1rem;
		box-sizing: border-box;
	}

	.form-group input:focus,
	.form-group select:focus {
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
		background: #007bff;
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

	.logout-btn {
		background: #dc3545;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		cursor: pointer;
		margin-top: 1rem;
	}

	.logout-btn:hover {
		background: #c82333;
	}
</style>