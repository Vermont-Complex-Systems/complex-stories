// Server-side hooks for authentication context
// See https://svelte.dev/docs/kit/auth and 
// https://svelte.dev/docs/kit/hooks#Server-hooks.
// Also the tutorial: https://svelte.dev/tutorial/kit/handle
export async function handle({ event, resolve }) {
	// Get auth token and user data from cookies
	const token = event.cookies.get('auth_token')
	const userData = event.cookies.get('auth_user')

	// If we have both token and user data, add them to locals
	if (token && userData) {
		try {
			event.locals.token = token
			event.locals.user = JSON.parse(decodeURIComponent(userData))
		} catch (error) {
			// If parsing fails, clear the invalid cookies
			event.cookies.delete('auth_token', { path: '/' })
			event.cookies.delete('auth_user', { path: '/' })
		}
	}

	return resolve(event)
}