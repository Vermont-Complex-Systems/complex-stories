
import { query } from "$app/server";
import * as v from "valibot"
import { error } from '@sveltejs/kit';
import { API_BASE } from '$env/static/private'

const API_BASE_URL = API_BASE || 'http://localhost:3001'

export const countData = query(
     v.object({
        start_year: v.integer(),
        end_year: v.integer()
     }),
    async ({start_year, end_year}) => {
    console.log(`${API_BASE_URL}/scisciDB/field-year-counts?start_year=${start_year}&end_year=${end_year}`)
    const response = await fetch(`${API_BASE_URL}/scisciDB/field-year-counts?start_year=${start_year}&end_year=${end_year}`);
    if (!response.ok) error(404, 'Not found');
    const results = await response.json();
    return results;
  });