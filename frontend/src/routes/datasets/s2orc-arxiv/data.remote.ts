import { query, command } from '$app/server'
import { browser } from '$app/environment'
import * as v from 'valibot'
import { getAuthToken } from '$lib/auth.svelte'
import { API_BASE } from '$env/static/private'

const API_BASE_URL = `${API_BASE || 'http://localhost:3001'}/datasets`

// Schema for dataset stats
const statsSchema = v.object({
	status: v.string(),
	message: v.string(),
	tables: v.array(v.string()),
	fulltext_stats: v.optional(v.object({
		total_arxiv: v.number(),
		with_fulltext: v.number(),
		null_fulltext: v.number()
	}))
})

// Schema for yearly stats
const yearlyStatsSchema = v.object({
	total_papers: v.number(),
	yearly_stats: v.record(v.string(), v.object({
		papers: v.number(),
		avg_text_length: v.number()
	})),
	estimated_size: v.object({
		bytes: v.number(),
		gb: v.number()
	}),
	avg_text_length: v.number()
})

// Schema for streaming parameters
const streamParamsSchema = v.object({
	year: v.optional(v.number()),
	format: v.optional(v.string())
})


// Helper function for authenticated API calls
async function authenticatedApiCall(endpoint: string, options: RequestInit = {}) {
	const token = getAuthToken()
	if (!token) {
		throw new Error('Authentication required')
	}

	const headers: Record<string, string> = {
		'Authorization': `Bearer ${token}`,
		...options.headers as Record<string, string>,
	}

	const response = await fetch(`${API_BASE_URL}${endpoint}`, {
		headers,
		...options,
	})

	if (!response.ok) {
		if (response.status === 401) {
			throw new Error('Invalid or expired authentication token')
		}
		throw new Error(`API Error: ${response.status}`)
	}

	return response
}



// Get yearly statistics for S2ORC arXiv dataset
export const getYearlyStats = query(
	async () => {
		try {
			const response = await authenticatedApiCall('/s2orc/arxiv/stats')
			const data = await response.json()
			return v.parse(yearlyStatsSchema, data)
		} catch (error) {
			console.error('Error fetching yearly stats:', error)
			throw error
		}
	}
)