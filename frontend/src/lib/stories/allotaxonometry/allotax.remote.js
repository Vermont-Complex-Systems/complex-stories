
import { query } from "$app/server";
import * as v from "valibot"
import { error } from '@sveltejs/kit';
import { API_BASE } from '$env/static/private'

const API_BASE_URL = API_BASE || 'http://localhost:8000'


export const getAdapter = query(async () => {
        const url = `${API_BASE_URL}/datalakes/babynames/adapter`
        console.log('Fetching available locations:', url)

        const response = await fetch(url)
        if (!response.ok) {
            const errorText = await response.text()
            console.error('Error response:', errorText)
            throw Error(`💣️ Failed to fetch available locations: ${response.status} - ${errorText}`)
        }

        return await response.json()
    }
);

export const getTopBabyNames = query(
    v.object({
        dates: v.string(),
        dates2: v.string(),
        location: v.optional(v.string()),
        sex: v.optional(v.string()),
        limit: v.integer()
    }),
    async ({ dates, dates2, location = 'wikidata:Q30', sex = 'M', limit = 10_000}) => {

        const params = new URLSearchParams({
            dates: dates,
            dates2: dates2,
            location: location,
            sex: sex,
            limit: limit,
        })

        const url = `${API_BASE_URL}/datalakes/babynames/top-ngrams?${params.toString()}`

        const response = await fetch(url)
        if (!response.ok) {
            const errorText = await response.text()
            console.error('Error response:', errorText)
            throw Error(`💣️ Failed to fetch top baby names: ${response.status} - ${errorText}`)
        }
        return await response.json()
    }

);
