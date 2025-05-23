import storiesIndex from '$data/stories.csv';

export function load() {
  const stories = storiesIndex.map((row) => ({
    slug: row.slug,
    title: row.title,
    description: row.description,
    cardType: row.cardType,
    month: row.month
  }));

  return {
    summaries: stories
  };
}