import { query, command, getRequestEvent } from '$app/server'
import * as v from 'valibot'
import { API_BASE } from '$env/static/private'

const API_BASE_URL = API_BASE || 'http://localhost:3001'

/**
 * AUTH REMOTE FUNCTIONS
 * Handle user registration, login, and session management
 */

// Register a new user
export const registerUser = command(
	v.object({
		username: v.string(),
		email: v.string(),
		password: v.string()
	}),
	async (data) => {
		const response = await fetch(`${API_BASE_URL}/auth/register`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(data)
		})

		if (!response.ok) {
			const error = await response.json()
			throw new Error(error.detail || 'Registration failed')
		}

		const result = await response.json()

		// Store token in locals for server-side access
		const { locals } = getRequestEvent()
		locals.token = result.access_token
		locals.user = result.user

		return result
	}
)

// Login user
export const loginUser = command(
	v.object({
		username: v.string(),
		password: v.string()
	}),
	async (data) => {
		const response = await fetch(`${API_BASE_URL}/auth/login`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(data)
		})

		if (!response.ok) {
			const error = await response.json()
			throw new Error(error.detail || 'Login failed')
		}

		const result = await response.json()

		// Store token in locals for server-side access
		const { locals } = getRequestEvent()
		locals.token = result.access_token
		locals.user = result.user

		return result
	}
)

// Logout user
export const logoutUser = command(
	v.null(),
	async () => {
		const { locals } = getRequestEvent()
		locals.token = undefined
		locals.user = undefined

		return { success: true }
	}
)

// Get current user info
export const getCurrentUser = query(async () => {
	const { locals } = getRequestEvent()

	if (!locals.token) {
		return null
	}

	const response = await fetch(`${API_BASE_URL}/auth/me`, {
		headers: {
			'Authorization': `Bearer ${locals.token}`
		}
	})

	if (!response.ok) {
		// Token expired or invalid - clear locals
		locals.token = undefined
		locals.user = undefined
		return null
	}

	return await response.json()
})

/**
 * ANNOTATION REMOTE FUNCTIONS
 * Handle paper annotations with dual auth (JWT token or fingerprint)
 */

// Submit or update an annotation
export const annotatePaper = command(
	v.object({
		paper_id: v.string(),
		interdisciplinarity_rating: v.pipe(v.number(), v.minValue(1), v.maxValue(5)),
		confidence: v.optional(v.pipe(v.number(), v.minValue(1), v.maxValue(5))),
		fingerprint: v.optional(v.string())
	}),
	async (data) => {
		const { locals } = getRequestEvent()

		const headers: Record<string, string> = {
			'Content-Type': 'application/json'
		}

		// Add auth header if user is logged in
		if (locals.token) {
			headers['Authorization'] = `Bearer ${locals.token}`
		}

		const response = await fetch(`${API_BASE_URL}/interdisciplinarity/annotate`, {
			method: 'POST',
			headers,
			body: JSON.stringify(data)
		})

		if (!response.ok) {
			const error = await response.json()
			throw new Error(error.detail || 'Failed to submit annotation')
		}

		return await response.json()
	}
)

// Get paper by ID (with caching)
export const getPaperById = query(
	v.string(),
	async (paper_id) => {
		const response = await fetch(`${API_BASE_URL}/interdisciplinarity/papers/${paper_id}`)

		if (!response.ok) {
			const error = await response.json()
			throw new Error(error.detail || 'Failed to fetch paper')
		}

		return await response.json()
	}
)

// Get user's annotations
export const getMyAnnotations = query(
	v.optional(v.object({ fingerprint: v.optional(v.string()) })),
	async (params = {}) => {
		const { locals } = getRequestEvent()

		if (!locals.token && !params.fingerprint) {
			throw new Error('Either login or fingerprint is required')
		}

		const queryParams = new URLSearchParams()
		if (params.fingerprint) {
			queryParams.append('fingerprint', params.fingerprint)
		}

		const queryString = queryParams.toString()
		const url = `${API_BASE_URL}/interdisciplinarity/my-annotations${queryString ? `?${queryString}` : ''}`

		const headers: Record<string, string> = {}
		if (locals.token) {
			headers['Authorization'] = `Bearer ${locals.token}`
		}

		const response = await fetch(url, { headers })

		if (!response.ok) {
			const error = await response.json()
			throw new Error(error.detail || 'Failed to fetch annotations')
		}

		return await response.json()
	}
)

// Get annotation statistics
export const getAnnotationStats = query(async () => {
	const response = await fetch(`${API_BASE_URL}/interdisciplinarity/stats`)

	if (!response.ok) {
		const error = await response.json()
		throw new Error(error.detail || 'Failed to fetch statistics')
	}

	return await response.json()
})

// Get inter-annotator agreement data
export const getAgreementData = query(async () => {
	const response = await fetch(`${API_BASE_URL}/interdisciplinarity/agreement`)

	if (!response.ok) {
		const error = await response.json()
		throw new Error(error.detail || 'Failed to fetch agreement data')
	}

	return await response.json()
})

// Get works by author (ORCID or OpenAlex ID)
export const getWorksByAuthor = query(
	v.string(),
	async (author_id) => {
		const params = new URLSearchParams({ filter: `author.id:${author_id}` })
		const response = await fetch(`${API_BASE_URL}/interdisciplinarity/works?${params}`)

		if (!response.ok) {
			const error = await response.json()
			throw new Error(error.detail || 'Failed to fetch papers')
		}

		return await response.json()
	}
)

// Get community-contributed papers for general queue
export const getCommunityQueuePapers = query(async () => {
	const response = await fetch(`${API_BASE_URL}/interdisciplinarity/queue`)

	if (!response.ok) {
		const error = await response.json()
		throw new Error(error.detail || 'Failed to fetch community queue')
	}

	return await response.json()
})
