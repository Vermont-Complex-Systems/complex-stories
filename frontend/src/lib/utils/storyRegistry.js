const storyModules = import.meta.glob('../stories/*/components/Index.svelte');

export const getStoryComponent = async (slug) => {
  const path = `../stories/${slug}/components/Index.svelte`;
  const module = await storyModules[path]?.();
  return module?.default;
};

// Optional: For development, get available stories (plain JS)
export const getAvailableStorySlugs = () => {
  return Object.keys(storyModules).map(path => {
    const match = path.match(/\.\.\/stories\/(.+)\/components\/Index\.svelte/);
    return match ? match[1] : null;
  }).filter(Boolean);
};