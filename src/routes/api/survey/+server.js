import { json } from '@sveltejs/kit';
import { eq } from 'drizzle-orm';
import { db } from '$lib/server/db/index.js';
import { surveyResponses } from '$lib/server/db/schema.ts';

const valueToOrdinal = {
	socialMediaPrivacy: { 'private': 1, 'mixed': 2, 'public': 3 },
	platformMatters: { 'no': 1, 'sometimes': 2, 'yes': 3 },
	institutionPreferences: { 'mostly-same': 1, 'depends-context': 2, 'vary-greatly': 3 },
	demographicsMatter: { 'no': 1, 'somewhat': 2, 'yes': 3 }
};

export async function POST({ request }) {
	try {
		const { fingerprint, value, field } = await request.json();

		// Validate inputs
		if (!fingerprint || fingerprint.trim() === '') {
			console.error('Invalid fingerprint:', fingerprint);
			return json({ error: 'Fingerprint is required' }, { status: 400 });
		}

		if (!valueToOrdinal[field]) {
			console.error('Invalid field:', field);
			return json({ error: 'Invalid field' }, { status: 400 });
		}

		const ordinal = valueToOrdinal[field][value];
		if (!ordinal) {
			console.error(`Invalid value ${value} for field ${field}`);
			return json({ error: `Invalid value for field ${field}` }, { status: 400 });
		}

		// Check if record exists
		const existing = await db.select()
			.from(surveyResponses)
			.where(eq(surveyResponses.fingerprint, fingerprint))
			.get();

		if (existing) {
			// Update only the specific field
			await db.update(surveyResponses)
				.set({ [field]: ordinal })
				.where(eq(surveyResponses.fingerprint, fingerprint));
		} else {
			// Insert new record
			await db.insert(surveyResponses)
				.values({
					fingerprint,
					[field]: ordinal
				});
		}

		console.log(`Saved ${field}:`, value, '(ordinal:', ordinal, ')');
		return json({ success: true });

	} catch (err) {
		console.error('Survey save error:', err);
		return json({ error: err.message }, { status: 500 });
	}
}
