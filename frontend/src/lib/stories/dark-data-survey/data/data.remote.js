import * as v from 'valibot';
import { command, query } from '$app/server';
import { API_BASE } from '$env/static/private';

const API_BASE_URL = API_BASE || 'http://localhost:3001';

// Remote function to post survey answer (with string value conversion)
export const postAnswer = command(
	v.object({ fingerprint: v.string(), value: v.string(), field: v.string() }),
	async (data) => {
		const response = await fetch(`${API_BASE_URL}/dark-data-survey/answer`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(data)
		});

		if (!response.ok) {
			const error = await response.text();
			throw new Error(`Failed to post survey answer: ${response.status} - ${error}`);
		}

		const result = await response.json();
		console.log(`Saved ${data.field}:`, data.value, 'via API');
		return result;
	}
);

// Remote function to upsert survey answer (with direct value - number or string)
export const upsertAnswer = command(
	v.object({ fingerprint: v.string(), field: v.string(), value: v.union([v.number(), v.string()]) }),
	async (data) => {
		const response = await fetch(`${API_BASE_URL}/dark-data-survey/upsert`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(data)
		});

		if (!response.ok) {
			const error = await response.text();
			throw new Error(`Failed to upsert survey answer: ${response.status} - ${error}`);
		}

		const result = await response.json();
		console.log(`Upserted ${data.field}:`, data.value, 'via API');
		return result;
	}
);

// Remote function to get survey response by fingerprint
export const getSurveyResponse = query(
	v.string(),
	async (fingerprint) => {
		const response = await fetch(`${API_BASE_URL}/dark-data-survey/${fingerprint}`);

		if (!response.ok) {
			if (response.status === 404) {
				return null; // Survey response not found
			}
			const error = await response.text();
			throw new Error(`Failed to fetch survey response: ${response.status} - ${error}`);
		}

		return await response.json();
	}
);