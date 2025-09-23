// src/lib/stories/open-academic-analytics/data/loader.js
import { base } from '$app/paths';

// Use static URLs instead of imports
export const uvmProfsURL = `${base}/data/open-academic-analytics/uvm_profs_2023.parquet`;
export const trainingUrl = `${base}/data/open-academic-analytics/training_data.parquet`;
export const departmentURL = `${base}/data/open-academic-analytics/uvm_departments.parquet`;
export const coauthorURL = `${base}/data/coauthor.parquet`;
export const paperURL = `${base}/data/paper.parquet`;

export const datasets = {
  uvm_profs_2023: {
    url: uvmProfsURL,
    description: 'Model output'
  },
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