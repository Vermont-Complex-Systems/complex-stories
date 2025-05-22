import { error } from '@sveltejs/kit';

export async function load({ params }) {
  try {
    // Dynamically import the JSON file based on the slug
    const story = await import(`$data/${params.slug}.json`);
    
    return {
      story: story.default || story
    };
  } catch (err) {
    console.error(`Story not found: ${params.slug}`, err);
    error(404, `Story "${params.slug}" not found`);
  }
}