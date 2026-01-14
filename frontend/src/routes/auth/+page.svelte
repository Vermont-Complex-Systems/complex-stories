<script lang="ts">
	import Spinner from "$lib/components/helpers/Spinner.svelte"
	import { loginUser, getCurrentUser, logoutUser, changePassword, updateProfile } from '$lib/api/auth.remote'

	let showPasswordChange = $state(false)
	let passwordChangeSuccess = $state(false)
	let profileUpdateSuccess = $state(false)

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

				{#if profileUpdateSuccess}
					<div class="success-message">
						✅ Profile updated successfully!
					</div>
				{/if}

				<form {...updateProfile.enhance(async ({ submit }) => {
						try {
							await submit()
							profileUpdateSuccess = true
							setTimeout(() => profileUpdateSuccess = false, 5000)
						} catch (error) {
							console.error('Profile update failed:', error)
						}
					})}>
					<div class="form-row">
						<label>Role</label>
						<div class="value-display">{user.role}</div>
					</div>

					<div class="form-row">
						<label>Email</label>
						<div class="value-display">{user.email}</div>
					</div>

					<div class="form-row">
						<label for="orcid_id">ORCID</label>
						<div class="input-wrapper">
							<input
								name="orcid_id"
								type="text"
								placeholder="0000-0002-1825-0097"
								value={user.orcid_id || ''}
							/>
							<span class="field-hint">Format: XXXX-XXXX-XXXX-XXXX</span>
						</div>
					</div>

					<div class="form-row">
						<label for="openalex_id">OpenAlex ID</label>
						<div class="input-wrapper">
							<input
								name="openalex_id"
								type="text"
								placeholder="A5017712502"
								value={user.openalex_id || ''}
							/>
							<span class="field-hint">Format: A followed by numbers</span>
						</div>
					</div>

					<div class="user-actions">
						<button type="submit" class="save-btn">
							Save
						</button>
						<button type="button" onclick={() => {
							showPasswordChange = !showPasswordChange
							passwordChangeSuccess = false
						}} class="change-password-btn">
							{showPasswordChange ? 'Cancel' : 'Change Password'}
						</button>
						<button type="button" onclick={() => logoutUser()} class="logout-btn">
							Logout
						</button>
					</div>
				</form>

				{#if passwordChangeSuccess}
					<div class="success-message">
						✅ Password changed successfully!
					</div>
				{/if}

				{#if showPasswordChange}
					<div class="password-change-form">
						<h4>Change Password</h4>
						<form {...changePassword.enhance(async ({ submit }) => {
								try {
									await submit()
									showPasswordChange = false
									passwordChangeSuccess = true
									setTimeout(() => passwordChangeSuccess = false, 5000)
								} catch (error) {
									console.error('Password change failed:', error)
								}
							})}>
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
		max-width: 600px;
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
		margin-top: 1.5rem;
		justify-content: center;
		flex-wrap: wrap;
	}

	.save-btn {
		background: #000;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.9rem;
	}

	.save-btn:hover {
		background: #333;
	}

	.change-password-btn {
		background: #000;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.9rem;
	}

	.change-password-btn:hover {
		background: #333;
	}

	.logout-btn {
		background: #000;
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

	.auth-success form {
		margin: 1.5rem 0;
		text-align: left;
	}

	.form-row {
		display: flex;
		align-items: flex-start;
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.form-row label {
		min-width: 120px;
		padding-top: 0.75rem;
		font-weight: 500;
		color: #333;
		text-align: left;
		flex-shrink: 0;
	}

	.input-wrapper {
		flex: 1;
		min-width: 0;
	}

	.input-wrapper input {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 1rem;
		box-sizing: border-box;
	}

	.input-wrapper input:focus {
		outline: none;
		border-color: #007bff;
		box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
	}

	.value-display {
		flex: 1;
		padding: 0.75rem 0;
		color: #333;
	}

	.password-change-form {
		margin-top: 1.5rem;
		padding: 1.5rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		background: #f8f9fa;
		text-align: left;
	}

	.password-change-form h4 {
		margin: 0 0 1rem 0;
		color: #333;
		text-align: center;
	}

	.field-hint {
		display: block;
		font-size: 0.75rem;
		color: #666;
		margin-top: 0.25rem;
		font-style: italic;
	}

	/* Mobile styles */
	@media screen and (max-width: 768px) {
		.form-row {
			flex-direction: column;
			gap: 0.25rem;
		}

		.form-row label {
			min-width: auto;
			padding-top: 0;
		}

		.value-display {
			padding: 0.5rem 0;
		}

		.user-actions {
			flex-direction: column;
			width: 100%;
		}

		.user-actions button {
			width: 100%;
		}
	}
</style>