import { query } from '$app/server'
import { api } from '$lib/server/api'
import * as v from 'valibot'

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