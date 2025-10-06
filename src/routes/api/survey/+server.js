import { json } from '@sveltejs/kit';
import { eq } from 'drizzle-orm';
import { db } from '$lib/server/db/index.js';
import { surveyResponses } from '$lib/server/db/schema.ts';

const valueToOrdinal = {
	socialMediaPrivacy: { 'private': 1, 'mixed': 2, 'public': 3 }
};

// Fields that are stored as-is (text or integer)
// relativePreferences, govPreferences, polPreferences are already numeric (1-7)
const directFields = ['consent', 'age', 'gender_ord', 'orientation_ord', 'race_ord', 'relativePreferences', 'govPreferences', 'polPreferences'];

// Fields that store arrays as JSON
const arrayFields = ['platformMatters'];

export async function POST({ request }) {
	try {
		const { fingerprint, value, field } = await request.json();

		// Validate inputs
		if (!fingerprint || fingerprint.trim() === '') {
			console.error('Invalid fingerprint:', fingerprint);
			return json({ error: 'Fingerprint is required' }, { status: 400 });
		}

		// Check if field is valid
		if (!valueToOrdinal[field] && !directFields.includes(field) && !arrayFields.includes(field)) {
			console.error('Invalid field:', field);
			return json({ error: 'Invalid field' }, { status: 400 });
		}

		// Determine the value to save
		let valueToSave;
		if (arrayFields.includes(field)) {
			// Array fields - store as JSON string
			valueToSave = Array.isArray(value) ? JSON.stringify(value) : value;
		} else if (directFields.includes(field)) {
			// Direct fields - save as-is
			valueToSave = value;
		} else {
			// Ordinal fields - convert to number
			const ordinal = valueToOrdinal[field][value];
			if (!ordinal) {
				console.error(`Invalid value ${value} for field ${field}`);
				return json({ error: `Invalid value for field ${field}` }, { status: 400 });
			}
			valueToSave = ordinal;
		}

		// Check if record exists
		const existing = await db.select()
			.from(surveyResponses)
			.where(eq(surveyResponses.fingerprint, fingerprint))
			.get();

		if (existing) {
			// Update only the specific field
			await db.update(surveyResponses)
				.set({ [field]: valueToSave })
				.where(eq(surveyResponses.fingerprint, fingerprint));
		} else {
			// Insert new record
			await db.insert(surveyResponses)
				.values({
					fingerprint,
					[field]: valueToSave
				});
		}

		console.log(`Saved ${field}:`, value, valueToSave);
		return json({ success: true });

	} catch (err) {
		console.error('Survey save error:', err);
		return json({ error: err.message }, { status: 500 });
	}
}
