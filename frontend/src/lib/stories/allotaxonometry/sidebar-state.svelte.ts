// Centralized state for the allotaxonometry sidebar and dashboard
import { getTopBabyNames, getAdapter } from './allotax.remote.js';
import { Allotaxonograph } from 'allotaxonometer-ui';
import { createQuery } from '@tanstack/svelte-query';
import { parseDataFile, calculateShiftedRange } from './utils.ts';

// Alpha values: 0, 1/4, 2/4, 3/4, 1, 3/2, 2, 3, 5, ∞
export const alphas = [0, 1/4, 2/4, 3/4, 1, 3/2, 2, 3, 5, Infinity];

// Centralized state object (Svelte 5 pattern for exportable state)
export const state = $state({
    // UI State
    period1: [1940, 1959],
    period2: [1990, 2009],
    sidebarCollapsed: false,
    jumpYears: 5,
    alphaIndex: 7,
    selectedLocation: 'wikidata:Q30',
    selectedSex: 'M', // 'M' or 'F'
    selectedTopN: 10000,

    // File upload state
    uploadedSys1: null,
    uploadedSys2: null,
    uploadedTitle: ['System 1', 'System 2'],
    uploadStatus: '',
    uploadWarnings: [],

    // Location/adapter state
    adapter: [],
    locationsLoading: true,
    locationsError: false,

    // Fetched parameters (what's currently displayed)
    fetchedPeriod1: [1940, 1959],
    fetchedPeriod2: [1990, 2009],
    fetchedLocation: 'wikidata:Q30',
    fetchedSex: 'M',
    fetchedTopN: 10000,

    // Warning state
    warningDismissed: false,
});

// Derived state class (Svelte 5 pattern)
class DerivedState {
    hasUploadedFiles = $derived(state.uploadedSys1 || state.uploadedSys2);

    currentAlpha = $derived(alphas[state.alphaIndex]);

    locationDateRange = $derived.by(() => {
        if (!state.adapter?.length) return { min: 1880, max: 2020 };
        const location = state.adapter.find(l => l[1] === state.selectedLocation);
        if (location && location[4] && location[5]) {
            return { min: location[4], max: location[5] };
        }
        // Default to US range if not found
        return { min: 1880, max: 2020 };
    });

    dateMin = $derived(this.locationDateRange.min);
    dateMax = $derived(this.locationDateRange.max);
}

export const derived = new DerivedState();

// Functions
export function onAlphaChange(newIndex: number) {
    state.alphaIndex = newIndex;
}

export async function handleFileUpload(file: File, system: 'sys1' | 'sys2') {
    state.uploadStatus = `Loading ${file.name}...`;
    state.uploadWarnings = [];

    try {
        // Use robust parseDataFile from utils.ts
        const result = await parseDataFile(file, {
            enableTruncation: true,
            maxRows: 50000,
            warnThreshold: 50000,
            maxFileSize: 50 * 1024 * 1024 // 50MB
        });

        if (!result.success || !result.data) {
            throw new Error(result.error || 'Failed to parse file');
        }

        // Update state based on system
        if (system === 'sys1') {
            state.uploadedSys1 = result.data;
            state.uploadedTitle[0] = result.fileName || file.name.replace(/\.(json|csv)$/i, '');
        } else {
            state.uploadedSys2 = result.data;
            state.uploadedTitle[1] = result.fileName || file.name.replace(/\.(json|csv)$/i, '');
        }

        // Set warnings if any
        if (result.warnings.length > 0) {
            state.uploadWarnings = result.warnings;
        }

        state.uploadStatus = `${system.toUpperCase()}: ${file.name} loaded successfully!`;
        setTimeout(() => state.uploadStatus = '', 3000);

        // Only trigger data refresh when BOTH files are uploaded
        setTimeout(() => {
            if (state.uploadedSys1 && state.uploadedSys2) {
                state.uploadStatus = 'Both files loaded! Generating visualization...';
                loadData();
            } else {
                state.uploadStatus = `Waiting for ${state.uploadedSys1 ? 'System 2' : 'System 1'} file...`;
            }
        }, 0);

        return { success: true, fileName: file.name };
    } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        state.uploadStatus = `Error loading ${file.name}: ${errorMessage}`;
        setTimeout(() => state.uploadStatus = '', 5000);
        return { success: false, error: errorMessage };
    }
}

