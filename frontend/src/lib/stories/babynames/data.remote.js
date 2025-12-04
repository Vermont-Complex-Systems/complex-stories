
import { query } from "$app/server";
import * as v from "valibot"
import { error } from '@sveltejs/kit';
import { API_BASE } from '$env/static/private'

const API_BASE_URL = API_BASE || 'http://localhost:8000'


export const getTopBabyNames = query(
    v.object({
        dates: v.string(),
        dates2: v.string()
    }),
    async ({ dates, dates2 }) => {

        const params = new URLSearchParams({ dates: dates, dates2: dates2, limit: 10_000  })
        
        // // Handle dates - add each date range as separate parameter
        // if (dates !== undefined) {
            // if (Array.isArray(dates)) {
            //     dates.forEach(dateRange => {
            //         params.append('dates', dateRange)
            //     })
            // } else {
            //     // Single date range
            //     params.append('dates', dates)
            // }
        // }

        // // Handle locations - add each location as separate parameter
        // if (locations !== undefined) {
        //     if (Array.isArray(locations)) {
        //         locations.forEach(location => {
        //             params.append('locations', location)
        //         })
        //     } else {
        //         // Single location
        //         params.append('locations', locations)
        //     }
        // }

        // if (sex !== undefined) params.append('sex', sex)
        // if (topN !== undefined) params.append('limit', topN.toString())

        // const queryString = params.toString()
        // const url = `${API_BASE_URL}/datalakes/babynames/top-ngrams${queryString ? `?${queryString}` : ''}`

        // const url = `${API_BASE_URL}/datalakes/babynames/top-ngrams?dates=1991%2C1993&${locations}&sex=M&limit=100`
        
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
