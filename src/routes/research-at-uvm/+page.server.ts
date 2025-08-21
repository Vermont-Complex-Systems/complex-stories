// src/routes/blog/+page.server.ts
import blogsData from "$data/research-groups.js";

export async function load() {
    const posts = blogsData.map(blog => ({
      id: blog.id,
      slug: blog.slug,
      title: blog.title,
      tease: blog.tease,
      excerpt: blog.excerpt,
      oa_uid: blog.oa_uid,
      group_url: blog.group_url,
      month: blog.month,
      date: blog.date,
      has_research_group: blog.has_research_group,
      author: blog.author,
      tags: blog.tags,
      hasMarkdown: blog.hasMarkdown
    }));

  return {
    posts
  };
}