import * as v from 'valibot';
import { command, query } from '$app/server';
import { eq } from 'drizzle-orm';
import { db } from '$lib/server/db/index.js';
import { surveyResponses } from '$lib/server/db/schema.ts';

// Import CSV files - the DSV plugin will handle these
import dfall from './dfall.csv';
import trust_circles_individual from './trust_circles_individual.csv';

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

// Get trust circles data with filters for privacy
export const getTrustCirclesData = query(
	v.object({
		timepoint: v.number(),
		category: v.string(),
		value: v.string(),
		institution: v.optional(v.string())
	}),
	async (filters) => {
		let filtered = trust_circles_individual.filter(
			d => d.Timepoint == filters.timepoint &&
			     parseFloat(d[filters.category]) === parseFloat(filters.value)
		);

		if (filters.institution) {
			filtered = filtered.filter(d => d.institution === filters.institution);
		}

		// Calculate aggregated statistics
		const distribution = {};
		const byCategory = {};

		filtered.forEach(d => {
			const distance = parseFloat(d.distance);
			distribution[distance] = (distribution[distance] || 0) + 1;

			const categoryValue = d[filters.category]?.toString() || '0';
			if (!byCategory[distance]) {
				byCategory[distance] = {};
			}
			byCategory[distance][categoryValue] = (byCategory[distance][categoryValue] || 0) + 1;
		});

		// Calculate demographic breakdown
		const breakdown = {
			total: filtered.length,
			orientation: {
				straight: filtered.filter(d => d.orientation_ord == 0).length,
				bisexual: filtered.filter(d => d.orientation_ord == 1).length,
				gay: filtered.filter(d => d.orientation_ord == 2).length,
				other: filtered.filter(d => d.orientation_ord == 3).length
			},
			race: {
				white: filtered.filter(d => d.race_ord == 0).length,
				mixed: filtered.filter(d => d.race_ord == 1).length,
				poc: filtered.filter(d => d.race_ord == 2).length
			},
			gender: {
				women: filtered.filter(d => d.gender_ord == 0).length,
				men: filtered.filter(d => d.gender_ord == 1).length,
				other: filtered.filter(d => d.gender_ord == 2).length
			}
		};

		return {
			distribution,
			byCategory,
			breakdown,
			count: filtered.length
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
		const filtered = trust_circles_individual.filter(d => {
			return d.gender_ord == filters.genderOrd &&
			       d.institution === filters.institution &&
			       d.Timepoint == filters.timepoint;
		});

		// Return only necessary fields, not entire rows
		return filtered.map(d => ({
			distance: parseFloat(d.distance),
			race_ord: d.race_ord,
			orientation_ord: d.orientation_ord
		}));
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