// Clean server-side API utilities
// Simple functions that can be used in load functions, server actions, etc.

import { API_BASE } from '$env/static/private'

const API_BASE_URL = API_BASE || 'http://localhost:3001'

async function getAnnotations(filters: { skip?: number; payroll_year?: number } = {}) {
    const params = new URLSearchParams()
    if (filters.skip !== undefined) params.append('skip', filters.skip.toString())
    if (filters.payroll_year !== undefined) params.append('payroll_year', filters.payroll_year.toString())

    const queryString = params.toString()
    const url = `${API_BASE_URL}/datasets/academic-research-groups${queryString ? `?${queryString}` : ''}`

    const response = await fetch(url)
    if (!response.ok) throw Error(`💣️ Failed to fetch annotations: ${response.status}`)
    return await response.json()
}

async function getAnnotationById(id: number) {
    const response = await fetch(`${API_BASE_URL}/datasets/academic-research-groups/${id}`)
    if (!response.ok) throw Error(`💣️ Failed to fetch annotation ${id}: ${response.status}`)
    return await response.json()
}

async function updateAnnotation(id: number, data: any, token: string) {
    const response = await fetch(`${API_BASE_URL}/datasets/academic-research-groups/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
    })
    if (!response.ok) throw Error(`💣️ Failed to update annotation ${id}: ${response.status}`)
    return await response.json()
}

async function deleteAnnotation(id: number, token: string) {
    const response = await fetch(`${API_BASE_URL}/datasets/academic-research-groups/${id}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    if (!response.ok) throw Error(`💣️ Failed to delete annotation ${id}: ${response.status}`)
    return await response.json()
}

async function createAnnotation(data: any, token: string) {
    const response = await fetch(`${API_BASE_URL}/datasets/academic-research-groups`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
    })
    if (!response.ok) throw Error(`💣️ Failed to create annotation: ${response.status}`)
    return await response.json()
}

async function getTopNgrams(filters: {
    dates?: Date | Date[];
    countries?: string | string[];
    topN?: number
} = {}) {
    const params = new URLSearchParams()

    // Handle dates - properly convert Date objects to YYYY-MM-DD format
    if (filters.dates !== undefined) {
        let dateString
        if (Array.isArray(filters.dates)) {
            dateString = filters.dates.map(d => {
                // Convert Date object to YYYY-MM-DD
                return d.toISOString().split('T')[0]
            }).join(',')
        } else {
            // Single date
            dateString = filters.dates.toISOString().split('T')[0]
        }
        params.append('dates', dateString)
    }

    // Handle countries (convert array to comma-separated string)
    if (filters.countries !== undefined) {
        const countryString = Array.isArray(filters.countries)
            ? filters.countries.join(',')
            : filters.countries
        params.append('countries', countryString)
    }

    if (filters.topN !== undefined) params.append('topN', filters.topN.toString())

    const queryString = params.toString()
    const url = `${API_BASE_URL}/wikimedia/top-ngrams${queryString ? `?${queryString}` : ''}`

    console.log('Full URL:', url)
    console.log('Query string:', queryString)

    const response = await fetch(url)
    if (!response.ok) {
        const errorText = await response.text()
        console.error('Error response:', errorText)
        throw Error(`💣️ Failed to fetch top ngrams: ${response.status} - ${errorText}`)
    }
    return await response.json()
}

async function getLabelStudioProjects() {
    const url = `${API_BASE_URL}/annotations/`
    console.log(`Fetching Label Studio projects from: ${url}`)
    console.log(`API_BASE_URL is: ${API_BASE_URL}`)
    const response = await fetch(url)
    console.log(`Response status: ${response.status}`)
    if (!response.ok) throw Error(`💣️ Failed to fetch Label Studio projects: ${response.status}`)
    return await response.json()
}

async function getLabelStudioAgreement(projectId: number = 75, forceRefresh: boolean = false) {
    const params = new URLSearchParams()
    if (forceRefresh) params.append('force_refresh', 'true')

    const queryString = params.toString()
    const url = `${API_BASE_URL}/annotations/projects/${projectId}/agreement${queryString ? `?${queryString}` : ''}`

    const response = await fetch(url)
    if (!response.ok) throw Error(`💣️ Failed to fetch agreement data for project ${projectId}: ${response.status}`)
    return await response.json()
}

export const api = {
    getAnnotations,
    getAnnotationById,
    updateAnnotation,
    deleteAnnotation,
    createAnnotation,
    getTopNgrams,
    getLabelStudioProjects,
    getLabelStudioAgreement
}