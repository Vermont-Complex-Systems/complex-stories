// Auth client utilities for managing authentication state
// Similar to the sveltekit-remote-functions pattern

// Global auth state
let authToken: string | null = null
let currentUser: any = null

// Initialize from localStorage immediately when module loads
if (typeof window !== 'undefined') {
	const storedToken = localStorage.getItem('auth_token')
	const storedUser = localStorage.getItem('auth_user')

	if (storedToken && storedUser) {
		try {
			authToken = storedToken
			currentUser = JSON.parse(storedUser)
			console.log('Auth restored from localStorage:', { username: currentUser?.username, role: currentUser?.role })
		} catch (e) {
			localStorage.removeItem('auth_token')
			localStorage.removeItem('auth_user')
		}
	}
}

// Helper to check if user is authenticated
export const isAuthenticated = () => {
	return authToken !== null && currentUser !== null
}

// Helper to check if current user is admin
export const isAdmin = () => {
	return currentUser?.role === 'admin'
}

// Helper to get auth token (for manual API calls)
export const getAuthToken = () => {
	return authToken
}

// Helper to get current user data
export const getCurrentUserData = () => {
	return currentUser
}

// Helper to set auth token and user (called from login)
export const setAuthData = (token: string, user: any) => {
	console.log('setAuthData called with:', { token: token?.substring(0, 20) + '...', user })
	authToken = token
	currentUser = user

	// Persist to localStorage
	if (typeof window !== 'undefined') {
		localStorage.setItem('auth_token', token)
		localStorage.setItem('auth_user', JSON.stringify(user))
	}
}

// Helper to clear auth data (called from logout)
export const clearAuthData = () => {
	authToken = null
	currentUser = null

	// Clear from localStorage
	if (typeof window !== 'undefined') {
		localStorage.removeItem('auth_token')
		localStorage.removeItem('auth_user')
	}
}

// Helper to set auth token only (for session restoration)
export const setAuthToken = (token: string) => {
	authToken = token
}

// Helper to set current user data only
export const setCurrentUser = (user: any) => {
	currentUser = user
}

// Export state getter for reactive access
export const getAuthState = () => ({
	token: authToken,
	user: currentUser,
	isAuthenticated: isAuthenticated(),
	isAdmin: isAdmin()
})

// Quick authentication check (synchronous)
export const isLoggedIn = () => {
	return authToken !== null
}

// Quick user info (synchronous)
export const getQuickUserInfo = () => {
	return currentUser ? {
		username: currentUser.username,
		role: currentUser.role,
		isAdmin: currentUser.role === 'admin'
	} : null
}