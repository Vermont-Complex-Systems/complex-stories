import { error } from '@sveltejs/kit';
import blogsData from '$data/blogs.js';

export function entries() {
  return blogsData.map(blog => ({ slug: blog.slug }));
}

export async function load({ params }) {
  const { slug } = params;
  
  const blog = blogsData.find(d => d.slug === slug);
  
  if (!blog) {
    throw error(404, 'Blog post not found');
  }

  let content = blog.content || '';
  
  if (blog.hasMarkdown) {
    try {
      // Try to import the markdown file
      const markdownModule = await import(`../../../lib/blog/${slug}.md?raw`);
      content = markdownModule.default;
    } catch (e) {
      console.warn(`No markdown file found for ${slug}:`, e);
      content = blog.content || blog.tease || '';
    }
  }

  return {
    blog,
    content
  };
}