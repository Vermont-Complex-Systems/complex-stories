// src/routes/blog/+page.server.ts
import blogsData from "$data/blogs.js";

export async function load() {
    const posts = blogsData.map(blog => ({
      id: blog.id,
      slug: blog.slug,
      title: blog.title,
      tease: blog.tease,
      excerpt: blog.excerpt,
      month: blog.month,
      date: blog.date,
      author: blog.author,
      tags: blog.tags,
      hasMarkdown: blog.hasMarkdown
    }));

  return {
    posts
  };
}