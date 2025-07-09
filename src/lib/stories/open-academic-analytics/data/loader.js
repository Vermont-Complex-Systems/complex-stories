// src/lib/stories/open-academic-analytics/data/loader.js
import { base } from '$app/paths';

// Use static URLs instead of imports
export const paperUrl = `${base}/data/open-academic-analytics/paper.parquet`;
export const authorUrl = `${base}/data/open-academic-analytics/author.parquet`;
export const coauthorUrl = `${base}/data/open-academic-analytics/coauthor.parquet`;

// Debug: log the URLs to see what we're getting
console.log('Paper URL:', paperUrl);
console.log('Author URL:', authorUrl);
console.log('Coauthor URL:', coauthorUrl);

export const datasets = {
  paper: {
    url: paperUrl,
    description: 'Academic paper publications'
  },
  author: {
    url: authorUrl,
    description: 'Author information'
  },
  coauthor: {
    url: coauthorUrl,
    description: 'Coauthor relationships'
  }
};