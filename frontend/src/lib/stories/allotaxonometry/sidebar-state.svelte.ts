/**
 * Allotaxonometry State Module
 *
 * This module organizes state by functional concern using Svelte 5 reactive classes.
 * Each class groups related state, derived values, and methods together.
 *
 * Structure:
 * - FileState: File upload handling and validation
 * - DashboardState: Dashboard controls (time periods, alpha, location, filtering, UI)
 */
import { getAdapter } from './allotax.remote.js';
import { parseDataFile, calculateShiftedRange } from './utils.ts';

// Alpha values: 0, 1/4, 2/4, 3/4, 1, 3/2, 2, 3, 5, ∞
export const alphas = [0, 1/4, 2/4, 3/4, 1, 3/2, 2, 3, 5, Infinity];

// =============================================================================
// FILE UPLOAD STATE & LOGIC
// =============================================================================
class FileState {
    uploadedSys1 = $state(null);
    uploadedSys2 = $state(null);
    uploadedTitle = $state(['System 1', 'System 2']);
    uploadStatus = $state('');
    uploadWarnings = $state([]);

    // Derived state co-located with the state it depends on
    hasUploadedFiles = $derived(this.uploadedSys1 || this.uploadedSys2);

    async handleFileUpload(file: File, system: 'sys1' | 'sys2') {
        this.uploadStatus = `Loading ${file.name}...`;
        this.uploadWarnings = [];

        try {
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
                this.uploadedSys1 = result.data;
                this.uploadedTitle = [
                    result.fileName || file.name.replace(/\.(json|csv)$/i, ''),
                    this.uploadedTitle[1]
                ];
            } else {
                this.uploadedSys2 = result.data;
                this.uploadedTitle = [
                    this.uploadedTitle[0],
                    result.fileName || file.name.replace(/\.(json|csv)$/i, '')
                ];
            }

            // Set warnings if any
            if (result.warnings.length > 0) {
                this.uploadWarnings = result.warnings;
            }

            this.uploadStatus = `${system.toUpperCase()}: ${file.name} loaded successfully!`;
            setTimeout(() => this.uploadStatus = '', 3000);

            // Only trigger data refresh when BOTH files are uploaded
            setTimeout(() => {
                if (this.uploadedSys1 && this.uploadedSys2) {
                    this.uploadStatus = 'Both files loaded! Generating visualization...';
                    dashboardState.loadData();
                } else {
                    this.uploadStatus = `Waiting for ${this.uploadedSys1 ? 'System 2' : 'System 1'} file...`;
                }
            }, 0);

            return { success: true, fileName: file.name };
        } catch (error: unknown) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            this.uploadStatus = `Error loading ${file.name}: ${errorMessage}`;
            setTimeout(() => this.uploadStatus = '', 5000);
            return { success: false, error: errorMessage };
        }
    }
}

export const fileState = new FileState();

// =============================================================================
// DASHBOARD CONTROLS STATE & LOGIC
// =============================================================================
class DashboardState {
    // Time periods
    period1 = $state([1940, 1959]);
    period2 = $state([1990, 2009]);
    jumpYears = $state(5);

    // Alpha parameter
    alphaIndex = $state(7);

    // Data filtering
    selectedLocation = $state('wikidata:Q30');
    selectedSex = $state('M');
    selectedTopN = $state(10000);

    // Location adapter data
    adapter = $state([]);
    locationsLoading = $state(true);
    locationsError = $state(false);

    // UI state
    sidebarCollapsed = $state(false);
    warningDismissed = $state(false);

    // What's currently fetched/displayed
    fetchedPeriod1 = $state([1940, 1959]);
    fetchedPeriod2 = $state([1990, 2009]);
    fetchedLocation = $state('wikidata:Q30');
    fetchedSex = $state('M');
    fetchedTopN = $state(10000);

    // Derived current alpha value
    currentAlpha = $derived(alphas[this.alphaIndex]);

    // Derived date range based on selected location
    dateRange = $derived.by(() => {
        if (!this.adapter?.length) return { min: 1880, max: 2020 };
        const location = this.adapter.find(l => l[1] === this.selectedLocation);
        if (location && location[4] && location[5]) {
            return { min: location[4], max: location[5] };
        }
        return { min: 1880, max: 2020 };
    });

    dateMin = $derived(this.dateRange.min);
    dateMax = $derived(this.dateRange.max);

    async initializeAdapter() {
        try {
            this.adapter = await getAdapter();
            this.locationsLoading = false;
        } catch (error) {
            console.error('Failed to fetch locations:', error);
            this.locationsError = true;
            this.locationsLoading = false;
        }
    }

    loadData() {
        this.fetchedPeriod1 = [...this.period1];
        this.fetchedPeriod2 = [...this.period2];
        this.fetchedLocation = this.selectedLocation;
        this.fetchedSex = this.selectedSex;
        this.fetchedTopN = this.selectedTopN;
    }

    shiftBothPeriodsLeft() {
        this.period1 = calculateShiftedRange(
            this.period1,
            -this.jumpYears,
            this.dateMin,
            this.dateMax
        );

        this.period2 = calculateShiftedRange(
            this.period2,
            -this.jumpYears,
            this.dateMin,
            this.dateMax
        );

        setTimeout(() => this.loadData(), 0);
    }

    shiftBothPeriodsRight() {
        this.period1 = calculateShiftedRange(
            this.period1,
            this.jumpYears,
            this.dateMin,
            this.dateMax
        );

        this.period2 = calculateShiftedRange(
            this.period2,
            this.jumpYears,
            this.dateMin,
            this.dateMax
        );

        setTimeout(() => this.loadData(), 0);
    }

    canShiftLeft() {
        return this.period1[0] > this.dateMin || this.period2[0] > this.dateMin;
    }

    canShiftRight() {
        return this.period1[1] < this.dateMax || this.period2[1] < this.dateMax;
    }
}

export const dashboardState = new DashboardState();
