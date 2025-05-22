import { error } from '@sveltejs/kit';
import storiesIndex from '$data/stories.csv';

export async function load() {
  try {
    const stories = await Promise.all(
      storiesIndex.map(async (row) => {
        try {
          const story = await import(`$data/${row.slug}.json`);
          const storyData = story.default || story;
          return {
            slug: storyData.slug,
            title: storyData.title,
            description: storyData.description
          };
        } catch (err) {
          console.error(`Failed to load story: ${row.slug}`, err);
          return null;
        }
      })
    );

    const validStories = stories.filter(story => story !== null);

    return {
      summaries: validStories
    };
  } catch (err) {
    console.error('Error loading stories:', err);
    error(500, 'Failed to load stories');
  }
}