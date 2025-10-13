import * as v from 'valibot';
import { command, query } from '$app/server';
// import { eq, and, sql } from 'drizzle-orm';
// import { db } from '$lib/server/db/index.js';
// import { surveyResponses, trustCirclesIndividual, surveyDataAll } from '$lib/server/db/schema.ts';

// All database functionality commented out - not currently in use

// Map friendly category names to database column names
const categoryToColumn = {
	'socialMediaPrivacy': 'tp_platform',
	'platformMatters': 'tp_platform',
	'institutionPreferences': 'tp_platform',
	'demographicsMatter': 'gender_ord'
};

// Query aggregated counts from database
export const countCategory = query(
	v.string(),
	async (category) => {
		// Database functionality disabled
		return [];
		// const column = categoryToColumn[category] || category;
		// const results = await db.all(sql`
		// 	SELECT ${sql.raw(column)} as types, COUNT(*) as count
		// 	FROM survey_data_all
		// 	WHERE timepoint = 1 AND ${sql.raw(column)} IS NOT NULL
		// 	GROUP BY ${sql.raw(column)}
		// 	ORDER BY types
		// `);
		// return results.map(row => ({
		// 	types: parseFloat(row.types),
		// 	count: row.count
		// }));
	}
)

// Map category names to database column names
const categoryFieldMap = {
	'overall_average': null, // No filtering needed
	'gender_ord': 'genderOrd',
	'orientation_ord': 'orientationOrd',
	'race_ord': 'raceOrd',
	'multi_platform_ord': 'multiPlatformOrd',
	'ACES_Compound': 'acesCompound',
	'Dem_Relationship_Status_Single': 'relationshipStatusSingle'
};


// Helper to upsert a single answer
async function upsertAnswer(fingerprint, field, value) {
	// Database functionality disabled
	return;
	// try {
	// 	// First, try to find existing record
	// 	const existing = await db.select()
	// 						 .from(surveyResponses)
	// 						 .where(eq(surveyResponses.fingerprint, fingerprint))
	// 						 .get();
	//
	// 	if (existing) {
	// 		// Update only the specific field
	// 		await db.update(surveyResponses)
	// 			.set({ [field]: value })
	// 			.where(eq(surveyResponses.fingerprint, fingerprint));
	// 	} else {
	// 		// Insert new record
	// 		await db.insert(surveyResponses)
	// 			.values({
	// 				fingerprint,
	// 				[field]: value
	// 			});
	// 	}
	// } catch (err) {
	// 	console.error('Upsert error:', err);
	// 	throw err;
	// }
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
		// Database functionality disabled
		console.log('Survey response (not saved):', data);
		return;
		// // Validate fingerprint is not empty
		// if (!data.fingerprint || data.fingerprint.trim() === '') {
		// 	console.error('Invalid fingerprint:', data.fingerprint);
		// 	throw new Error('Fingerprint is required');
		// }
		// const ordinal = valueToOrdinal[data.field][data.value];
		// if (!ordinal) {
		// 	console.error(`Invalid value ${data.value} for field ${data.field}`);
		// 	throw new Error(`Invalid value for field ${data.field}`);
		// }
		// await upsertAnswer(data.fingerprint, data.field, ordinal);
		// console.log(`Saved ${data.field}:`, data.value, '(ordinal:', ordinal, ')');
	}
);
