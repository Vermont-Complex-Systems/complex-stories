import { error } from '@sveltejs/kit'
import { command, form, query } from '$app/server'
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

// GET all annotations with optional filtering
export const getAnnotations = query(
	filterAnnotationsSchema,
	async (filters = {}) => {
		const params = new URLSearchParams()

		if (filters?.skip !== undefined) params.append('skip', filters.skip.toString())
		if (filters?.payroll_year !== undefined) params.append('payroll_year', filters.payroll_year.toString())

		const queryString = params.toString()
		const endpoint = `/academic-research-groups${queryString ? `?${queryString}` : ''}`

		const data = await apiCall(endpoint)

		// Validate response data
		return v.parse(v.array(annotationSchema), data)
	}
)

// GET single annotation by record ID
export const getAnnotation = query(
	v.pipe(v.number(), v.minValue(1, 'Record ID is required')),
	async (record_id: number) => {
		const data = await apiCall(`/academic-research-groups/${record_id}`)

		// Validate response data
		return v.parse(annotationSchema, data)
	}
)

// CREATE new annotation (requires authentication)
export const createAnnotation = form(
	createAnnotationSchema,
	async (annotation: CreateAnnotation) => {
		if (!isLoggedIn()) {
			error(401, 'You must be logged in to create annotations')
		}

		const data = await apiCall('/academic-research-groups', {
			method: 'POST',
			body: JSON.stringify(annotation),
		})

		// Validate response data
		const created = v.parse(annotationSchema, data)

		// Refresh the annotations list
		getAnnotations().refresh()

		return created
	}
)

// UPDATE existing annotation by record ID (requires authentication)
export const updateAnnotation = form(
	updateAnnotationSchema,
	async (annotation: UpdateAnnotation) => {
		if (!isLoggedIn()) {
			error(401, 'You must be logged in to update annotations')
		}

		const { id, ...updateData } = annotation

		const data = await apiCall(`/academic-research-groups/${id}`, {
			method: 'PUT',
			body: JSON.stringify(updateData),
		})

		// Validate response data
		const updated = v.parse(annotationSchema, data)

		// Refresh the annotations list and the specific annotation
		getAnnotations().refresh()
		getAnnotation(id).refresh()

		return updated
	}
)

// DELETE annotation by record ID (requires authentication)
export const removeAnnotation = form(
	deleteAnnotationSchema,
	async ({ id }: { id: number }) => {
		if (!isLoggedIn()) {
			error(401, 'You must be logged in to delete annotations')
		}

		await apiCall(`/academic-research-groups/${id}`, {
			method: 'DELETE',
		})

		// Refresh the annotations list
		getAnnotations().refresh()

		return { success: true, id }
	}
)

// BULK CREATE annotations (requires authentication)
export const bulkCreateAnnotations = form(
	bulkCreateAnnotationsSchema,
	async (annotations: CreateAnnotation[]) => {
		if (!isLoggedIn()) {
			error(401, 'You must be logged in to create annotations')
		}

		const data = await apiCall('/academic-research-groups/bulk', {
			method: 'POST',
			body: JSON.stringify(annotations),
		})

		// Validate response data
		const created = v.parse(v.array(annotationSchema), data)

		// Refresh the annotations list
		getAnnotations().refresh()

		return created
	}
)

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

		// Refresh the specific annotation and list
		getAnnotation(id).refresh()
		getAnnotations().refresh()
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

		// Refresh the annotations list
		getAnnotations().refresh()
	}
)

