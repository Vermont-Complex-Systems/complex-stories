import * as v from 'valibot';
import { form } from '$app/server';
import { db } from '$lib/server/db/index.js';
import { surveyResponses } from '$lib/server/db/schema.ts';

// Multi-question survey form
export const submitSurvey = form(
	v.object({
		socialMedia: v.pipe(v.string(), v.nonEmpty('Please answer: Social media privacy')),
		platformMatters: v.pipe(v.string(), v.nonEmpty('Please answer: Platform matters')),
		institutionPreferences: v.pipe(v.string(), v.nonEmpty('Please answer: Institution preferences')),
		demographicsMatter: v.pipe(v.string(), v.nonEmpty('Please answer: Demographics matter')),
		fingerprint: v.pipe(v.string(), v.nonEmpty('Fingerprint required'))
	}),
	async ({ socialMedia, platformMatters, institutionPreferences, demographicsMatter, fingerprint }) => {
		
		// Convert text responses to ordinal values
		const ordinalValues = {
			socialMediaPrivacy: socialMedia === 'private' ? 1 : socialMedia === 'mixed' ? 2 : 3,
			platformMatters: platformMatters === 'no' ? 1 : platformMatters === 'sometimes' ? 2 : 3,
			institutionPreferences: institutionPreferences === 'mostly-same' ? 1 : institutionPreferences === 'depends-context' ? 2 : 3,
			demographicsMatter: demographicsMatter === 'no' ? 1 : demographicsMatter === 'somewhat' ? 2 : 3
		};

		try {
			// Insert into database  
			await db.insert(surveyResponses).values({
				fingerprint,
				socialMediaPrivacy: ordinalValues.socialMediaPrivacy,
				platformMatters: ordinalValues.platformMatters,
				institutionPreferences: ordinalValues.institutionPreferences,
				demographicsMatter: ordinalValues.demographicsMatter,
			});

			return { success: true };

		} catch (err) {
			console.error('Survey submission error:', err);
			console.error('Error details:', err.message, err.code);
			
			// Handle duplicate fingerprint
			if (err.message && err.message.includes('UNIQUE constraint failed')) {
				return { success: false, error: 'You have already completed this survey.' };
			}
			
			return { success: false, error: 'Failed to save survey response. Please try again.' };
		}
	}
);