
import { query } from "$app/server";
import * as v from "valibot"
import { error } from '@sveltejs/kit';
import { API_BASE } from '$env/static/private'

const API_BASE_URL = API_BASE || 'http://localhost:8000'


export const getAvailableLocations = query(async () => {
        const url = `${API_BASE_URL}/datalakes/babynames`
        console.log('Fetching available locations:', url)

        const response = await fetch(url)
        if (!response.ok) {
            const errorText = await response.text()
            console.error('Error response:', errorText)
            throw Error(`💣️ Failed to fetch available locations: ${response.status} - ${errorText}`)
        }

        const data = await response.json()

        // Extract and transform entity_mappings into locations array
        if (data?.entity_mappings && Array.isArray(data.entity_mappings)) {
            return data.entity_mappings.map(mapping => ({
                code: mapping.local_id,
                name: mapping.entity_name || mapping.local_id
            }));
        }

        return [];
    }
);

export const getTopBabyNames = query(
    v.object({
        dates: v.string(),
        dates2: v.string(),
        location: v.optional(v.string())
    }),
    async ({ dates, dates2, location = 'united_states' }) => {

        const params = new URLSearchParams({
            dates: dates,
            dates2: dates2,
            limit: 10_000,
            location: location
        })

        const url = `${API_BASE_URL}/datalakes/babynames/top-ngrams?${params.toString()}`
        console.log(url)

        const response = await fetch(url)
        if (!response.ok) {
            const errorText = await response.text()
            console.error('Error response:', errorText)
            throw Error(`💣️ Failed to fetch top baby names: ${response.status} - ${errorText}`)
        }
        return await response.json()
    }

);
