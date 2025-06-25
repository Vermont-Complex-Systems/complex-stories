import * as d3 from "d3";
import { combElems, rank_turbulence_divergence, diamond_count, wordShift_dat, balanceDat } from 'allotaxonometer-ui';

// Import default data
import boys1895 from '../data/boys-1895.json';
import boys1968 from '../data/boys-1968.json';

// =============================================================================
// UI STATE AND CONSTANTS
// =============================================================================

export const uiState = $state({
    sidebarCollapsed: false,
    isDarkMode: false,
    uploadStatus: '',
    title: ['Boys 1895', 'Boys 1968']
});

export const alphaState = $state({
    alphaIndex: 7
});

export const alphas = d3.range(0,18).map(v => +(v/12).toFixed(2)).concat([1, 2, 5, Infinity]);

// =============================================================================
// REACTIVE DATA PROCESSING CLASS
// =============================================================================

export class AllotaxonometerData {
    // Reactive input state
    sys1 = $state(boys1895);
    sys2 = $state(boys1968);
    
    // Derived alpha value from global alphaState
    alpha = $derived(alphas[alphaState.alphaIndex]);
    
    // Reactive data pipeline
    me = $derived(this.sys1 && this.sys2 ? combElems(this.sys1, this.sys2) : null);
    rtd = $derived(this.me ? rank_turbulence_divergence(this.me, this.alpha) : null);
    dat = $derived(this.me && this.rtd ? diamond_count(this.me, this.rtd) : null);
    
    // Derived data for components
    barData = $derived(this.me && this.dat ? wordShift_dat(this.me, this.dat).slice(0, 30) : []);
    balanceData = $derived(this.sys1 && this.sys2 ? balanceDat(this.sys1, this.sys2) : []);
    
    // Computed metrics
    maxlog10 = $derived(this.me ? Math.ceil(d3.max([
        Math.log10(d3.max(this.me[0].ranks)), 
        Math.log10(d3.max(this.me[1].ranks))
    ])) : 0);
    
    max_count_log = $derived(this.dat ? Math.ceil(Math.log10(d3.max(this.dat.counts, d => d.value))) + 1 : 2);
    max_shift = $derived(this.barData.length > 0 ? d3.max(this.barData, d => Math.abs(d.metric)) : 1);
    isDataReady = $derived(this.dat && this.barData && this.balanceData && this.me && this.rtd);
}

// =============================================================================
// SINGLETON DATA INSTANCE
// =============================================================================

export const dataProcessor = new AllotaxonometerData();

// =============================================================================
// ACTIONS
// =============================================================================

export function toggleSidebar() {
    uiState.sidebarCollapsed = !uiState.sidebarCollapsed;
}

export async function handleFileUpload(file, system) {
    try {
        uiState.uploadStatus = `Loading ${system}...`;
        const text = await file.text();
        const data = JSON.parse(text);
        
        if (system === 'sys1') {
            dataProcessor.sys1 = data;
            uiState.title[0] = file.name.replace('.json', '');
        } else {
            dataProcessor.sys2 = data;
            uiState.title[1] = file.name.replace('.json', '');
        }
        
        uiState.uploadStatus = `${system.toUpperCase()} loaded successfully!`;
        setTimeout(() => uiState.uploadStatus = '', 3000);
    } catch (error) {
        uiState.uploadStatus = `Error loading ${system}: ${error.message}`;
        setTimeout(() => uiState.uploadStatus = '', 5000);
    }
}