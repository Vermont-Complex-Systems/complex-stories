// src/lib/stories/open-academic-analytics/data/loader.js
import paperUrl from './processed/paper.parquet?url';
import authorUrl from './processed/author.parquet?url';
import coauthorUrl from './processed/coauthor.parquet?url';

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

export { paperUrl, authorUrl, coauthorUrl };