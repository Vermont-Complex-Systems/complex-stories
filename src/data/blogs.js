// src/data/blogs.js
import data from "$data/blog.csv";
import { timeParse, timeFormat } from "d3";

const parseDate = timeParse("%m/%d/%Y");
const formatMonth = timeFormat("%b %Y");

const clean = data
  .map((d) => {
    return {
      ...d,
      date: parseDate(d.date),
      month: formatMonth(parseDate(d.date)),
      slug: d.slug,
      // Try different possible column names for title
      title: d.title || d.hed || d.short || d.name || 'Untitled',
      // Try different possible column names for description  
      tease: d.tease || d.description || d.excerpt || d.summary || '',
      excerpt: d.excerpt || d.tease || d.description || d.summary || '',
      // Handle author field
      author: d.author ? d.author.split(",").map(a => a.trim()) : [],
      // Handle tags field
      tags: d.tags ? d.tags.split(",").map(t => t.trim()) : [],
      hasMarkdown: d.content_type === 'markdown',
    };
  })
  .filter((d) => !d.hide && d.slug) // Only include rows with slugs
  .map((d, i) => ({
    ...d,
    id: i + 1
  }));

export default clean;