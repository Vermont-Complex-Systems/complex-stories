import storiesData from "$data/stories.js";

export async function load() {
  // Pass all the story data your Stories component needs
  const stories = storiesData.map(story => ({
    id: story.id,
    slug: story.slug,
    short: story.short,
    tease: story.tease,
    month: story.month,
    bgColor: story.bgColor,
    href: `/${story.slug}`, // Local links to your story pages
    filters: story.filters
  }));

  return {
    stories
  };
}