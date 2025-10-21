import { query, command, getRequestEvent } from '$app/server'
import { api } from '$lib/server/api'
import * as v from 'valibot'

// Cache annotations data
let annotations = await api.getAnnotations()

export const getAnnotations = query(async () => {
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
		const index = annotations.findIndex(a => a.id === id)
		if (index !== -1) {
			annotations[index][field] = value
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
		const index = annotations.findIndex(a => a.id === id)
		if (index !== -1) {
			annotations.splice(index, 1)
		}

		await getAnnotations().refresh()
		return { success: true, id }
	}
)