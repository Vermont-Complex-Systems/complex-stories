import { error } from '@sveltejs/kit';
import storiesData from '$data/stories.js';

export async function load({ params }) {
  const { slug } = params;
  console.log('Loading story for slug:', slug);
  
  // Find the story by slug
  const story = storiesData.find(d => d.slug === slug);
  console.log('Found story:', story);
  
  if (!story) {
    console.log('Story not found for slug:', slug);
    throw error(404, 'Story not found');
  }

  // Try to load the story's copy data
  let copyData = {};
  try {
    const copyModule = await import(`$lib/stories/${slug}/data/copy.json`);
    copyData = copyModule.default || copyModule;
    console.log('Loaded copy data:', copyData);
  } catch (e) {
    console.warn(`No copy.json found for ${slug}:`, e);
  }

  return {
    story,
    copyData
  };
}