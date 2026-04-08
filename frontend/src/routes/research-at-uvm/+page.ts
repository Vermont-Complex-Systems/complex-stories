import { getSortedResearchGroups } from '$lib/data/research';

export const load = () => {
  return {
    posts: getSortedResearchGroups()
  };
};
