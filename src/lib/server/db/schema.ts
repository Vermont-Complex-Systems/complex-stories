import { sqliteTable, integer, text, real, customType } from 'drizzle-orm/sqlite-core';
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
	// Consent (accepted/declined)
	consent: text('consent'),
	// Q1: Social media privacy (1=private, 2=mixed, 3=public)
	socialMediaPrivacy: ordinalResponse('social_media_privacy'),
	// Q2: Which social media platforms (stored as JSON array)
	platformMatters: text('platform_matters'),
	// Q3: Comfort sharing PII with relatives (1-7 scale)
	relativePreferences: integer('relative_preferences'),
	// Q4: Comfort sharing PII with government (1-7 scale)
	govPreferences: integer('gov_preferences'),
	// Q5: Comfort sharing PII with police (1-7 scale)
	polPreferences: integer('pol_preferences'),
	// Demographics - optional
	age: text('age'),
	gender_ord: integer('gender_ord'),
	orientation_ord: integer('orientation_ord'),
	race_ord: integer('race_ord'),
	// Timestamp (SQLite uses integer for timestamps)
	createdAt: integer('created_at', { mode: 'timestamp' })
		.notNull()
		.default(sql`(unixepoch())`),
});

// Trust circles individual data (from CSV)
export const trustCirclesIndividual = sqliteTable('trust_circles_individual', {
	id: integer('id').primaryKey({ autoIncrement: true }),
	respondentId: integer('respondent_id').notNull(),
	genderOrd: integer('gender_ord'),
	relationshipStatusSingle: real('relationship_status_single'),
	orientationOrd: integer('orientation_ord'),
	raceOrd: integer('race_ord'),
	multiPlatformOrd: integer('multi_platform_ord'),
	acesCompound: real('aces_compound'),
	timepoint: integer('timepoint').notNull(),
	institution: text('institution').notNull(),
	distance: real('distance').notNull(),
});

// Overall aggregate data (from dfall.csv)
export const surveyDataAll = sqliteTable('survey_data_all', {
	id: integer('id').primaryKey({ autoIncrement: true }),
	respondentId: integer('respondent_id').notNull(),
	timepoint: integer('timepoint').notNull(),
	// Trust preference columns (1-7 scale)
	tpSocial: real('tp_social'),
	tpGov: real('tp_gov'),
	tpPolice: real('tp_police'),
	tpFriend: real('tp_friend'),
	tpRelative: real('tp_relative'),
	tpEmployer: real('tp_employer'),
	tpMedical: real('tp_medical'),
	tpFinancial: real('tp_financial'),
	tpNeighbor: real('tp_neighbor'),
	tpAcquaintance: real('tp_acquaintance'),
	tpCoWorker: real('tp_co_worker'),
	tpSchool: real('tp_school'),
	tpResearcher: real('tp_researcher'),
	tpPlatform: real('tp_platform'),
	tpNonProf: real('tp_non_prof'),
	tpCompanyCust: real('tp_company_cust'),
	tpCompanyNotcust: real('tp_company_notcust'),
	tpStranger: real('tp_stranger'),
	// Demographics
	genderOrd: integer('gender_ord'),
	orientationOrd: integer('orientation_ord'),
	raceOrd: integer('race_ord'),
	relationshipStatusSingle: real('relationship_status_single'),
	multiPlatformOrd: integer('multi_platform_ord'),
	acesCompound: real('aces_compound'),
});

