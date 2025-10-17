const storyModules = import.meta.glob('../stories/*/components/Index.svelte', { eager: true });

export const getStoryComponent = (slug) => {
  const path = `../stories/${slug}/components/Index.svelte`;
  return storyModules[path]?.default;
};

// Optional: For development, get available stories (plain JS)
export const getAvailableStorySlugs = () => {
  return Object.keys(storyModules).map(path => {
    const match = path.match(/\.\.\/stories\/(.+)\/components\/Index\.svelte/);
    return match ? match[1] : null;
  }).filter(Boolean);
};