
import { query } from "$app/server";
import * as v from "valibot"
import { error } from '@sveltejs/kit';

export const loadPaperData = query(
    v.object({
        authorName: v.string(),
        filterBigPapers: v.boolean()
     }),
    async ({authorName, filterBigPapers}) => {
    const response = await fetch(`https://api.complexstories.uvm.edu/open-academic-analytics/papers/${authorName}?filter_big_papers=${filterBigPapers}`);
    if (!response.ok) error(404, 'Not found');
    const data = await response.json();
    const papers = data.papers.map(paper => ({
          ...paper,
          pub_date: new Date(paper.publication_date).toISOString().split('T')[0]
    }));
    return { papers };
  });

export const loadCoauthorData = query(
    v.object({
        authorName: v.string(),
        filterBigPapers: v.boolean()
     }),
    async ({authorName, filterBigPapers}) => {
    const response = await fetch(`https://api.complexstories.uvm.edu/open-academic-analytics/coauthors/${authorName}?filter_big_papers=${filterBigPapers}`);
    if (!response.ok) error(404, 'Not found');
    const data = await response.json();
    const coauthors = data.coauthors.map(coauthor => ({
          ...coauthor,
          pub_date: new Date(coauthor.publication_date).toISOString().split('T')[0]
    }));
    return { coauthors };
  });

export const loadAvailableAuthors = query(async () => {
    const response = await fetch(`https://api.complexstories.uvm.edu/open-academic-analytics/authors`);
    if (!response.ok) error(404, 'Not found');
    return response.json()
  });