import { query } from '$app/server';
import researchData from '$data/research-group.csv';

export interface ResearchGroup {
  id: number;
  slug: string;
  title: string;
  tease: string;
  excerpt: string;
  oa_uid: string;
  group_url: string;
  date: string;
  month: string;
  has_research_group: number;
  author: string[];
  tags: string[];
  hasMarkdown: boolean;
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function formatMonth(dateStr: string): string {
  const [month, , year] = dateStr.split('/').map(Number);
  return `${MONTHS[month - 1]} ${year}`;
}

function parseAuthor(name: string): string[] {
  if (!name) return [];
  return name.split(',').map((a) =>
    a.trim().toLowerCase().split(' ')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  );
}

function parseTags(college: string): string[] {
  if (!college) return [];
  return college.split(',').map((t) => t.trim()).filter(Boolean);
}

const researchGroups: ResearchGroup[] = (researchData as any[])
  .filter((d) => !d.hide && d.slug && +d.has_research_group === 1)
  .map((d, i) => ({
    id: i + 1,
    slug: d.slug,
    title: d.slug || d.hed || d.short || d.name || 'Untitled',
    tease: d.group_url || d.description || d.summary || '',
    excerpt: d.excerpt || d.tease || d.description || d.summary || '',
    oa_uid: d.oa_uid || '',
    group_url: d.group_url || '',
    date: d.date,
    month: formatMonth(d.date),
    has_research_group: +d.has_research_group,
    author: parseAuthor(d.oa_display_name),
    tags: parseTags(d.college),
    hasMarkdown: d.content_type === 'markdown'
  }));

export const getResearchGroups = query(async () => {
  return researchGroups.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
});
