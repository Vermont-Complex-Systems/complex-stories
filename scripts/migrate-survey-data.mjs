#!/usr/bin/env node
/**
 * Migration script to load CSV survey data into SQLite database
 * Run with: node scripts/migrate-survey-data.mjs
 */

import { readFileSync } from 'fs';
import { csvParse } from 'd3-dsv';
import Database from 'better-sqlite3';

const db = new Database('./privacy.db');

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
const trustInsertStmt = db.prepare(`
	INSERT INTO trust_circles_individual (
		respondent_id, gender_ord, relationship_status_single, orientation_ord,
		race_ord, multi_platform_ord, aces_compound, timepoint, institution, distance
	) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
`);

const trustInsertMany = db.transaction((rows) => {
	for (const row of rows) {
		trustInsertStmt.run(
			parseInt(row.respondent_id),
			row.gender_ord ? parseInt(row.gender_ord) : null,
			row.Dem_Relationship_Status_Single ? parseFloat(row.Dem_Relationship_Status_Single) : null,
			row.orientation_ord ? parseInt(row.orientation_ord) : null,
			row.race_ord ? parseInt(row.race_ord) : null,
			row.multi_platform_ord ? parseInt(row.multi_platform_ord) : null,
			row.ACES_Compound ? parseFloat(row.ACES_Compound) : null,
			parseInt(row.Timepoint),
			row.institution,
			parseFloat(row.distance)
		);
	}
});

try {
	trustInsertMany(trustCirclesData);
	console.log(`   ✅ Inserted ${trustCirclesData.length} rows successfully`);
} catch (error) {
	console.error('\n   ❌ Error:', error.message);
}

// Insert dfall data
console.log('\n💾 Inserting dfall data...');
const dfallInsertStmt = db.prepare(`
	INSERT INTO survey_data_all (
		respondent_id, timepoint, tp_social, tp_gov, tp_police, tp_friend, tp_relative,
		tp_employer, tp_medical, tp_financial, tp_neighbor, tp_acquaintance, tp_co_worker,
		tp_school, tp_researcher, tp_platform, tp_non_prof, tp_company_cust,
		tp_company_notcust, tp_stranger, gender_ord, orientation_ord, race_ord,
		relationship_status_single, multi_platform_ord, aces_compound
	) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
`);

const dfallInsertMany = db.transaction((rows) => {
	for (let i = 0; i < rows.length; i++) {
		const row = rows[i];
		dfallInsertStmt.run(
			row.ID ? parseInt(row.ID) : i,
			parseInt(row.Timepoint || 1),
			row.TP_Social ? parseFloat(row.TP_Social) : null,
			row.TP_Gov ? parseFloat(row.TP_Gov) : null,
			row.TP_Police ? parseFloat(row.TP_Police) : null,
			row.TP_Friend ? parseFloat(row.TP_Friend) : null,
			row.TP_Relative ? parseFloat(row.TP_Relative) : null,
			row.TP_Employer ? parseFloat(row.TP_Employer) : null,
			row.TP_Medical ? parseFloat(row.TP_Medical) : null,
			row.TP_Financial ? parseFloat(row.TP_Financial) : null,
			row.TP_Neighbor ? parseFloat(row.TP_Neighbor) : null,
			row.TP_Acquaintance ? parseFloat(row.TP_Acquaintance) : null,
			row.TP_Co_worker ? parseFloat(row.TP_Co_worker) : null,
			row.TP_School ? parseFloat(row.TP_School) : null,
			row.TP_Researcher ? parseFloat(row.TP_Researcher) : null,
			row.TP_Platform ? parseFloat(row.TP_Platform) : null,
			row.TP_NonProf ? parseFloat(row.TP_NonProf) : null,
			row.TP_Company_cust ? parseFloat(row.TP_Company_cust) : null,
			row.TP_Company_notcust ? parseFloat(row.TP_Company_notcust) : null,
			row.TP_Stranger ? parseFloat(row.TP_Stranger) : null,
			row.Dem_Gender_Woman === '1.0' ? 0 : row.Dem_Gender_Man === '1.0' ? 1 : 2,
			row.Dem_Sexual_Orientation_straight === '1.0' ? 0 :
				row.Dem_Sexual_Orientation_Bisexual === '1.0' ? 1 :
				row.Dem_Sexual_Orientation_Gay === '1.0' ? 2 : 3,
			row.Dem_Race_White === '1.0' ? 0 : row.Dem_Race_Mixed === '1.0' ? 1 : 2,
			row.Dem_Relationship_Status_Single ? parseFloat(row.Dem_Relationship_Status_Single) : null,
			null, // multi_platform_ord not in dfall
			row.ACES_Compound ? parseFloat(row.ACES_Compound) : null
		);
	}
});

try {
	dfallInsertMany(dfallData);
	console.log(`   ✅ Inserted ${dfallData.length} rows successfully`);
} catch (error) {
	console.error('\n   ❌ Error:', error.message);
}

db.close();

console.log('\n✅ Migration completed successfully!');
console.log('\n📊 Summary:');
console.log(`   - trust_circles_individual: ${trustCirclesData.length} rows`);
console.log(`   - survey_data_all: ${dfallData.length} rows`);
