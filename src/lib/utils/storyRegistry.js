// Debug version to see what's being imported
const storyModules = import.meta.glob('../stories/*/components/Index.svelte', { eager: true });

console.log('Available story modules:', Object.keys(storyModules));

export const getStoryComponent = (slug) => {
  const path = `../stories/${slug}/components/Index.svelte`;
  console.log('Looking for component at path:', path);
  console.log('Available paths:', Object.keys(storyModules));
  const component = storyModules[path]?.default;
  console.log('Found component:', component);
  return component;
};