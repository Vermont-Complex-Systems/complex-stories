// src/lib/stories/open-academic-analytics/data/loader.js
import { base } from '$app/paths';

// Use static URLs instead of imports
export const trainingUrl = `${base}/data/open-academic-analytics/uvm_profs_2023.parquet`;
export const departmentURL = `${base}/data/open-academic-analytics/uvm_departments.parquet`;
export const coauthorURL = `${base}/data/open-academic-analytics/coauthor.parquet`;
export const paperURL = `${base}/data/open-academic-analytics/paper.parquet`;

export const datasets = {
  training: {
    url: trainingUrl,
    description: 'Model output'
  },
  department: {
    url: departmentURL,
    description: 'Department to college mapping'
  },
  coauthor: {
    url: coauthorURL,
    description: 'Department to college mapping'
  },
  paper: {
    url: paperURL,
    description: 'Department to college mapping'
  },
};