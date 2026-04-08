import { error } from '@sveltejs/kit';
import { blogs } from '$lib/data/blogs';

// Vite analyzes this glob at build time — no runtime dynamic import needed
const markdownModules = import.meta.glob('/src/lib/blog/*.md', {
  query: '?raw',
  import: 'default'
});

export const load = async ({ params }: { params: { slug: string } }) => {
  const blog = blogs.find((d) => d.slug === params.slug);

  if (!blog) {
    error(404, 'Blog post not found');
  }

  let content = '';

  if (blog.hasMarkdown) {
    const markdownPath = `/src/lib/blog/${params.slug}.md`;
    if (markdownPath in markdownModules) {
      content = (await markdownModules[markdownPath]()) as string;
    } else {
      console.warn(`No markdown file found for ${params.slug}`);
    }
  }

  return { blog, content };
};
