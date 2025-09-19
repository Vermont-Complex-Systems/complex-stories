import { sqliteTable, integer, text, customType } from 'drizzle-orm/sqlite-core';
import { sql } from 'drizzle-orm';

// Custom ordinal type for survey responses (1-3 scale typically)
const ordinalResponse = customType<{ data: number; notNull: false; default: false }>({
  dataType() {
    return 'integer';
  },
  toDriver(value: number): number {
    // Ensure value is within valid ordinal range (1-3 for most survey questions)
    return Math.max(1, Math.min(3, Math.round(value)));
  },
  fromDriver(value: unknown): number {
    return typeof value === 'number' ? value : 1;
  },
});

export const surveyResponses = sqliteTable('survey_responses', {
	id: integer('id').primaryKey(),
	// Browser fingerprint for duplicate prevention (unique constraint)
	fingerprint: text('fingerprint').notNull().unique(),
	// Q1: Social media privacy (1=private, 2=mixed, 3=public)
	socialMediaPrivacy: ordinalResponse('social_media_privacy'),
	// Q2: Platform matters (1=no, 2=sometimes, 3=yes)
	platformMatters: ordinalResponse('platform_matters'),
	// Q3: Institution preferences (1=mostly same, 2=depends context, 3=vary greatly)
	institutionPreferences: ordinalResponse('institution_preferences'),
	// Q4: Demographics matter (1=no, 2=somewhat, 3=yes)
	demographicsMatter: ordinalResponse('demographics_matter'),
	// Timestamp (SQLite uses integer for timestamps)
	createdAt: integer('created_at', { mode: 'timestamp' })
		.notNull()
		.default(sql`(unixepoch())`),
});
