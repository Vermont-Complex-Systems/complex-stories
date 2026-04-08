
import { query } from "$app/server";
import * as v from "valibot"
import { error } from '@sveltejs/kit';
import { env } from '$env/dynamic/private'

const API_BASE_URL = env.STORYWRANGLER_API_BASE || 'http://localhost:8000'


export const getAdapter = query(async () => {
        const url = `${API_BASE_URL}/registry/babynames/ngrams/adapter`
        const response = await fetch(url)
        if (!response.ok) {
            const errorText = await response.text()
            throw Error(`💣️ Failed to fetch adapter: ${response.status} - ${errorText}`)
        }
        return await response.json()
    }
);

export const getTopBabyNames = query(
    v.object({
        dates: v.string(),
        dates2: v.string(),
        locations: v.optional(v.string()),
        sex: v.optional(v.string()),
        limit: v.integer()
    }),
    async ({ dates, dates2, locations = 'wikidata:Q30', sex = 'M', limit = 10_000}) => {

        const params = new URLSearchParams({
            dates: dates,
            dates2: dates2,
            locations: locations,
            sex: sex,
            limit: limit,
        })

        const url = `${API_BASE_URL}/babynames/ngrams?${params.toString()}`

        const response = await fetch(url)
        if (!response.ok) {
            const errorText = await response.text()
            console.error('Error response:', errorText)
            throw Error(`💣️ Failed to fetch top baby names: ${response.status} - ${errorText}`)
        }
        return await response.json()
    }

);
