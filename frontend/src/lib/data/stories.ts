import storiesData from '$data/stories.csv';

export interface Story {
  slug: string;
  title: string;
  description: string;
  author: string;
  date: string;
  month: string;
  externalUrl: string;
  tags: string[];
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function formatMonth(dateStr: string): string {
  const [month, , year] = dateStr.split('/').map(Number);
  return `${MONTHS[month - 1]} ${year}`;
}

function parseTags(tags: string): string[] {
  if (!tags) return [];
  return tags.split(',').map((t) => t.trim()).filter(Boolean);
}

export const stories: Story[] = (storiesData as any[]).map((d) => ({
  ...d,
  month: formatMonth(d.date),
  tags: parseTags(d.tags)
}));

// Stories not yet ready for the homepage listing
export const HIDDEN_STORIES = ['dark-data-survey'];

export function getVisibleStories(): Story[] {
  return stories
    .filter((d) => !HIDDEN_STORIES.includes(d.slug))
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}
