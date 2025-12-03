// state.svelte.ts
import * as d3 from "d3";
import { Allotaxonograph } from 'allotaxonometer-ui';

import { getTopBabyNames } from './data.remote.js';
import { createQuery } from '@tanstack/svelte-query'
import { CalendarDate, parseDate } from "@internationalized/date";
import { createUrlState } from '$lib/state/urlParams.svelte.js';

import { parseDataFile } from './utils.ts';

import boys1895 from './data/boys-1895.json';
import boys1968 from './data/boys-1968.json';

// =============================================================================
// UI STATE
// =============================================================================

export const uiState = $state({
    sidebarCollapsed: false,
    isDarkMode: false,
    uploadStatus: '',
    uploadWarnings: [],
    truncationSettings: {
        enabled: true,
        maxRows: 10000,
        warnThreshold: 5000
    }
});

// =============================================================================
// CONSTANTS
// =============================================================================

export const alphas = d3.range(0,18).map(v => +(v/12).toFixed(2)).concat([1, 2, 5, Infinity]);

// =============================================================================
// MAIN ALLOTAXONOGRAPH CLASS
// =============================================================================

export const dataState = $state({
    isLoading: false,
    error: null,
    // Direct period arrays for the sliders
    period1: [1950, 1959],
    period2: [1990, 1999],
    // Simple reactive allotax data
    allotax: {
        sys1: { dat: boys1895 },
        sys2: { dat: boys1968 },
        alpha: 0.58,
        title: ['Boys 1895', 'Boys 1968'],
        isDataReady: true,
        me: undefined,
        rtd: undefined
    }
});

// =============================================================================
// DATA ACTIONS
// =============================================================================

export async function loadBabynamesData() {
    try {
        dataState.isLoading = true;
        dataState.error = null;

        const period1Str = `${dataState.period1[0]},${dataState.period1[1]}`;
        const period2Str = `${dataState.period2[0]},${dataState.period2[1]}`;

        const data = await getTopBabyNames({
            dates: [period1Str, period2Str],
            locations: ["wikidata:Q30"]
        });

        const keys = Object.keys(data);

        // Simple direct update to reactive state - ensure data has the structure Dashboard expects
        dataState.allotax = {
            sys1: { dat: data[keys[0]] },
            sys2: { dat: data[keys[1]] },
            alpha: 0.58,
            title: [`${dataState.period1[0]}-${dataState.period1[1]}`, `${dataState.period2[0]}-${dataState.period2[1]}`],
            isDataReady: true,
            me: undefined,
            rtd: undefined
        };

        dataState.isLoading = false;
    } catch (error) {
        console.error('Failed to load babynames data:', error);
        dataState.error = error.message;
        dataState.isLoading = false;
    }
}

// =============================================================================
// UI ACTIONS
// =============================================================================

export function toggleSidebar() {
    uiState.sidebarCollapsed = !uiState.sidebarCollapsed;
}

// Updated file upload handler that properly updates the allotax data
export async function handleFileUpload(file: File, system: 'sys1' | 'sys2') {
    uiState.uploadStatus = `Loading ${file.name}...`;
    uiState.uploadWarnings = [];
    
    try {
        const result = await parseDataFile(file, {
            enableTruncation: uiState.truncationSettings.enabled,
            maxRows: uiState.truncationSettings.maxRows,
            warnThreshold: uiState.truncationSettings.warnThreshold
        });
        
        if (result.success) {
            // Update the allotaxonograph data directly
            if (system === 'sys1') {
                dataState.allotax.sys1 = { dat: result.data };
                dataState.allotax.title[0] = result.fileName;
            } else {
                dataState.allotax.sys2 = { dat: result.data };
                dataState.allotax.title[1] = result.fileName;
            }
            
            // Set warnings if any
            if (result.warnings && result.warnings.length > 0) {
                uiState.uploadWarnings = result.warnings;
            }
            
            // Create success message with file info
            const fileInfo = result.meta ? 
                ` (${result.meta.processedRows.toLocaleString()} rows, ${result.fileType?.toUpperCase()})` :
                ` (${result.fileType?.toUpperCase()})`;
                
            uiState.uploadStatus = `${system.toUpperCase()}: ${result.fileName} loaded successfully!${fileInfo}`;
            
            // Clear status after delay
            setTimeout(() => {
                uiState.uploadStatus = '';
                if (uiState.uploadWarnings.length === 0) {
                    uiState.uploadWarnings = [];
                }
            }, 3000);
            
            return { success: true, fileName: result.fileName, fileType: result.fileType };
        } else {
            uiState.uploadStatus = `Error loading ${file.name}: ${result.error}`;
            setTimeout(() => uiState.uploadStatus = '', 5000);
            return { success: false, error: result.error };
        }
        
    } catch (error) {
        uiState.uploadStatus = `Error loading ${file.name}: ${error.message}`;
        setTimeout(() => uiState.uploadStatus = '', 5000);
        return { success: false, error: error.message };
    }
}