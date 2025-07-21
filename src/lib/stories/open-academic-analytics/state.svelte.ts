// src/lib/stories/open-academic-analytics/state.svelte.ts
import { registerParquetFile, query } from '$lib/utils/duckdb.js';
import { paperUrl, coauthorUrl, trainingUrl } from './data/loader.js';

// ------------------
//
// APP STATES
//
//-------------------

// UI State - Controls layout and appearance
export const uiState = $state({
    sidebarCollapsed: false,
    isDarkMode: false
});

// Dashboard State - Controls filtering, selection, and visualization settings
export const dashboardState = $state({
    // Author selection
    selectedAuthor: 'Peter Sheridan Dodds',
    selectedCollege: 'College of Engineering and Mathematical Sciences',
    
    // Visualization settings
    coauthorNodeColor: 'age_diff',        // 'age_diff' | 'acquaintance' | 'institutions' | 'shared_institutions'
    paperNodeSize: 'cited_by_count',      // 'cited_by_count' | 'nb_coauthors'
    
    // Filters
    ageFilter: null,                      // [minAge, maxAge] or null
    
    // Interaction state
    clickedCoauthor: null,                // string | null - for highlighting specific coauthor
    highlightedCoauthor: null             // string | null - deprecated, keeping for backward compatibility
});

// Data State - Holds all loaded data
export const dataState = $state({
    // App-level data
    availableAuthors: [],                 // List of all available authors
    availableColleges: [],                // List of all available colleges
    isInitializing: true,                 // Loading state for initial app setup
    
    // Author-specific data
    paperData: [],                        // Papers for selected author
    coauthorData: [],                     // Coauthor relationships for selected author
    trainingData: null,                   // Training data for selected author
    isLoadingAuthor: false,               // Loading state for author-specific data
    
    // Global analytics data
    trainingAggData: null,                // Aggregated training data across all authors
    isLoadingGlobalData: false,           // Loading state for global data
    
    // Error handling
    error: null                           // Error message if something goes wrong
});

// ------------------
//
// DUCKDB QUERIES
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
    
    return result.map(d => d.college);
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

// ------------------
//
// STATE ACTIONS
//
//-------------------

// 1. App Init (once) - Global data everyone needs
export async function initializeApp() {
    try {
        dataState.isInitializing = true;
        dataState.error = null;
        
        dataState.availableAuthors = await loadAvailableAuthors();
        dataState.availableColleges = await loadAvailableColleges();
        dataState.trainingAggData = await trainingAggData();
        
        dataState.isInitializing = false;
    } catch (error) {
        dataState.error = error.message;
        dataState.isInitializing = false;
    }
}

// 2. Author Selection - Specific author data
export async function loadSelectedAuthor() {
    try {
        dataState.isLoadingAuthor = true;
        dataState.error = null;
        
        const [papers, coauthors] = await loadAuthorData(dashboardState.selectedAuthor);
        dataState.paperData = papers;
        dataState.coauthorData = coauthors;
        dataState.trainingData = await trainingData(dashboardState.selectedAuthor);
        
        dataState.isLoadingAuthor = false;
    } catch (error) {
        dataState.error = error.message;
        dataState.isLoadingAuthor = false;
    }
}

// ------------------
//
// UI ACTIONS
//
//-------------------

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

export function toggleSidebar() {
    uiState.sidebarCollapsed = !uiState.sidebarCollapsed;
}

export function resetDashboardFilters() {
    dashboardState.clickedCoauthor = null;
    dashboardState.highlightedCoauthor = null;
    dashboardState.ageFilter = null;
    dashboardState.coauthorNodeColor = 'age_diff';
    dashboardState.paperNodeSize = 'cited_by_count';
}

// Helper action for updating filters
export function setAgeFilter(minAge, maxAge) {
    dashboardState.ageFilter = minAge !== null && maxAge !== null ? [minAge, maxAge] : null;
}

// Helper action for author selection
export function selectAuthor(authorName) {
    if (dashboardState.selectedAuthor !== authorName) {
        dashboardState.selectedAuthor = authorName;
        dashboardState.clickedCoauthor = null;
        dashboardState.highlightedCoauthor = null;
    }
}