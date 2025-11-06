#!/usr/bin/env node
/**
 * Migration script to load CSV survey data into SQLite database
 * Run with: node scripts/migrate-survey-data.js
 */

import { readFileSync } from 'fs';
import { csvParse } from 'd3-dsv';
import { db } from '../src/lib/server/db/index.js';
import { trustCirclesIndividual, surveyDataAll } from '../src/lib/server/db/schema.ts';

console.log('🔄 Starting survey data migration...\n');

// Load and parse trust_circles_individual.csv
console.log('📊 Loading trust_circles_individual.csv...');
const trustCirclesData = csvParse(
	readFileSync('src/lib/stories/dark-data-survey/data/trust_circles_individual.csv', 'utf-8')
);
console.log(`   Found ${trustCirclesData.length} rows`);

// Load and parse dfall.csv
console.log('📊 Loading dfall.csv...');
const dfallData = csvParse(
	readFileSync('src/lib/stories/dark-data-survey/data/dfall.csv', 'utf-8')
);
console.log(`   Found ${dfallData.length} rows\n`);

// Insert trust_circles_individual data
console.log('💾 Inserting trust_circles_individual data...');
try {
	const trustCirclesInserts = trustCirclesData.map(row => ({
		respondentId: parseInt(row.respondent_id),
		genderOrd: row.gender_ord ? parseInt(row.gender_ord) : null,
		relationshipStatusSingle: row.Dem_Relationship_Status_Single ? parseFloat(row.Dem_Relationship_Status_Single) : null,
		orientationOrd: row.orientation_ord ? parseInt(row.orientation_ord) : null,
		raceOrd: row.race_ord ? parseInt(row.race_ord) : null,
		multiPlatformOrd: row.multi_platform_ord ? parseInt(row.multi_platform_ord) : null,
		acesCompound: row.ACES_Compound ? parseFloat(row.ACES_Compound) : null,
		timepoint: parseInt(row.Timepoint),
		institution: row.institution,
		distance: parseFloat(row.distance)
	}));

	// Batch insert in chunks of 500 to avoid SQLite limits
	const chunkSize = 500;
	for (let i = 0; i < trustCirclesInserts.length; i += chunkSize) {
		const chunk = trustCirclesInserts.slice(i, i + chunkSize);
		await db.insert(trustCirclesIndividual).values(chunk);
		process.stdout.write(`\r   Inserted ${Math.min(i + chunkSize, trustCirclesInserts.length)} / ${trustCirclesInserts.length} rows`);
	}
	console.log('\n   ✅ trust_circles_individual data inserted successfully');
} catch (error) {
	console.error('\n   ❌ Error inserting trust_circles_individual:', error.message);
	process.exit(1);
}

// Insert dfall data
console.log('\n💾 Inserting dfall data...');
try {
	const dfallInserts = dfallData.map((row, index) => ({
		respondentId: row.ID ? parseInt(row.ID) : index,
		timepoint: parseInt(row.Timepoint || 1),
		tpSocial: row.TP_Social ? parseFloat(row.TP_Social) : null,
		tpGov: row.TP_Gov ? parseFloat(row.TP_Gov) : null,
		tpPolice: row.TP_Police ? parseFloat(row.TP_Police) : null,
		tpFriend: row.TP_Friend ? parseFloat(row.TP_Friend) : null,
		tpRelative: row.TP_Relative ? parseFloat(row.TP_Relative) : null,
		tpEmployer: row.TP_Employer ? parseFloat(row.TP_Employer) : null,
		tpMedical: row.TP_Medical ? parseFloat(row.TP_Medical) : null,
		tpFinancial: row.TP_Financial ? parseFloat(row.TP_Financial) : null,
		tpNeighbor: row.TP_Neighbor ? parseFloat(row.TP_Neighbor) : null,
		tpAcquaintance: row.TP_Acquaintance ? parseFloat(row.TP_Acquaintance) : null,
		tpCoWorker: row.TP_Co_worker ? parseFloat(row.TP_Co_worker) : null,
		tpSchool: row.TP_School ? parseFloat(row.TP_School) : null,
		tpResearcher: row.TP_Researcher ? parseFloat(row.TP_Researcher) : null,
		tpPlatform: row.TP_Platform ? parseFloat(row.TP_Platform) : null,
		tpNonProf: row.TP_NonProf ? parseFloat(row.TP_NonProf) : null,
		tpCompanyCust: row.TP_Company_cust ? parseFloat(row.TP_Company_cust) : null,
		tpCompanyNotcust: row.TP_Company_notcust ? parseFloat(row.TP_Company_notcust) : null,
		tpStranger: row.TP_Stranger ? parseFloat(row.TP_Stranger) : null,
		genderOrd: row.Dem_Gender_Woman === '1.0' ? 0 : row.Dem_Gender_Man === '1.0' ? 1 : 2,
		orientationOrd: row.Dem_Sexual_Orientation_straight === '1.0' ? 0 :
		                row.Dem_Sexual_Orientation_Bisexual === '1.0' ? 1 :
		                row.Dem_Sexual_Orientation_Gay === '1.0' ? 2 : 3,
		raceOrd: row.Dem_Race_White === '1.0' ? 0 : row.Dem_Race_Mixed === '1.0' ? 1 : 2,
		relationshipStatusSingle: row.Dem_Relationship_Status_Single ? parseFloat(row.Dem_Relationship_Status_Single) : null,
		multiPlatformOrd: row.multi_platform_ord ? parseInt(row.multi_platform_ord) : null,
		acesCompound: row.ACES_Compound ? parseFloat(row.ACES_Compound) : null
	}));

	// Batch insert in chunks
	const chunkSize = 500;
	for (let i = 0; i < dfallInserts.length; i += chunkSize) {
		const chunk = dfallInserts.slice(i, i + chunkSize);
		await db.insert(surveyDataAll).values(chunk);
		process.stdout.write(`\r   Inserted ${Math.min(i + chunkSize, dfallInserts.length)} / ${dfallInserts.length} rows`);
	}
	console.log('\n   ✅ dfall data inserted successfully');
} catch (error) {
	console.error('\n   ❌ Error inserting dfall:', error.message);
	process.exit(1);
}

console.log('\n✅ Migration completed successfully!');
console.log('\n📊 Summary:');
console.log(`   - trust_circles_individual: ${trustCirclesData.length} rows`);
console.log(`   - survey_data_all: ${dfallData.length} rows`);
