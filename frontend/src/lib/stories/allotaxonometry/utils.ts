// utils.ts
import * as d3 from 'd3';

// =============================================================================
// TYPES
// =============================================================================

export interface DataItem {
    types: string;
    counts: number;
    probs: number;
    totalunique: number;
}

export interface ParseSettings {
    enableTruncation?: boolean;
    maxRows?: number;
    warnThreshold?: number;
    maxFileSize?: number;
}

export interface ProcessingMeta {
    totalRows: number;
    processedRows: number;
    skippedRows: number;
    wasTruncated: boolean;
    truncatedAt: number | null;
    wasRecalculated: boolean;
    originalTotalCounts?: number;
    newTotalCounts?: number;
    coveragePercent?: string;
}

export interface ParseResult {
    success: boolean;
    data: DataItem[] | null;
    fileName: string | null;
    fileType: string | null;
    meta: ProcessingMeta | null;
    warnings: string[];
    error: string | null;
}

interface RecalculationResult {
    data: DataItem[];
    originalTotal: number;
    newTotal: number;
    originalTotalCounts: number;
    newTotalCounts: number;
}

// =============================================================================
// CONSTANTS
// =============================================================================

const DEFAULT_SETTINGS: Required<ParseSettings> = {
    enableTruncation: true,
    maxRows: 10000,
    warnThreshold: 5000,
    maxFileSize: 50 * 1024 * 1024 // 50MB
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function validateDataStructure(data: unknown): data is DataItem[] {
    if (!Array.isArray(data) || data.length === 0) return false;
    
    return data.every((item): item is DataItem => 
        item && 
        typeof item === 'object' &&
        typeof item.types === 'string' &&
        typeof item.counts === 'number' &&
        typeof item.probs === 'number' &&
        typeof item.totalunique === 'number' &&
        item.counts > 0 &&
        item.probs >= 0 &&
        item.probs <= 1
    );
}

// =============================================================================
// CORE PROCESSING FUNCTIONS
// =============================================================================

function recalculateStats(data: DataItem[], maxRows: number): RecalculationResult {
    // Sort by counts (descending) to get top words
    const sortedData = [...data].sort((a, b) => b.counts - a.counts);
    
    // Take top N rows
    const topData = sortedData.slice(0, maxRows);
    
    // Calculate totals
    const originalTotalCounts = data.reduce((sum, item) => sum + item.counts, 0);
    const newTotalCounts = topData.reduce((sum, item) => sum + item.counts, 0);
    const newTotalUnique = topData.length;
    
    // Update probabilities based on new total
    const recalculatedData: DataItem[] = topData.map(item => ({
        types: item.types,
        counts: item.counts,
        probs: item.counts / newTotalCounts, // Recalculate probability
        totalunique: newTotalUnique
    }));
    
    return {
        data: recalculatedData,
        originalTotal: data.length,
        newTotal: newTotalUnique,
        originalTotalCounts,
        newTotalCounts
    };
}

function findColumnHeader(headers: string[], possibleNames: string[]): string | null {
    for (const name of possibleNames) {
        const found = headers.find(h => h.toLowerCase() === name.toLowerCase());
        if (found) return found;
    }
    return null;
}

function parseCSV(csvText: string, settings: Required<ParseSettings>): { data: DataItem[], meta: ProcessingMeta } {
    // Use d3 to parse CSV - robust and reliable
    const parsed = d3.csvParse(csvText);
    
    if (!parsed || parsed.length === 0) {
        throw new Error('No data found in CSV file');
    }
    
    // Get headers and find required columns
    const headers = parsed.columns;
    
    const typeColumn = findColumnHeader(headers, ['types', 'type', 'words', 'word', 'terms', 'term']);
    const countsColumn = findColumnHeader(headers, ['counts', 'count', 'frequency', 'freq', 'n']);
    const probsColumn = findColumnHeader(headers, ['probs', 'prob', 'probability', 'probabilities', 'p']);
    const totaluniqueColumn = findColumnHeader(headers, ['totalunique', 'total_unique', 'total', 'unique_total']);
    
    // Validate required columns
    if (!typeColumn || !countsColumn || !probsColumn) {
        const missing: string[] = [];
        if (!typeColumn) missing.push('types/words');
        if (!countsColumn) missing.push('counts/frequency');
        if (!probsColumn) missing.push('probs/probability');
        throw new Error(`Missing required columns: ${missing.join(', ')}. Found: ${headers.join(', ')}`);
    }
    
    // Process rows
    const rawData: DataItem[] = [];
    let skippedRows = 0;
    
    for (let i = 0; i < parsed.length; i++) {
        const row = parsed[i];
        
        const typeValue = row[typeColumn];
        const countsStr = row[countsColumn];
        const probsStr = row[probsColumn];
        
        // Skip rows with missing essential data
        if (!typeValue || !countsStr || !probsStr) {
            skippedRows++;
            continue;
        }
        
        const counts = Number(countsStr);
        const probs = Number(probsStr);
        
        // Validate numbers
        if (isNaN(counts)) {
            console.warn(`Row ${i + 2}: invalid counts "${countsStr}" for "${typeValue}"`);
            skippedRows++;
            continue;
        }
        
        if (isNaN(probs)) {
            console.warn(`Row ${i + 2}: invalid probs "${probsStr}" for "${typeValue}"`);
            skippedRows++;
            continue;
        }
        
        if (counts <= 0) {
            console.warn(`Row ${i + 2}: counts <= 0 (${counts}) for "${typeValue}"`);
            skippedRows++;
            continue;
        }
        
        if (probs < 0) {
            console.warn(`Row ${i + 2}: probs < 0 (${probs}) for "${typeValue}"`);
            skippedRows++;
            continue;
        }
        
        rawData.push({
            types: typeValue,
            counts,
            probs,
            totalunique: totaluniqueColumn ? Number(row[totaluniqueColumn]) || 0 : 0
        });
    }
    
    if (rawData.length === 0) {
        throw new Error('No valid data rows found');
    }
    
    // Apply truncation if needed
    return applyTruncation(rawData, skippedRows, settings);
}

function parseJSON(jsonData: unknown, settings: Required<ParseSettings>): { data: DataItem[], meta: ProcessingMeta } {
    if (!Array.isArray(jsonData)) {
        throw new Error('JSON data must be an array');
    }
    
    if (jsonData.length === 0) {
        throw new Error('JSON array is empty');
    }
    
    // Validate structure
    if (!validateDataStructure(jsonData)) {
        throw new Error('Invalid JSON structure. Expected array of objects with types, counts, probs, and totalunique fields.');
    }
    
    // Apply truncation if needed
    return applyTruncation(jsonData, 0, settings);
}

function applyTruncation(
    data: DataItem[], 
    skippedRows: number, 
    settings: Required<ParseSettings>
): { data: DataItem[], meta: ProcessingMeta } {
    
    if (!settings.enableTruncation || data.length <= settings.maxRows) {
        // No truncation needed - just ensure totalunique is correct
        const totalUnique = data.length;
        const finalData = data.map(item => ({
            ...item,
            totalunique: totalUnique
        }));
        
        return {
            data: finalData,
            meta: {
                totalRows: data.length,
                processedRows: finalData.length,
                skippedRows,
                wasTruncated: false,
                truncatedAt: null,
                wasRecalculated: false
            }
        };
    }
    
    // Smart truncation: take top words and recalculate
    const recalcResult = recalculateStats(data, settings.maxRows);
    
    return {
        data: recalcResult.data,
        meta: {
            totalRows: data.length,
            processedRows: recalcResult.data.length,
            skippedRows,
            wasTruncated: true,
            truncatedAt: settings.maxRows,
            wasRecalculated: true,
            originalTotalCounts: recalcResult.originalTotalCounts,
            newTotalCounts: recalcResult.newTotalCounts,
            coveragePercent: ((recalcResult.newTotalCounts / recalcResult.originalTotalCounts) * 100).toFixed(1)
        }
    };
}

function generateWarnings(meta: ProcessingMeta, settings: Required<ParseSettings>): string[] {
    const warnings: string[] = [];
    
    if (meta.wasRecalculated && meta.coveragePercent) {
        warnings.push(
            `Dataset truncated to top ${meta.processedRows.toLocaleString()} most frequent items ` +
            `(${meta.coveragePercent}% of original frequency mass). ` +
            `Probabilities recalculated for subset.`
        );
    } else if (meta.wasTruncated) {
        warnings.push(
            `File was truncated from ${meta.totalRows.toLocaleString()} to ${meta.processedRows.toLocaleString()} rows.`
        );
    } else if (meta.totalRows > settings.warnThreshold) {
        warnings.push(
            `Large dataset detected (${meta.totalRows.toLocaleString()} items). Processing may be slow.`
        );
    }
    
    if (meta.skippedRows > 0) {
        warnings.push(`Skipped ${meta.skippedRows} invalid rows.`);
    }
    
    return warnings;
}

// =============================================================================
// MAIN EXPORT FUNCTION
// =============================================================================

export async function parseDataFile(file: File, options: ParseSettings = {}): Promise<ParseResult> {
    // Merge with defaults
    const settings: Required<ParseSettings> = {
        ...DEFAULT_SETTINGS,
        ...options
    };

    try {
        // Check file size
        if (file.size > settings.maxFileSize) {
            throw new Error(
                `File too large (${formatFileSize(file.size)}). ` +
                `Maximum size is ${formatFileSize(settings.maxFileSize)}.`
            );
        }
        
        // Read file
        const text = await file.text();
        const fileName = file.name.replace(/\.(json|csv)$/i, '');
        const extension = file.name.split('.').pop()?.toLowerCase();
        
        // Parse based on file type
        let result: { data: DataItem[], meta: ProcessingMeta };
        
        if (extension === 'json') {
            const jsonData = JSON.parse(text);
            result = parseJSON(jsonData, settings);
        } else if (extension === 'csv') {
            result = parseCSV(text, settings);
        } else {
            throw new Error('Unsupported file type. Please use .json or .csv files.');
        }
        
        // Generate warnings
        const warnings = generateWarnings(result.meta, settings);
        
        return {
            success: true,
            data: result.data,
            fileName,
            fileType: extension,
            meta: result.meta,
            warnings,
            error: null
        };
        
    } catch (error) {
        return {
            success: false,
            data: null,
            fileName: null,
            fileType: null,
            meta: null,
            warnings: [],
            error: error instanceof Error ? error.message : 'Unknown error occurred'
        };
    }
}