import storiesData from "$data/stories.js";

export async function load() {
  // Filter out external stories from getting internal routes
  const stories = storiesData
    .filter(story => !story.external && !story.isExternal) // Only internal stories
    .map(story => ({
      id: story.id,
      slug: story.slug,
      short: story.short,
      tease: story.tease,
      month: story.month,
      bgColor: story.bgColor,
      href: `/${story.slug}`,
      filters: story.filters
    }));

  return {
    stories
  };
}