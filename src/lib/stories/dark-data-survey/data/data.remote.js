import * as v from 'valibot';
import { command, query } from '$app/server';
import { eq, count } from 'drizzle-orm';
import { db } from '$lib/server/db/index.js';
import { surveyResponses } from '$lib/server/db/schema.ts';
import dfall from './dfall.csv';

// We use raw JS here to avoid pushing dfall.csv into the public db...
export const countCategory = query(
	v.string(),
	async (category) => {
		const counts = dfall.filter(d => d.Timepoint == 1).reduce((acc, row) => {
			const types = row[category];
			if (types !== null && types !== undefined && types !== '') {
				acc[types] = (acc[types] || 0) + 1;
			}
			return acc;
		}, {});

		return Object.entries(counts).map(([types, count]) => ({
			types: parseFloat(types),
			count
		})).sort((a, b) => a.types - b.types);
	}
)

// Helper to upsert a single answer
async function upsertAnswer(fingerprint, field, value) {
	try {
		// First, try to find existing record
		const existing = await db.select()
								 .from(surveyResponses)
								 .where(eq(surveyResponses.fingerprint, fingerprint))
								 .get();
		
		if (existing) {
			// Update only the specific field
			await db.update(surveyResponses)
				.set({ [field]: value })
				.where(eq(surveyResponses.fingerprint, fingerprint));
		} else {
			// Insert new record
			await db.insert(surveyResponses)
				.values({
					fingerprint,
					[field]: value
				});
		}
	} catch (err) {
		console.error('Upsert error:', err);
		throw err;
	}
}

const valueToOrdinal = {
	socialMediaPrivacy: { 'private': 1, 'mixed': 2, 'public': 3 },
	platformMatters: { 'no': 1, 'sometimes': 2, 'yes': 3 },
	institutionPreferences: { 'mostly-same': 1, 'depends-context': 2, 'vary-greatly': 3 },
	demographicsMatter: { 'no': 1, 'somewhat': 2, 'yes': 3 }
};

export const postAnswer = command(
	v.object({ fingerprint: v.string(), value: v.string(), field: v.string() }),
	async (data) => {
		// Validate fingerprint is not empty
		if (!data.fingerprint || data.fingerprint.trim() === '') {
			console.error('Invalid fingerprint:', data.fingerprint);
			throw new Error('Fingerprint is required');
		}

		const ordinal = valueToOrdinal[data.field][data.value];
		if (!ordinal) {
			console.error(`Invalid value ${data.value} for field ${data.field}`);
			throw new Error(`Invalid value for field ${data.field}`);
		}

		await upsertAnswer(data.fingerprint, data.field, ordinal);
		console.log(`Saved ${data.field}:`, data.value, '(ordinal:', ordinal, ')');
	}
);