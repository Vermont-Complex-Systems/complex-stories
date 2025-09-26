import * as v from 'valibot';
import { command } from '$app/server';
import { eq } from 'drizzle-orm';
import { db } from '$lib/server/db/index.js';
import { surveyResponses } from '$lib/server/db/schema.ts';
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
		const ordinal = valueToOrdinal[data.field][data.value];
		await upsertAnswer(data.fingerprint, data.field, ordinal);
		console.log(`Saved ${data.field}:`, data.value);
	}
);