import storiesData from "$data/stories.js";

export async function load() {
  const stories = storiesData
    // Filter removed: hide_home column causes memory issue with Svelte reactivity
    .map(story => ({
      id: story.id,
      slug: story.slug,
      short: story.short,
      tease: story.tease,
      month: story.month,
      bgColor: story.bgColor,
      href: story.external ? story.href : `/${story.slug}`,
      isExternal: story.external,
      filters: Array.isArray(story.filters) ? story.filters : [story.filters].filter(Boolean) // Ensure it's an array and remove empty values
    }));

  return {
    stories
  };
}