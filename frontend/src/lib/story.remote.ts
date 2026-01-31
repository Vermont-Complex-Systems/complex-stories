import * as v from 'valibot';
import { query } from '$app/server';
import storiesData from '$data/stories.csv';
import authorsData from '$data/authors.js';
import { error, redirect } from '@sveltejs/kit';



// STORIES 

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

const stories: Story[] = (storiesData as any[]).map((d) => ({
  ...d,
  month: formatMonth(d.date),
  tags: parseTags(d.tags)
}));

// Stories not yet ready for the homepage listing
const HIDDEN_STORIES = ['dark-data-survey'];

// Query for getting all stories (sorted newest first, excluding hidden)
export const getStories = query(async () => {
  return stories
    .filter(d => !HIDDEN_STORIES.includes(d.slug))
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
});

// Query for getting a single story by slug
export const getStory = query(v.string(), async (slug) => {
  const story = stories.find(d => d.slug === slug);

  if (!story) {
    error(404, 'Story not found');
  }

  // If it has an external URL, redirect to it
  if (story.externalUrl) {
    redirect(302, story.externalUrl);
  }

  // Load copy data for internal stories
  let copyData = {};
  try {
    const module = await import(`$lib/stories/${slug}/data/copy.json`);
    copyData = module.default || module;
  } catch (e) {
    console.warn(`No copy.json found for ${slug}`);
  }

  return {
    story,
    copyData
  };
});

// AUTHORS

export interface Author {
  id: string;
  name: string;
  email: string;
  slug: string;
  position: string;
  social: string;
  url: string;
  bio: string;
  pronoun: string;
}

// Query for getting an author and their stories
export const getAuthor = query(v.string(), async (slug) => {
  const author = (authorsData as Author[]).find(d => d.slug === slug);

  if (!author) {
    error(404, 'Author not found');
  }

  const authorStories = stories
    .filter(d => d.author === author.name)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  return { stories: authorStories, author };
});
