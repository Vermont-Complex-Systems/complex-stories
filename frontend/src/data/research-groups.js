// src/data/blogs.js
import data from "$data/research-group.csv";
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
      title: d.slug || d.hed || d.short || d.name || 'Untitled',
      // Try different possible column names for description  
      tease: d.group_url || d.description || d.summary || '',
      excerpt: d.excerpt || d.tease || d.description || d.summary || '',
      oa_uid: d.oa_uid || '',
      // Handle author field
      author: d.oa_display_name ? d.oa_display_name.split(",").map(a => 
          a.trim()
          .toLowerCase()
          .split(' ')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ')
        ) : [],
      // Handle tags field
      tags: d.college ? d.college.split(",").map(t => t.trim()) : [],
      hasMarkdown: d.content_type === 'markdown',
      has_research_group: +d.has_research_group
    };
  })
  .filter((d) => !d.hide && d.slug && d.has_research_group == 1) // Only include rows with slugs
  .map((d, i) => ({
    ...d,
    id: i + 1
  }));


export default clean;