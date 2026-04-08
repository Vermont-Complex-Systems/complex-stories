import { getVisibleStories } from '$lib/data/stories';

export const load = () => {
  return {
    stories: getVisibleStories()
  };
};
