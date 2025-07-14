// src/lib/stories/open-academic-analytics/state.svelte.ts
import { registerParquetFile, query } from '$lib/utils/duckdb.js';
import { paperUrl, coauthorUrl, trainingUrl } from './data/loader.js';

// UI State
export const uiState = $state({
    sidebarCollapsed: false,
    isDarkMode: false
});

export const dashboardState = $state({
    selectedAuthor: 'Peter Sheridan Dodds',
    colorMode: 'age_diff',
    highlightedAuthor: null,
    authorAgeFilter: null, // [minAge, maxAge] or null
    highlightedCoauthor: null,
});

// Data State
export const dataState = $state({
    // App-level
    availableAuthors: [],
    isInitializing: true,
    
    // Author-specific  
    paperData: [],
    coauthorData: [],
    trainingData: null,
    isLoadingAuthor: false,
    
    // Global analytics
    AggData: null,
    isLoadingGlobalData: false,
    
    error: null
});

// Derived state
export const derivedData = {
    get availableCoauthors() {
        if (!dataState.coauthorData?.length) return [];
        return [...new Set(dataState.coauthorData.map(d => d.coauth_name).filter(Boolean))].sort();
    }
};

// Tables registration state
let tablesRegistered = false;

// Register parquet tables once
async function registerTables() {
    if (tablesRegistered) return;
    
    await registerParquetFile(paperUrl, 'paper');
    await registerParquetFile(coauthorUrl, 'coauthor');
    await registerParquetFile(trainingUrl, 'training');
    tablesRegistered = true;
}

// Simple aggData function
export async function aggData() {
    await registerTables();
    const result = await query(`
        WITH tmp AS (
            SELECT 
                COUNT(*) as collaboration_count, 
                age_category, 
                substr(strftime(age_std::DATE, '%Y'), -2) as year_short,
                name
            FROM coauthor 
            GROUP BY age_category, substr(strftime(age_std::DATE, '%Y'), -2), name
        )
        SELECT 
            AVG(collaboration_count) as mean_collabs,
            QUANTILE_CONT(collaboration_count, 0.5) as median_collabs,
            STDDEV(collaboration_count) as std_collabs,
            age_category, 
            year_short::INT as age_std
        FROM tmp    
        GROUP BY age_category, age_std
        ORDER BY age_category, age_std
        `);
    return result;
}

// model output
export async function trainingData(authorName) {
    await registerTables();
    const result = await query(`SELECT * FROM training WHERE name = '${authorName}'`);
    return result;
}

// Load available authors
async function loadAvailableAuthors() {
    await registerTables();
    
    const result = await query(`
        SELECT DISTINCT 
            name,
            LAST(author_age) as current_age,
            LAST(pub_year) as last_pub_year
        FROM coauthor 
        WHERE name IS NOT NULL AND author_age IS NOT NULL
        GROUP BY name
        ORDER BY name
    `);
    
    return result;
}

// Load data for specific author
async function loadAuthorData(authorName) {
    await registerTables();
    
    const [paperData, coauthorData] = await Promise.all([
        query(`
            SELECT 
                ego_aid,
                name,
                strftime(pub_date::DATE, '%Y-%m-%d') as pub_date,
                pub_year,
                title,
                cited_by_count,
                doi,
                wid,
                authors,
                work_type,
                ego_age,
                nb_coauthors
            FROM paper 
            WHERE name = '${authorName}'
            ORDER BY pub_year
        `),
        
        query(`
            SELECT 
                strftime(age_std::DATE, '%Y-%m-%d') as age_std,
                strftime(pub_date::DATE, '%Y-%m-%d') as pub_date,
                pub_year,
                aid,
                institution,
                name,
                author_age,
                first_pub_year,
                last_pub_year,
                yearly_collabo,
                all_times_collabo,
                acquaintance,
                shared_institutions,
                coauth_aid,
                coauth_name,
                coauth_age,
                coauth_min_year,
                age_diff,
                age_category,
                collaboration_intensity,
                institution_normalized,
                coauth_institution_normalized,
                shared_institutions_normalized
            FROM coauthor 
            WHERE name = '${authorName}'
            ORDER BY pub_year
        `)
    ]);
    
    return [paperData, coauthorData];
}

// 1. App Init (once) - Global data everyone needs
export async function initializeApp() {
        dataState.isInitializing = true;
        dataState.availableAuthors = await loadAvailableAuthors();
        dataState.AggData = await aggData();
        dataState.isInitializing = false;
}

// 2. Author Selection - Specific author data
export async function loadSelectedAuthor() {
    dataState.isLoadingAuthor = true;
    const [papers, coauthors] = await loadAuthorData(dashboardState.selectedAuthor);
    dataState.paperData = papers;
    dataState.coauthorData = coauthors;
    dataState.trainingData = await trainingData(dashboardState.selectedAuthor);
    dataState.isLoadingAuthor = false;
}

// Auto-collapse sidebar on mobile
if (typeof window !== 'undefined') {
    function handleResize() {
        if (window.innerWidth <= 768) {
            uiState.sidebarCollapsed = true;
        } else {
            uiState.sidebarCollapsed = false;
        }
    }
    
    handleResize();
    window.addEventListener('resize', handleResize);
}

// UI Actions
export function toggleSidebar() {
    uiState.sidebarCollapsed = !uiState.sidebarCollapsed;
}

export function resetDashboardFilters() {
    dashboardState.highlightedAuthor = null;
    dashboardState.authorAgeFilter = null;
    dashboardState.colorMode = 'age_diff';
}

export function setSelectedAuthor(authorName) {
    dashboardState.selectedAuthor = authorName;
}