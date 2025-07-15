// src/lib/stories/open-academic-analytics/data/loader.js
import { base } from '$app/paths';

// Use static URLs instead of imports
export const trainingUrl = `https://raw.githubusercontent.com/Vermont-Complex-Systems/datasets/main/static/data/academic-research-groups.parquet`;
export const departmentURL = `https://raw.githubusercontent.com/Vermont-Complex-Systems/datasets/main/static/data/academic-department.parquet`;

export const datasets = {
  training: {
    url: trainingUrl,
    description: 'Model output'
  },
  department: {
    url: departmentURL,
    description: 'Department to college mapping'
  },
};