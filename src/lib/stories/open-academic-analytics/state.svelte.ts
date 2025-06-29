// src/lib/stories/open-academic-analytics/state.svelte.ts
import { registerParquetFile, query } from '$lib/utils/duckdb.js';
import { paperUrl, coauthorUrl } from './data/loader.js';

// UI State
export const uiState = $state({
    sidebarCollapsed: false,
    isDarkMode: false
});

// Dashboard State
export const dashboardState = $state({
    colorMode: 'age_diff',
    highlightedAuthor: null,
    highlightedCoauthor: null,
    selectedAuthor: 'Peter Sheridan Dodds'
});

// Data State
export const dataState = $state({
    paperData: [],
    coauthorData: [],
    availableAuthors: [],
    isInitializing: true,
    isLoadingAuthor: false,
    error: null
});

// Tables registration state
let tablesRegistered = false;

// Register parquet tables once
async function registerTables() {
    if (tablesRegistered) return;
    
    await registerParquetFile(paperUrl, 'paper');
    await registerParquetFile(coauthorUrl, 'coauthor');
    tablesRegistered = true;
}

// Load available authors
async function loadAvailableAuthors() {
    await registerTables();
    
    const result = await query(`
        SELECT DISTINCT name 
        FROM coauthor 
        WHERE name IS NOT NULL 
        ORDER BY name
        LIMIT 50
    `);
    
    return result.map(row => row.name);
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
                age_bucket
            FROM coauthor 
            WHERE name = '${authorName}'
            ORDER BY pub_year
        `)
    ]);
    
    return [paperData, coauthorData];
}

// Initialize app - load author list
export async function initializeApp() {
    try {
        dataState.isInitializing = true;
        dataState.error = null;
        
        const authors = await loadAvailableAuthors();
        dataState.availableAuthors = authors;
        dataState.isInitializing = false;
        
        console.log(`📋 Loaded ${authors.length} available authors`);
        
    } catch (error) {
        dataState.error = error.message;
        dataState.isInitializing = false;
        console.error('Failed to initialize app:', error);
    }
}

// Load data for selected author
export async function loadSelectedAuthor() {
    if (!dashboardState.selectedAuthor) return;
    
    try {
        dataState.isLoadingAuthor = true;
        
        const [paperData, coauthorData] = await loadAuthorData(dashboardState.selectedAuthor);
        
        dataState.paperData = paperData;
        dataState.coauthorData = coauthorData;
        dataState.isLoadingAuthor = false;
        
        console.log(`📊 Loaded ${paperData.length} papers and ${coauthorData.length} coauthor records for ${dashboardState.selectedAuthor}`);
        
    } catch (error) {
        dataState.isLoadingAuthor = false;
        console.error('Failed to load author data:', error);
    }
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
    dashboardState.highlightedCoauthor = null;
    dashboardState.colorMode = 'age_diff';
}

export function setSelectedAuthor(authorName) {
    dashboardState.selectedAuthor = authorName;
}