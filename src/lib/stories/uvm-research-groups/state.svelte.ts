// src/lib/stories/open-academic-analytics/state.svelte.ts
import { registerParquetFile, query } from '$lib/utils/duckdb.js';
import { coauthorURL, departmentURL, paperURL, trainingUrl, uvmProfsURL } from './data/loader.js';

export const dashboardState = $state({
    selectedAuthor: 'Peter Sheridan Dodds',
    colorMode: 'age_diff',
    highlightedAuthor: null,
    authorAgeFilter: null, // [minAge, maxAge] or null
    highlightedCoauthor: null,
});

export const dataState = $state({
    isInitializing: true,
    trainingAggData: null,
    isLoadingGlobalData: false,
    error: null
});

let tablesRegistered = false;

// Register parquet tables once
async function registerTables() {
    if (tablesRegistered) return;
    
    await registerParquetFile(trainingUrl, 'training');
    await registerParquetFile(departmentURL, 'department');
    await registerParquetFile(paperURL, 'paper');
    await registerParquetFile(coauthorURL, 'coauthor');
    await registerParquetFile(uvmProfsURL, 'uvm_profs_2023');
    tablesRegistered = true;
}

export async function DoddsPaperData(authorName) {
    await registerTables();
    const result = await query(`
        SELECT *, strftime(pub_date::DATE, '%Y-%m-%d') as pub_date 
        FROM paper
        WHERE ego_aid = 'A5040821463'`);
    return result;
}

export async function DoddsCoauthorData(authorName) {
    await registerTables();
    const result = await query(`
        SELECT *, strftime(pub_date::DATE, '%Y-%m-%d') as pub_date 
        FROM coauthor
        WHERE aid = 'A5040821463'
        `);
    return result;
}

export async function EmbeddingsData() {
    await registerTables();
    const result = await query(`
        WITH exploded_depts AS (
            SELECT 
                DISTINCT t.name,
                t.aid as oa_uid,
                t.has_research_group,
                trim(unnest(string_split(t.host_dept, ';'))) as host_dept,
                t.perceived_as_male,
                t.college,
                t.group_url,
                t.group_size
            FROM training t
            WHERE oa_uid IS NOT NULL
        )
        SELECT DISTINCT doi, *, strftime(pub_date::DATE, '%Y-%m-%d') as pub_date, e.host_dept, e.college
        FROM paper p
        LEFT JOIN exploded_depts e ON p.ego_aid = e.oa_uid
        WHERE p.umap_1 IS NOT NULL
        ORDER BY 
            CASE WHEN ego_aid = 'A5040821463' THEN 1 ELSE 0 END,  -- Peter's papers last
            pub_date  -- Then by date within each group
        `);
    return result;
}
// export async function EmbeddingsData() {
//     await registerTables();
//     const result = await query(`
//         SELECT *, strftime(pub_date::DATE, '%Y-%m-%d') as pub_date 
//         FROM (
//             -- Keep ALL papers from ego author
//             SELECT * FROM paper WHERE ego_aid = 'A5040821463'
            
//             UNION ALL
            
//             -- 10% sample from other distinct DOIs
//             SELECT * FROM (
//                 SELECT DISTINCT ON (doi) *
//                 FROM paper 
//                 WHERE ego_aid != 'A5040821463' 
//                 AND doi IS NOT NULL 
//                 AND umap_1 IS NOT NULL
//                 AND doi != ''
//                 ORDER BY doi, RANDOM()
//             )
//             TABLESAMPLE BERNOULLI(90 PERCENT)  -- 50% sample
//         )
//         ORDER BY 
//             CASE WHEN ego_aid = 'A5040821463' THEN 1 ELSE 0 END,  -- Peter's papers last
//             pub_date  -- Then by date within each group
//         `);
//     return result;
// }

export async function trainingAggData(authorName) {
    await registerTables();
    const result = await query(`
       WITH exploded_depts AS (
            SELECT 
                t.payroll_name as name,
                t.has_research_group,
                trim(unnest(string_split(t.host_dept, ';'))) as host_dept,
                t.perceived_as_male,
                t.group_url,
                t.group_size
            FROM uvm_profs_2023 t
        )
        SELECT DISTINCT 
            e.name,
            e.has_research_group,
            e.host_dept,
            e.perceived_as_male,
            e.group_url,
            e.group_size,
            d.college
        FROM exploded_depts e
        LEFT JOIN department d ON e.host_dept = d.department
        ORDER BY has_research_group
        `);
    return result;
}

// App Init (once) - Global data everyone needs
export async function initializeApp() {
        dataState.isInitializing = true;
        dataState.trainingAggData = await trainingAggData();
        dataState.DoddsPaperData = await DoddsPaperData();
        dataState.EmbeddingsData = await EmbeddingsData();
        dataState.DoddsCoauthorData = await DoddsCoauthorData();
        dataState.isInitializing = false;
}
