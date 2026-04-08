import { getSortedBlogs } from '$lib/data/blogs';

export const load = () => {
  return {
    posts: getSortedBlogs()
  };
};
