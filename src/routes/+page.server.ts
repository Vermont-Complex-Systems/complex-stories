import storiesIndex from '$data/stories.csv';

export async function load() {
  const stories = await Promise.all(
    storiesIndex.map(async (row) => {
      const story = await import(`$data/${row.slug}.json`);
      return {
        slug: story.slug,
        title: story.title,
        description: story.description
      };
    })
  );

  return {
    summaries: stories
  };
}