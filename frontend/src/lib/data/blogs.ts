import blogsData from '$data/blog.csv';

export interface Blog {
  id: number;
  slug: string;
  title: string;
  tease: string;
  excerpt: string;
  date: string;
  month: string;
  author: string[];
  tags: string[];
  hasMarkdown: boolean;
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function formatMonth(dateStr: string): string {
  const [month, , year] = dateStr.split('/').map(Number);
  return `${MONTHS[month - 1]} ${year}`;
}

function parseAuthor(author: string): string[] {
  if (!author) return [];
  return author.split(',').map((a) =>
    a.trim().toLowerCase().split(' ')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  );
}

function parseTags(tags: string): string[] {
  if (!tags) return [];
  return tags.split(',').map((t) => t.trim()).filter(Boolean);
}

export const blogs: Blog[] = (blogsData as any[])
  .filter((d) => !d.hide && d.slug)
  .map((d, i) => ({
    id: i + 1,
    slug: d.slug,
    title: d.title || d.hed || d.short || d.name || 'Untitled',
    tease: d.tease || d.description || d.summary || '',
    excerpt: d.excerpt || d.tease || d.description || d.summary || '',
    date: d.date,
    month: formatMonth(d.date),
    author: parseAuthor(d.author),
    tags: parseTags(d.tags),
    hasMarkdown: d.content_type === 'markdown'
  }));

export function getSortedBlogs(): Blog[] {
  return [...blogs].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}
