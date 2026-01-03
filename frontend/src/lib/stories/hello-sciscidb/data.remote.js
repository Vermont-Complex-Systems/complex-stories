
import { query } from "$app/server";
import * as v from "valibot"
import { error } from '@sveltejs/kit';
import { API_BASE } from '$env/static/private'

const API_BASE_URL = API_BASE || 'http://localhost:3001'

// New metric-based data fetching
export const metricData = query(
     v.object({
        start_year: v.integer(),
        end_year: v.integer(),
        fields: v.optional(v.array(v.string())),
        metric_types: v.optional(v.array(v.string())), // 'total', 'has_abstract', 'has_fulltext'
        group_by: v.optional(v.string()) // 'field' or 'venue'
     }),
    async ({start_year, end_year, fields, metric_types, group_by = 'field'}) => {
    const params = new URLSearchParams({
        start_year: start_year.toString(),
        end_year: end_year.toString(),
        group_by: group_by
    });

    // Add field filters if provided
    if (fields && fields.length > 0) {
        fields.forEach(field => params.append('fields', field));
    }

    // Add metric type filters if provided
    if (metric_types && metric_types.length > 0) {
        metric_types.forEach(metric => params.append('metric_types', metric));
    }

    const url = `${API_BASE_URL}/scisciDB/metrics?${params}`;
    console.log(`Fetching ${group_by} metrics: ${url}`);

    const response = await fetch(url);
    if (!response.ok) error(response.status, `API error: ${response.statusText}`);

    const results = await response.json();
    console.log(`Got ${results.length} ${group_by}-metric combinations!`);
    return results;
  });

// Legacy API for backward compatibility
export const countData = query(
     v.object({
        start_year: v.integer(),
        end_year: v.integer(),
        fields: v.optional(v.array(v.string()))
     }),
    async ({start_year, end_year, fields}) => {
    // Use the new metric API but filter for 'total' metric type
    const data = await metricData({
        start_year,
        end_year,
        fields,
        metric_types: ['total']
    });

    // Convert back to old format for compatibility
    return data.map(row => ({
        year: row.year,
        field: row.field,
        count: row.count
    }));
  });

// Helper function for field aggregation with multiple metrics (for FosBarChart)
export const getAllFieldsAgg = query(async () => {
        // Get all metric types for comprehensive view
        const data = await metricData({
            start_year: 1900,
            end_year: 2025,
            metric_types: ['total', 'has_abstract', 'has_fulltext']
        });

        // Aggregate by field and metric_type across all years
        const fieldMetrics = {};
        data.forEach(row => {
            if (!fieldMetrics[row.field]) fieldMetrics[row.field] = {};
            if (!fieldMetrics[row.field][row.metric_type]) fieldMetrics[row.field][row.metric_type] = 0;
            fieldMetrics[row.field][row.metric_type] += row.count;
        });

        // Convert to array format expected by FosBarChart (stacked bars)
        const result = [];
        Object.entries(fieldMetrics).forEach(([field, metrics]) => {
            // Add each metric type as a separate data point
            Object.entries(metrics).forEach(([metric_type, count]) => {
                result.push({ field, metric_type, count });
            });
        });

        // Sort by total count for consistent ordering
        const fieldTotals = {};
        result.forEach(row => {
            if (row.metric_type === 'total') {
                fieldTotals[row.field] = row.count;
            }
        });

        return result.sort((a, b) => {
            const totalA = fieldTotals[a.field] || 0;
            const totalB = fieldTotals[b.field] || 0;
            return totalB - totalA;
        });
    }
);

// Helper function for STEM fields over time (for Streamgraph)
export const getFieldsStem = query(async () => {
        const stemFields = [
            'Computer Science', 'Medicine', 'Physics', 'Chemistry',
            'Biology', 'Mathematics', 'Materials Science', 'Engineering',
            'Environmental Science'
        ];

        const data = await metricData({
            start_year: 2000,
            end_year: 2024,
            fields: stemFields,
            metric_types: ['total', 'has_abstract', 'has_fulltext']
        });

        // Convert to format expected by Streamgraph component
        return data.map(row => ({
            year: row.year,
            field: row.field,
            count: row.count,
            metric: row.metric_type
        }));
    }
);

// Helper function for Social Science fields over time (for Streamgraph)
export const getFieldsSocSci = query(async () => {
        const socSciFields = [
            'Psychology', 'Sociology', 'Economics', 'Political Science',
            'Education', 'Business', 'Law', 'History', 'Philosophy',
            'Art', 'Linguistics', 'Geography'
        ];

        const data = await metricData({
            start_year: 2000,
            end_year: 2024,
            fields: socSciFields,
            metric_types: ['total', 'has_abstract', 'has_fulltext']
        });

        // Convert to format expected by Streamgraph component
        return data.map(row => ({
            year: row.year,
            field: row.field,
            count: row.count,
            metric: row.metric_type
        }));
    }
);

// Get available fields from Google Scholar venues
// export const getFields = query(async () => {
//     const response = await fetch(`${API_BASE_URL}/datasets/google-scholar-venues`);
//     if (!response.ok) error(response.status, `API error: ${response.statusText}`);

//     const venues = await response.json();
//     const fields = [...new Set(venues.map(v => v.field))].sort();
//     console.log(`Got ${fields.length} unique fields from Google Scholar venues`);
//     return fields;
// });