export function loadData() {
    state.fetchedPeriod1 = [...state.period1];
    state.fetchedPeriod2 = [...state.period2];
    state.fetchedLocation = state.selectedLocation;
    state.fetchedSex = state.selectedSex;
    state.fetchedTopN = state.selectedTopN;
}

export function shiftBothPeriodsLeft() {
    // Shift both periods backward by jumpYears
    state.period1 = calculateShiftedRange(
        state.period1,
        -state.jumpYears,
        derived.dateMin,
        derived.dateMax
    );

    state.period2 = calculateShiftedRange(
        state.period2,
        -state.jumpYears,
        derived.dateMin,
        derived.dateMax
    );

    // Use setTimeout to ensure state updates before refetching
    setTimeout(() => loadData(), 0);
}

export function shiftBothPeriodsRight() {
    // Shift both periods forward by jumpYears
    state.period1 = calculateShiftedRange(
        state.period1,
        state.jumpYears,
        derived.dateMin,
        derived.dateMax
    );

    state.period2 = calculateShiftedRange(
        state.period2,
        state.jumpYears,
        derived.dateMin,
        derived.dateMax
    );

    // Use setTimeout to ensure state updates before refetching
    setTimeout(() => loadData(), 0);
}

export function canShiftLeft() {
    return state.period1[0] > derived.dateMin || state.period2[0] > derived.dateMin;
}

export function canShiftRight() {
    return state.period1[1] < derived.dateMax || state.period2[1] < derived.dateMax;
}

// Initialize adapter loading
export async function initializeAdapter() {
    try {
        state.adapter = await getAdapter();
        state.locationsLoading = false;
    } catch (error) {
        console.error('Failed to fetch locations:', error);
        state.locationsError = true;
        state.locationsLoading = false;
    }
}

// Query factory - create the query in the component that needs it
export function createBabyNamesQuery() {
    return createQuery(() => ({
        queryKey: ['babynames', state.fetchedPeriod1[0], state.fetchedPeriod1[1], state.fetchedPeriod2[0], state.fetchedPeriod2[1], state.fetchedLocation, state.fetchedSex, state.fetchedTopN, derived.hasUploadedFiles, !!state.uploadedSys1, !!state.uploadedSys2, JSON.stringify(state.uploadedTitle)],
        queryFn: async () => {
            if (derived.hasUploadedFiles) {
                const elem1 = state.uploadedSys1 || [];
                const elem2 = state.uploadedSys2 || [];
                return {
                    elem1,
                    elem2,
                    title: state.uploadedTitle
                };
            }

            const period1Str = `${state.fetchedPeriod1[0]},${state.fetchedPeriod1[1]}`;
            const period2Str = `${state.fetchedPeriod2[0]},${state.fetchedPeriod2[1]}`;

            const ngrams = await getTopBabyNames({
                dates: period1Str,
                dates2: period2Str,
                location: state.fetchedLocation,
                sex: state.fetchedSex,
                limit: state.fetchedTopN
            });

            const keys = Object.keys(ngrams);
            const elem1 = ngrams[keys[0]];
            const elem2 = ngrams[keys[1]];

            return {
                elem1,
                elem2,
                title: [`${state.fetchedPeriod1[0]}-${state.fetchedPeriod1[1]}`, `${state.fetchedPeriod2[0]}-${state.fetchedPeriod2[1]}`]
            };
        },
        enabled: true,
        staleTime: 5 * 60 * 1000, // 5 minutes
        gcTime: 10 * 60 * 1000, // 10 minutes
        placeholderData: (previousData) => previousData,
    }));
}

// Derived data from query - to be used in components
export function getInstanceFromQuery(queryData: any) {
    return queryData
        ? new Allotaxonograph(queryData.elem1, queryData.elem2, {
            alpha: derived.currentAlpha,
            title: queryData.title
        })
        : null;
}

export function getActualCounts(queryData: any) {
    if (!queryData) return null;
    const count1 = queryData.elem1?.length || 0;
    const count2 = queryData.elem2?.length || 0;
    return { period1: count1, period2: count2 };
}

export function shouldShowTopNWarning(queryData: any, isDataReady: boolean) {
    const counts = getActualCounts(queryData);
    if (!counts || !isDataReady) return false;
    return counts.period1 < state.fetchedTopN || counts.period2 < state.fetchedTopN;
}
