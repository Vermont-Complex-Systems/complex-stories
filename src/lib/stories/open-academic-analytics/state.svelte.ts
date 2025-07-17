// src/lib/stories/open-academic-analytics/state.svelte.ts
import { registerParquetFile, query } from '$lib/utils/duckdb.js';
import { paperUrl, coauthorUrl, trainingUrl } from './data/loader.js';

// ------------------
//
// APP STATES
//
//-------------------


// UI State
export const uiState = $state({
    sidebarCollapsed: false,
    isDarkMode: false
});

// Filters, both sidebar and chart specific
export const dashboardState = $state({
    selectedAuthor: 'Peter Sheridan Dodds',
    colorMode: 'age_diff',
    highlightedAuthor: null,
    authorAgeFilter: null, // [minAge, maxAge] or null
    highlightedCoauthor: null,
    selectedCollege: 'College of Engineering and Mathematical Sciences'
});

// Data State: the data we load
export const dataState = $state({
    // App-level
    availableAuthors: [],
    availableColleges: [],
    isInitializing: true,
    
    // Author-specific  
    paperData: [],
    coauthorData: [],
    trainingData: null,
    isLoadingAuthor: false,
    
    // Global analytics
    TrainingAggData: null,
    isLoadingGlobalData: false,
    
    error: null
});


// ------------------
//
// DUCKDB
//
//-------------------

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


export async function trainingData(authorName) {
    await registerTables();
    const result = await query(`
        SELECT * 
        FROM training 
        WHERE name = '${authorName}'`);
    return result;
}

export async function trainingAggData() {
    await registerTables();
    const result = await query(`
        SELECT 
            AVG(younger) as younger, 
            QUANTILE_CONT(younger, 0.5) as median_collabs,
            QUANTILE_CONT(younger, 0.25) as q25_collabs,
            QUANTILE_CONT(younger, 0.75) as q75_collabs,
            STDDEV(younger) as std_collabs,
            author_age, has_research_group, college 
        FROM training 
        GROUP BY has_research_group, author_age, college
        ORDER BY has_research_group, author_age, college
        `);
    return result;
}

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

async function loadAvailableColleges() {
    await registerTables();
    
    const result = await query(`
        SELECT DISTINCT college FROM training 
        WHERE college IS NOT NULL
    `);
    
    return result.map(d=>d.college);
}

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
        dataState.availableColleges = await loadAvailableColleges();
        dataState.trainingAggData = await trainingAggData();
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
