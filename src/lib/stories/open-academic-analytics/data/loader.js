// src/lib/stories/open-academic-analytics/data/loader.js
import { base } from '$app/paths';

// Use static URLs instead of imports
export const paperUrl = `${base}/data/paper.parquet`;

export const datasets = {
  paper: {
    url: paperUrl,
    description: 'UVM paper publications'
  },
};