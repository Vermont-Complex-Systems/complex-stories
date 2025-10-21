class AuthState {
	#authToken = $state<string | null>(null)
	#currentUser = $state<any>(null)

	constructor() {
		// Initialize from localStorage or cookies if available
		if (typeof window !== 'undefined') {
			const storedToken = localStorage.getItem('auth_token')
			const storedUser = localStorage.getItem('auth_user')

			if (storedToken && storedUser) {
				try {
					this.#authToken = storedToken
					this.#currentUser = JSON.parse(storedUser)
				} catch (e) {
					localStorage.removeItem('auth_token')
					localStorage.removeItem('auth_user')
				}
			} else {
				// Try to load from cookies if localStorage is empty
				const cookieToken = this.getCookieValue('auth_token')
				const cookieUser = this.getCookieValue('auth_user')

				if (cookieToken && cookieUser) {
					try {
						this.#authToken = cookieToken
						this.#currentUser = JSON.parse(decodeURIComponent(cookieUser))

						// Also sync to localStorage for client-side reactivity
						localStorage.setItem('auth_token', cookieToken)
						localStorage.setItem('auth_user', decodeURIComponent(cookieUser))
					} catch (e) {
						// Silently handle cookie parsing errors
					}
				}
			}
		}
	}

	// Helper function to get cookie value
	getCookieValue(name: string): string | null {
		if (typeof document === 'undefined') return null

		const value = `; ${document.cookie}`
		const parts = value.split(`; ${name}=`)
		if (parts.length === 2) {
			return parts.pop()?.split(';').shift() || null
		}
		return null
	}

	get isLoggedIn() {
		return this.#authToken !== null
	}

	get user() {
		return this.#currentUser
	}

	get token() {
		return this.#authToken
	}

	setAuthData(token: string, userData: any) {
		this.#authToken = token
		this.#currentUser = userData

		// Persist to localStorage for client-side reactivity
		// Note: Server-side cookies are now set by login remote function
		if (typeof window !== 'undefined') {
			localStorage.setItem('auth_token', token)
			localStorage.setItem('auth_user', JSON.stringify(userData))
		}
	}

	clearAuthData() {
		this.#authToken = null
		this.#currentUser = null

		// Clear from localStorage
		// Note: Server-side cookies are now cleared by logout remote function
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