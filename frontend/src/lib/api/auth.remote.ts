import { error } from '@sveltejs/kit'
import { command, form, query } from '$app/server'
import * as v from 'valibot'
import {
	userSchema,
	tokenSchema,
	registerUserSchema,
	loginUserSchema,
	updateUserRoleSchema,
	type RegisterUser,
	type LoginUser,
	type UpdateUserRole
} from '$lib/schema/auth'

// API base URL
const API_BASE = 'http://localhost:8000/auth'

// Import auth client for token management
import { getAuthToken, setAuthData, clearAuthData } from '$lib/auth.svelte'

// Helper function for API calls with auth header
async function apiCall(endpoint: string, options: RequestInit = {}) {
	const url = `${API_BASE}${endpoint}`

	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		...options.headers as Record<string, string>,
	}

	// Add auth header if we have a token
	const token = getAuthToken()
	if (token) {
		headers['Authorization'] = `Bearer ${token}`
	}

	const response = await fetch(url, {
		headers,
		...options,
	})

	if (!response.ok) {
		const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
		error(response.status, errorData.detail || `API Error: ${response.status}`)
	}

	return response.json()
}

// REGISTER new user
export const registerUser = form(
	registerUserSchema,
	async (userData: RegisterUser) => {
		const data = await apiCall('/register', {
			method: 'POST',
			body: JSON.stringify(userData),
		})

		// Validate response data
		return v.parse(userSchema, data)
	}
)

// LOGIN user
export const loginUser = form(
	loginUserSchema,
	async (credentials: LoginUser) => {
		const data = await apiCall('/login', {
			method: 'POST',
			body: JSON.stringify(credentials),
		})

		// Validate response data
		const tokenData = v.parse(tokenSchema, data)

		// Store auth token and user data
		setAuthData(tokenData.access_token, tokenData.user)

		// Refresh user info
		getCurrentUser().refresh()

		return tokenData
	}
)

// LOGOUT user (client-side only)
export const logoutUser = command(
	async () => {
		clearAuthData()

		// Refresh user state
		getCurrentUser().refresh()

		return { success: true }
	}
)

// GET current user info
export const getCurrentUser = query(
	async () => {
		// Check if we have locally stored user data first
		const { getUser } = await import('$lib/auth.svelte')
		const localUser = getUser()

		if (localUser) {
			return localUser
		}

		// If no local user, check if we have a token and fetch from API
		const token = getAuthToken()
		if (!token) {
			return null
		}

		try {
			const data = await apiCall('/me')
			const user = v.parse(userSchema, data)

			// Store the fetched user data locally
			const { setAuthData } = await import('$lib/auth.svelte')
			setAuthData(token, user)

			return user
		} catch (err) {
			// Token might be expired, clear auth state
			clearAuthData()
			return null
		}
	}
)

// GET all users (admin only)
export const getAllUsers = query(
	async () => {
		const data = await apiCall('/users')
		return v.parse(v.array(userSchema), data)
	}
)

// UPDATE user role (admin only)
export const updateUserRole = form(
	updateUserRoleSchema,
	async ({ user_id, role }: UpdateUserRole) => {
		await apiCall(`/users/${user_id}/role`, {
			method: 'PUT',
			body: JSON.stringify({ role }),
		})

		// Refresh users list
		getAllUsers().refresh()

		return { success: true, user_id, role }
	}
)

