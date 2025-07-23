import { registerParquetFile, query } from '$lib/utils/duckdb.js';
import { paperUrl } from '../data/loader.js';

export const data = $state({
    isInitializing: true,
    error: null,
    paperData: []
});

let tablesRegistered = false;

async function registerTables() {
    if (tablesRegistered) return;
    
    await registerParquetFile(paperUrl, 'paper');
    tablesRegistered = true;
}

export async function loadPaperData() {
    await registerTables();
    const result = await query(`
        SELECT 
        strftime(publication_date::DATE, '%Y-%m-%d') as pub_date, * 
        FROM paper 
        WHERE 
            professor_oa_uid = 'https://openalex.org/A5014570718' 
            AND publication_year > 1983
            AND doi IS NOT NULL
            AND work_type IN ('article', 'preprint', 'book-chapter', 'book', 'report')
        ORDER BY publication_date DESC
        `);
    return result;
}

export async function initializeApp() {
    try {
        data.isInitializing = true;
        data.error = null;
        data.paper = await loadPaperData();
        data.isInitializing = false;
    } catch (error) {
        console.error('Failed to initialize app:', error);
        data.error = error.message;
        data.isInitializing = false;
    }
}