import { registerParquetFile, query } from '$lib/utils/duckdb.js';
import { paperUrl, coauthorUrl } from '../data/loader.js';


// UI State - Controls layout and appearance
export const uiState = $state({
    sidebarCollapsed: false,
    isDarkMode: false
});

export const dashboardState = $state({
    selectedAuthor: 'Jason H. T. Bates',
    selectedCollege: 'College of Engineering and Mathematical Sciences',
    coauthorNodeColor: 'age_diff',
    paperNodeSize: 'cited_by_count',
    ageFilter: null,
    clickedCoauthor: null,
    highlightedCoauthor: null
});

export const data = $state({
    isInitializing: true,
    error: null
});

let tablesRegistered = false;

async function registerTables() {
    if (tablesRegistered) return;
    
    await registerParquetFile(paperUrl, 'paper');
    await registerParquetFile(coauthorUrl, 'coauthor');
    tablesRegistered = true;
}

export async function loadPaperData(authorName) {
    await registerTables();
    const result = await query(`
        SELECT 
        strftime(publication_date::DATE, '%Y-%m-%d') as pub_date, * 
        FROM paper 
        WHERE name = '${authorName}' AND nb_coauthors < 25
        ORDER BY pub_date DESC
        `);

    return result;
}
export async function loadCoauthorData(authorName) {
    await registerTables();
    const result = await query(`
        SELECT 
        strftime(publication_date::DATE, '%Y-%m-%d') as pub_date, 
        * 
        FROM coauthor 
        WHERE name = '${authorName}' AND nb_coauthors < 25
        ORDER BY pub_date DESC
        `);
    return result;
}

async function loadAvailableAuthors() {
    await registerTables();
    
    const result = await query(`
        SELECT DISTINCT 
            name,
            LAST(ego_age) as current_age,
            LAST(publication_year) as last_pub_year
        FROM coauthor 
        WHERE name IS NOT NULL AND ego_age IS NOT NULL
        GROUP BY name
        ORDER BY name
    `);
    
    return result;
}

export async function initializeApp() {
    try {
        data.isInitializing = true;
        data.availableAuthors = await loadAvailableAuthors(); 
        data.error = null;
        data.isInitializing = false;
    } catch (error) {
        console.error('Failed to initialize app:', error);
        data.error = error.message;
        data.isInitializing = false;
    }
}


export async function loadSelectedAuthor() {
    try {
        data.isLoadingAuthor = true;
        data.error = null;
        
        data.paper = await loadPaperData(dashboardState.selectedAuthor);
        data.coauthor = await loadCoauthorData(dashboardState.selectedAuthor);
        
        data.isLoadingAuthor = false;
    } catch (error) {
        data.error = error.message;
        data.isLoadingAuthor = false;
    }
}


// ------------------
// UNIQUE DATA CLASS
// We cannot export derived statement from object, we need a class.
// ------------------

class DerivedData {
    chosen_author = $derived.by(() => {
        if (!data.trainingData) return [];
        return data.trainingData[0]
    })

    authors = $derived(data.availableAuthors || []);

    colleges = $derived.by(() => {
        if (!data.trainingAggData || data.trainingAggData.length === 0) return [];
        return [...new Set(data.trainingAggData
        .map(d => d.college)
        .filter(college => college != null)
        )];
    });

  coauthors = $derived.by(() => {
    if (!data.coauthorData || data.coauthorData.length === 0) return [];
    const coauthors = [...new Set(data.coauthorData.map(c => c.coauth_name).filter(Boolean))];
    return coauthors.sort();
  });
}

// ✅ Export the instance - this should work!
export const unique = new DerivedData();


// ------------------
//
// UI ACTIONS
//
//-------------------

import { breakpoints } from './utils/layout.js';

if (typeof window !== 'undefined') {
    function handleResize() {
        if (window.innerWidth <= breakpoints.mobile) {
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