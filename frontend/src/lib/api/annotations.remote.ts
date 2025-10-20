import { error } from '@sveltejs/kit'
import { command } from '$app/server'
import * as v from 'valibot'
import {
	annotationSchema,
	createAnnotationSchema,
	updateAnnotationSchema,
	deleteAnnotationSchema,
	filterAnnotationsSchema,
	bulkCreateAnnotationsSchema,
	type CreateAnnotation,
	type UpdateAnnotation,
	type FilterAnnotations
} from '$lib/schema/annotations'

// API base URL - adjust as needed
const API_BASE = 'http://localhost:8000/datasets'

// Import auth client for token management
import { getAuthToken } from '$lib/auth.svelte'
import { isLoggedIn } from '$lib/auth.svelte'

// Helper function for API calls with optional auth header
async function apiCall(endpoint: string, options: RequestInit = {}) {
	const url = `${API_BASE}${endpoint}`

	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		...options.headers as Record<string, string>,
	}

	// Add auth header if we have a token (for authenticated operations)
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

// Convenience command for quick field updates without full form validation (requires authentication)
export const quickUpdateAnnotation = command(
	v.object({
		id: v.pipe(v.number(), v.minValue(1)),
		field: v.string(),
		value: v.any(),
	}),
	async ({ id, field, value }) => {
		if (!isLoggedIn()) {
			error(401, 'You must be logged in to update annotations')
		}

		const updateData = { [field]: value }

		await apiCall(`/academic-research-groups/${id}`, {
			method: 'PUT',
			body: JSON.stringify(updateData),
		})
	}
)

// Convenience command for quick delete without full form validation (requires authentication)
export const quickDeleteAnnotation = command(
	v.object({
		id: v.pipe(v.number(), v.minValue(1)),
	}),
	async ({ id }) => {
		if (!isLoggedIn()) {
			error(401, 'You must be logged in to delete annotations')
		}

		await apiCall(`/academic-research-groups/${id}`, {
			method: 'DELETE',
		})
	}
)

