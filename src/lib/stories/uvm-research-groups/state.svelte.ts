// src/lib/stories/open-academic-analytics/state.svelte.ts
import { registerParquetFile, query } from '$lib/utils/duckdb.js';
import { departmentURL, trainingUrl } from './data/loader.js';

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
    tablesRegistered = true;
}

export async function trainingAggData(authorName) {
    await registerTables();
    const result = await query(`
        SELECT 
            DISTINCT t.payroll_name as name, t.has_research_group, 
            t.host_dept, t.perceived_as_male, t.group_url, t.group_size,
            d.college
        FROM training t
        LEFT JOIN 
            department d ON t.host_dept = d.department
        ORDER BY has_research_group
        `);
    return result;
}

// App Init (once) - Global data everyone needs
export async function initializeApp() {
        dataState.isInitializing = true;
        dataState.trainingAggData = await trainingAggData();
        dataState.isInitializing = false;
}
