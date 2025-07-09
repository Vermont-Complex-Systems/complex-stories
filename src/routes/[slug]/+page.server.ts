import { error, redirect } from '@sveltejs/kit';
import storiesData from '$data/stories.js';

// Tell SvelteKit which dynamic routes to prerender
export function entries() {
  return storiesData
    .filter(story => !story.isExternal) // Only prerender internal stories
    .map(story => ({ slug: story.slug }));
}

export async function load({ params }) {
  const { slug } = params;
  
  
  // Find the story by slug
  const story = storiesData.find(d => d.slug === slug);
  
  if (!story) {
    console.log('Story not found in data');
    throw error(404, 'Story not found');
  }
  
  // If it's an external story, redirect to the external URL
  if (story.isExternal) {
    throw redirect(302, story.href);
  }

  // Continue with internal story loading...
  let copyData = {};
  try {
    copyData = await import(`$lib/stories/${slug}/data/copy.json`);
  } catch (e) {
    console.warn(`No copy.json found for ${slug}`);
  }

  return {
    story,
    copyData: copyData.default || copyData
  };
}