// src/lib/stories/open-academic-analytics/data/loader.js
// Dynamic imports that resolve at runtime
export async function getDataUrls() {
  const [paperModule, authorModule, coauthorModule] = await Promise.all([
    import('./processed/paper.parquet?url'),
    import('./processed/author.parquet?url'),
    import('./processed/coauthor.parquet?url')
  ]);

  return {
    paperUrl: paperModule.default,
    authorUrl: authorModule.default,
    coauthorUrl: coauthorModule.default
  };
}