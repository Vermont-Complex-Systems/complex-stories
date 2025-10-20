// Svelte 5 rune-based auth state
// Simple reactive authentication state using modern Svelte patterns

class AuthState {
	#authToken = $state<string | null>(null)
	#currentUser = $state<any>(null)

	constructor() {
		// Initialize from localStorage if available
		if (typeof window !== 'undefined') {
			const storedToken = localStorage.getItem('auth_token')
			const storedUser = localStorage.getItem('auth_user')

			if (storedToken && storedUser) {
				try {
					this.#authToken = storedToken
					this.#currentUser = JSON.parse(storedUser)
					console.log('Auth restored from localStorage:', { username: this.#currentUser?.username, role: this.#currentUser?.role })
				} catch (e) {
					localStorage.removeItem('auth_token')
					localStorage.removeItem('auth_user')
				}
			}
		}
	}

	get isLoggedIn() {
		const result = this.#authToken !== null
		console.log('isLoggedIn check:', { authToken: this.#authToken ? 'present' : 'null', result })
		return result
	}

	get user() {
		console.log('getUser check:', { currentUser: this.#currentUser })
		return this.#currentUser
	}

	get token() {
		return this.#authToken
	}

	setAuthData(token: string, userData: any) {
		console.log('setAuthData called with:', { token: token?.substring(0, 20) + '...', user: userData })
		this.#authToken = token
		this.#currentUser = userData

		// Persist to localStorage
		if (typeof window !== 'undefined') {
			localStorage.setItem('auth_token', token)
			localStorage.setItem('auth_user', JSON.stringify(userData))
		}
	}

	clearAuthData() {
		this.#authToken = null
		this.#currentUser = null

		// Clear from localStorage
		if (typeof window !== 'undefined') {
			localStorage.removeItem('auth_token')
			localStorage.removeItem('auth_user')
		}
	}
}

const authState = new AuthState()

// Export functions that access the reactive state
export function isLoggedIn() {
	return authState.isLoggedIn
}

export function getUser() {
	return authState.user
}

export function getAuthToken() {
	return authState.token
}

// Actions that delegate to the auth state
export function setAuthData(token: string, userData: any) {
	authState.setAuthData(token, userData)
}

export function clearAuthData() {
	authState.clearAuthData()
}

// Legacy compatibility functions
export function getCurrentUserData() {
	return authState.user
}