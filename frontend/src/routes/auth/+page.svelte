<script lang="ts">
	import AuthForm from '$lib/components/AuthForm.svelte'
</script>

<svelte:head>
	<title>Authentication - Complex Stories</title>
</svelte:head>

<div class="auth-page">
	<h1>Complex Stories Authentication</h1>
	<p>Login or register to access the annotation system.</p>

	<AuthForm />
</div>

<style>
	.auth-page {
		max-width: 600px;
		margin: 2rem auto;
		padding: 0 1rem;
		text-align: center;
	}

	.auth-page h1 {
		color: #333;
		margin-bottom: 0.5rem;
	}

	.auth-page p {
		color: #666;
		margin-bottom: 2rem;
	}
</style>