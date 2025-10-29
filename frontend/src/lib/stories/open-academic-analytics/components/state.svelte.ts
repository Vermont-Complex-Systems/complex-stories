import { loadPaperData, loadCoauthorData, loadAvailableAuthors } from '../api/data.remote.js';

// UI State - Controls layout and appearance
export const uiState = $state({
    sidebarCollapsed: false,
    isDarkMode: false,
    debug: false
});

export const dashboardState = $state({
    selectedAuthor: 'Peter Sheridan Dodds',
    selectedCollege: 'College of Engineering and Mathematical Sciences',
    coauthorNodeColor: 'age_diff',
    paperNodeSize: 'cited_by_count',
    ageFilter: null,
    clickedCoauthor: null,
    filterBigPapers: true,
    highlightedCoauthor: null
});

export const data = $state({
    isInitializing: true,
    isLoadingAuthor: false,
    error: null,
    paper: null,
    coauthor: null,
    availableAuthors: null
});



export async function initializeApp() {
    try {
        data.isInitializing = true;
        const result = await loadAvailableAuthors();
        data.availableAuthors = result.authors;
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

        const paperResult = await loadPaperData({authorName: dashboardState.selectedAuthor, filterBigPapers: dashboardState.filterBigPapers});
        const coauthorResult = await loadCoauthorData({authorName: dashboardState.selectedAuthor, filterBigPapers: dashboardState.filterBigPapers});

        data.paper = paperResult.papers;
        data.coauthor = coauthorResult.coauthors;

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
        if (!data.coauthor) return [];
        return data.coauthor.filter(d=>d.ego_display_name == dashboardState.selectedAuthor)[0]
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
    if (!data.coauthor || data.coauthor.length === 0) return [];
    const coauthors = [...new Set(data.coauthor.map(c => c.coauthor_display_name).filter(Boolean))];
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
import { filter } from 'svelteplot';

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