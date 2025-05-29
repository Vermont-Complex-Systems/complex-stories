import storiesData from "$data/stories.js";

export async function load() {
  const stories = storiesData.map(story => ({
    id: story.id,
    slug: story.slug,
    short: story.short,
    tease: story.tease,
    month: story.month,
    bgColor: story.bgColor,
    href: story.external ? story.href : `/${story.slug}`, // External URL for external stories
    isExternal: story.external,
    filters: story.filters
  }));

  return {
    stories
  };
}