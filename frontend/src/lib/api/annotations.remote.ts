import { query, command, getRequestEvent } from '$app/server'
import { api } from '$lib/server/api'
import * as v from 'valibot'

// Cache annotations data - lazy loading to avoid top-level await
let annotations: any[] | null = null

export const getAnnotations = query(async () => {
	if (annotations === null) {
		annotations = await api.getAnnotations()
	}
	return annotations
})

export const getAnnotationById = query(v.number(), async (id) => {
	return api.getAnnotationById(id)
})

export const quickUpdateAnnotation = command(
	v.object({
		id: v.number(),
		field: v.string(),
		value: v.any()
	}),
	async ({ id, field, value }) => {
		const { locals } = getRequestEvent()

		if (!locals.token) {
			throw new Error('💣️ Authentication required')
		}

		const updateData = { [field]: value }
		const result = await api.updateAnnotation(id, updateData, locals.token)

		// Update cached data optimistically
		if (annotations !== null) {
			const index = annotations.findIndex(a => a.id === id)
			if (index !== -1) {
				annotations[index][field] = value
			}
		}

		return result
	}
)

export const quickDeleteAnnotation = command(
	v.object({
		id: v.number()
	}),
	async ({ id }) => {
		const { locals } = getRequestEvent()

		if (!locals.token) {
			throw new Error('💣️ Authentication required')
		}

		await api.deleteAnnotation(id, locals.token)

		// Remove from cached data optimistically
		if (annotations !== null) {
			const index = annotations.findIndex(a => a.id === id)
			if (index !== -1) {
				annotations.splice(index, 1)
			}
		}

		await getAnnotations().refresh()
		return { success: true, id }
	}
)

// Label Studio specific remote functions
export const getLabelStudioProjects = query(async () => {
	console.log("getLabelStudioProjects remote function called")
	try {
		const result = await api.getLabelStudioProjects()
		console.log("API call successful, result:", result)
		return result
	} catch (error) {
		console.error("API call failed:", error)
		throw error
	}
})

export const getLabelStudioAgreement = query(
	v.optional(v.object({
		projectId: v.optional(v.number()),
		forceRefresh: v.optional(v.boolean())
	})),
	async (params = {}) => {
		const { projectId = 75, forceRefresh = false } = params
		return await api.getLabelStudioAgreement(projectId, forceRefresh)
	}
)