import { loadPaperData, loadCoauthorData, loadAvailableAuthors } from '$stories/open-academic-analytics/data.remote.js';

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
    authorAgeFilter: null,
    clickedCoauthor: null,
    filterBigPapers: true,
    highlightedCoauthor: null,
    researchGroupFilter: 'all' // 'all', 'with_group', 'without_group'
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

        data.paper = await loadPaperData({authorName: dashboardState.selectedAuthor, filterBigPapers: dashboardState.filterBigPapers});
        data.coauthor = await loadCoauthorData({authorName: dashboardState.selectedAuthor, filterBigPapers: dashboardState.filterBigPapers});

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

    // Filtered authors based on age and research group filters
    filteredAuthors = $derived.by(() => {
        let authors = this.authors || [];

        // Apply age filter
        if (dashboardState.authorAgeFilter) {
            const [minAge, maxAge] = dashboardState.authorAgeFilter;
            authors = authors.filter(author => {
                const age = author.current_age || 0;
                return age >= minAge && age <= maxAge;
            });
        }

        // Apply research group filter
        if (dashboardState.researchGroupFilter && dashboardState.researchGroupFilter !== 'all') {
            switch (dashboardState.researchGroupFilter) {
                case 'with_group':
                    authors = authors.filter(author => author.has_research_group === true);
                    break;
                case 'without_group':
                    authors = authors.filter(author => author.has_research_group === false);
                    break;
            }
        }

        return authors;
    });

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

// Auto-select author from filtered results - this needs to be called from a component
export function initializeAutoSelection() {
    $effect(() => {
        const filteredAuthors = unique.filteredAuthors;
        const currentAuthor = dashboardState.selectedAuthor;

        // Only auto-select if we have filtered authors and current author is not in the filtered list
        if (filteredAuthors && filteredAuthors.length > 0) {
            const currentAuthorInFiltered = filteredAuthors.some(author => author.ego_display_name === currentAuthor);

            if (!currentAuthorInFiltered) {
                // Select the first author from filtered results
                dashboardState.selectedAuthor = filteredAuthors[0].ego_display_name;
            }
        }
    });
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