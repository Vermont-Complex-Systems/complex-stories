import storiesData from "$data/stories.js";

export async function load() {
  const stories = storiesData.map(story => ({
    id: story.id,
    slug: story.slug,
    short: story.short,
    tease: story.tease,
    month: story.month,
    bgColor: story.bgColor,
    href: story.external ? story.href : `/${story.slug}`,
    isExternal: story.external,
    filters: Array.isArray(story.filters) ? story.filters : [story.filters] // Ensure it's an array
  }));

  console.log("Processed stories:", stories.slice(0, 3)); // Debug log

  return {
    stories
  };
}