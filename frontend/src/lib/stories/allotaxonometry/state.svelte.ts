// state.svelte.ts
import * as d3 from "d3";
import { Allotaxonograph } from 'allotaxonometer-ui';
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

export const allotax = new Allotaxonograph(
    boys1895, 
    boys1968, 
    0.58, 
    ['Boys 1895', 'Boys 1968']
);

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
                allotax.sys1 = result.data;
                allotax.title[0] = result.fileName;
            } else {
                allotax.sys2 = result.data;
                allotax.title[1] = result.fileName;
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