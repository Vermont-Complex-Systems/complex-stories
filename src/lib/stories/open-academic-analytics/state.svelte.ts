// src/lib/stories/open-academic-analytics/state.svelte.ts
import { registerParquetFile, query } from '$lib/utils/duckdb.js';
import { paperUrl, coauthorUrl } from './data/loader.js';

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
    paperData: [],
    coauthorData: [],
    availableAuthors: [],
    availableCoauthors: [],
    isInitializing: true,
    isLoadingAuthor: false,
    error: null
});

// Tables registration state
let tablesRegistered = false;

export function getAvailableCoauthors() {
  if (!dataState.coauthorData || dataState.coauthorData.length === 0) {
    return [];
  }
  
  // Get unique coauthor names from the current dataset
  const uniqueNames = [...new Set(dataState.coauthorData.map(d => d.coauth_name))];
  return uniqueNames.sort();
}

// Register parquet tables once
async function registerTables() {
    if (tablesRegistered) return;
    
    await registerParquetFile(paperUrl, 'paper');
    await registerParquetFile(coauthorUrl, 'coauthor');
    tablesRegistered = true;
}

// Load available authors WITH age data
async function loadAvailableAuthors() {
    await registerTables();
    
    // Get authors with their most recent age data
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
                age_bucket
            FROM coauthor 
            WHERE name = '${authorName}'
            ORDER BY pub_year
        `)
    ]);
    
    return [paperData, coauthorData];
}

export async function initializeApp() {
    try {
        dataState.isInitializing = true;
        dataState.error = null;
        
        const authorsWithAges = await loadAvailableAuthors();
        dataState.availableAuthors = authorsWithAges;
        dataState.isInitializing = false;
        
        console.log(`📋 Loaded ${authorsWithAges.length} available authors with age data`);
        
    } catch (error) {
        dataState.error = error.message;
        dataState.isInitializing = false;
        console.error('Failed to initialize app:', error);
    }
}

// Load data for selected author
export async function loadSelectedAuthor() {
    if (!dashboardState.selectedAuthor) return;
    
    dataState.isLoadingAuthor = true;
    dataState.error = null; // Clear any previous errors
    
    try {
        const [paperData, coauthorData] = await loadAuthorData(dashboardState.selectedAuthor);
        
        dataState.paperData = paperData;
        dataState.coauthorData = coauthorData;
        
        // Update available coauthors after setting the data
        dataState.availableCoauthors = getAvailableCoauthors();
        
        // Reset highlighted coauthor if it's not in the new dataset
        if (dashboardState.highlightedCoauthor && 
            !dataState.availableCoauthors.includes(dashboardState.highlightedCoauthor)) {
            dashboardState.highlightedCoauthor = null;
        }
        
        console.log(`📊 Loaded ${paperData.length} papers and ${coauthorData.length} coauthor records for ${dashboardState.selectedAuthor}`);
        console.log(`👥 Available coauthors: ${dataState.availableCoauthors.length}`);
        
    } catch (error) {
        dataState.error = error.message || 'Failed to load author data';
        dataState.paperData = [];
        dataState.coauthorData = [];
        dataState.availableCoauthors = [];
        console.error('Failed to load author data:', error);
    } finally {
        dataState.isLoadingAuthor = false;
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
    dashboardState.authorAgeFilter = null;
    dashboardState.colorMode = 'age_diff';
}

export function setSelectedAuthor(authorName) {
    dashboardState.selectedAuthor = authorName;
}