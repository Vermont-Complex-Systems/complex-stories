<script lang="ts">
	import { loginUser, registerUser, getCurrentUser, logoutUser, updateProfile } from '$lib/api/auth.remote'

	let isRegistering = $state(false)
	let isEditing = $state(false)
</script>

{#await getCurrentUser()}
	<div class="loading">Loading...</div>
{:then user}
	{#if user}
		{#if isEditing}
			<div class="auth-form">
				<div class="form-header">
					<h2>Edit Profile</h2>
				</div>

				<form {...updateProfile}>
					<div class="form-group">
						<label for="orcid_id">ORCID (optional)</label>
						<input
							name="orcid_id"
							type="text"
							placeholder="0000-0002-1825-0097"
							value={user.orcid_id || ''}
						/>
						<span class="field-hint">Format: XXXX-XXXX-XXXX-XXXX</span>
					</div>

					<div class="form-group">
						<label for="openalex_id">OpenAlex ID (optional)</label>
						<input
							name="openalex_id"
							type="text"
							placeholder="A5017712502"
							value={user.openalex_id || ''}
						/>
						<span class="field-hint">Format: A followed by numbers</span>
					</div>

					<button type="submit" class="submit-btn">
						Save Changes
					</button>

					<button type="button" class="toggle-btn" onclick={() => isEditing = false}>
						Cancel
					</button>
				</form>
			</div>
		{:else}
			<div class="auth-success">
				<h3>Welcome, {user.username}!</h3>

				<div class="profile-grid">
					<div class="profile-item">
						<span class="profile-label">Role:</span>
						<span class="profile-value">{user.role}</span>
					</div>

					<div class="profile-item">
						<span class="profile-label">Email:</span>
						<span class="profile-value">{user.email}</span>
					</div>

					<div class="profile-item">
						<span class="profile-label">ORCID:</span>
						{#if user.orcid_id}
							<span class="profile-value">
								<a href="https://orcid.org/{user.orcid_id}" target="_blank" rel="noopener noreferrer">{user.orcid_id}</a>
							</span>
						{:else}
							<span class="profile-value not-set">Not set</span>
						{/if}
					</div>

					<div class="profile-item">
						<span class="profile-label">OpenAlex:</span>
						{#if user.openalex_id}
							<span class="profile-value">
								<a href="https://openalex.org/{user.openalex_id}" target="_blank" rel="noopener noreferrer">{user.openalex_id}</a>
							</span>
						{:else}
							<span class="profile-value not-set">Not set</span>
						{/if}
					</div>
				</div>

				<div class="button-group">
					<button onclick={() => isEditing = true} class="edit-btn">
						Edit Profile
					</button>
					<button onclick={() => logoutUser()} class="logout-btn">
						Logout
					</button>
				</div>
			</div>
		{/if}
	{:else}
		<div class="auth-form">
			<div class="form-header">
				<h2>{isRegistering ? 'Register' : 'Login'}</h2>
			</div>

			{#if isRegistering}
				<form {...registerUser}>
					<div class="form-group">
						<label for="username">Username</label>
						<input name="username" type="text" required />
						<span class="field-hint">3-50 characters, letters, numbers, and underscores only</span>
					</div>

					<div class="form-group">
						<label for="email">Email</label>
						<input name="email" type="email" required />
					</div>

					<div class="form-group">
						<label for="password">Password</label>
						<input name="password" type="password" required />
						<span class="field-hint">At least 8 characters</span>
					</div>

					<div class="form-group">
						<label for="orcid_id">ORCID (optional)</label>
						<input name="orcid_id" type="text" placeholder="0000-0002-1825-0097" />
						<span class="field-hint">Format: XXXX-XXXX-XXXX-XXXX</span>
					</div>

					<div class="form-group">
						<label for="openalex_id">OpenAlex ID (optional)</label>
						<input name="openalex_id" type="text" placeholder="A5017712502" />
						<span class="field-hint">Format: A followed by numbers</span>
					</div>

					<button type="submit" class="submit-btn">
						Register
					</button>

					<button type="button" class="toggle-btn" onclick={() => isRegistering = false}>
						Already have an account? Login
					</button>
				</form>
			{:else}
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

					<button type="button" class="toggle-btn" onclick={() => isRegistering = true}>
						Don't have an account? Register
					</button>
				</form>
			{/if}
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
	}

	.auth-success h3 {
		text-align: center;
		margin-bottom: 1.5rem;
	}

	.profile-grid {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		margin-bottom: 1.5rem;
		text-align: left;
	}

	.profile-item {
		display: flex;
		flex-direction: row;
		gap: 0.5rem;
		align-items: baseline;
	}

	.profile-label {
		font-weight: 600;
		min-width: 80px;
		flex-shrink: 0;
	}

	.profile-value {
		word-break: break-word;
		overflow-wrap: break-word;
	}

	.button-group {
		display: flex;
		justify-content: center;
		gap: 0.5rem;
		flex-wrap: wrap;
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

	.edit-btn {
		background: #28a745;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		cursor: pointer;
	}

	.edit-btn:hover {
		background: #218838;
	}

	.logout-btn {
		background: #dc3545;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		cursor: pointer;
	}

	.logout-btn:hover {
		background: #c82333;
	}

	.not-set {
		color: #999;
		font-style: italic;
	}

	.toggle-btn {
		width: 100%;
		padding: 0.75rem;
		background: transparent;
		color: #007bff;
		border: 1px solid #007bff;
		border-radius: 4px;
		font-size: 0.9rem;
		cursor: pointer;
		margin-top: 1rem;
		transition: all 0.2s;
	}

	.toggle-btn:hover {
		background: #007bff;
		color: white;
	}

	.field-hint {
		display: block;
		font-size: 0.75rem;
		color: #666;
		margin-top: 0.25rem;
		font-style: italic;
	}

	.auth-success a {
		color: #007bff;
		text-decoration: none;
	}

	.auth-success a:hover {
		text-decoration: underline;
	}

	/* Mobile styles */
	@media screen and (max-width: 768px) {
		.auth-form,
		.auth-success {
			padding: 1.5rem;
			margin: 0 1rem;
		}

		:global(.profile-item) {
			display: block !important;
			background: rgba(255, 0, 0, 0.1); /* DEBUG: remove this */
		}

		:global(.profile-label) {
			display: block !important;
			min-width: auto;
			font-size: 0.9rem;
			margin-bottom: 0.25rem;
			background: rgba(0, 255, 0, 0.1); /* DEBUG: remove this */
		}

		:global(.profile-value) {
			display: block !important;
			font-size: 0.95rem;
			background: rgba(0, 0, 255, 0.1); /* DEBUG: remove this */
		}

		.button-group {
			flex-direction: column;
			width: 100%;
		}

		.edit-btn,
		.logout-btn {
			width: 100%;
		}
	}
</style>