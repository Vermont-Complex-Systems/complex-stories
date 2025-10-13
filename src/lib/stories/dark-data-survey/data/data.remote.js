import * as v from 'valibot';
import { command, query } from '$app/server';
import { eq, and, sql } from 'drizzle-orm';
import { db } from '$lib/server/db/index.js';
import { surveyResponses, trustCirclesIndividual, surveyDataAll } from '$lib/server/db/schema.ts';

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
		const column = categoryToColumn[category] || category;

		// Execute raw SQL for aggregation
		const results = await db.all(sql`
			SELECT ${sql.raw(column)} as types, COUNT(*) as count
			FROM survey_data_all
			WHERE timepoint = 1 AND ${sql.raw(column)} IS NOT NULL
			GROUP BY ${sql.raw(column)}
			ORDER BY types
		`);

		return results.map(row => ({
			types: parseFloat(row.types),
			count: row.count
		}));
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

// Get trust circles data with filters for privacy
export const getTrustCirclesData = query(
	v.object({
		timepoint: v.number(),
		category: v.string(),
		value: v.string(),
		institution: v.optional(v.string())
	}),
	async (filters) => {
		const dbColumn = categoryFieldMap[filters.category];

		// Build where conditions
		const conditions = [
			eq(trustCirclesIndividual.timepoint, filters.timepoint)
		];

		// Add category filter if not "overall_average"
		if (dbColumn && filters.value !== "1.0") {
			const numValue = parseFloat(filters.value);
			conditions.push(eq(trustCirclesIndividual[dbColumn], numValue));
		}

		// Add institution filter if provided
		if (filters.institution) {
			conditions.push(eq(trustCirclesIndividual.institution, filters.institution));
		}

		// Query database
		const rows = await db.select()
			.from(trustCirclesIndividual)
			.where(and(...conditions));

		// Calculate aggregated statistics
		const distribution = {};
		const byCategory = {};

		rows.forEach(row => {
			const distance = row.distance;
			distribution[distance] = (distribution[distance] || 0) + 1;

			const categoryValue = (row[dbColumn] || 0).toString();
			if (!byCategory[distance]) {
				byCategory[distance] = {};
			}
			byCategory[distance][categoryValue] = (byCategory[distance][categoryValue] || 0) + 1;
		});

		// Calculate demographic breakdown
		const breakdown = {
			total: rows.length,
			orientation: {
				straight: rows.filter(d => d.orientationOrd == 0).length,
				bisexual: rows.filter(d => d.orientationOrd == 1).length,
				gay: rows.filter(d => d.orientationOrd == 2).length,
				other: rows.filter(d => d.orientationOrd == 3).length
			},
			race: {
				white: rows.filter(d => d.raceOrd == 0).length,
				mixed: rows.filter(d => d.raceOrd == 1).length,
				poc: rows.filter(d => d.raceOrd == 2).length
			},
			gender: {
				women: rows.filter(d => d.genderOrd == 0).length,
				men: rows.filter(d => d.genderOrd == 1).length,
				other: rows.filter(d => d.genderOrd == 2).length
			}
		};

		return {
			distribution,
			byCategory,
			breakdown,
			count: rows.length
		};
	}
)

// Get individual points for visualization (for scrollyIndex === 1 only)
export const getIndividualPoints = query(
	v.object({
		timepoint: v.number(),
		genderOrd: v.number(),
		institution: v.string()
	}),
	async (filters) => {
		const rows = await db.select({
			distance: trustCirclesIndividual.distance,
			race_ord: trustCirclesIndividual.raceOrd,
			orientation_ord: trustCirclesIndividual.orientationOrd
		})
		.from(trustCirclesIndividual)
		.where(and(
			eq(trustCirclesIndividual.genderOrd, filters.genderOrd),
			eq(trustCirclesIndividual.institution, filters.institution),
			eq(trustCirclesIndividual.timepoint, filters.timepoint)
		));

		return rows;
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