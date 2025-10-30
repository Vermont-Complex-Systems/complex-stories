
import { query } from "$app/server";
import * as v from "valibot"
import { error } from '@sveltejs/kit';
import { API_BASE } from '$env/static/private'

const API_BASE_URL = API_BASE || 'http://localhost:3001'

export const loadPaperData = query(
    v.object({
        authorName: v.string(),
        filterBigPapers: v.boolean()
     }),
    async ({authorName, filterBigPapers}) => {
    const response = await fetch(`${API_BASE_URL}/open-academic-analytics/papers/${authorName}?filter_big_papers=${filterBigPapers}`);
    if (!response.ok) error(404, 'Not found');
    const papers = await response.json();
    const processedPapers = papers.map(paper => ({
          ...paper,
          pub_date: new Date(paper.publication_date).toISOString().split('T')[0]
    }));
    return processedPapers;
  });

export const loadCoauthorData = query(
    v.object({
        authorName: v.string(),
        filterBigPapers: v.boolean()
     }),
    async ({authorName, filterBigPapers}) => {
    const response = await fetch(`${API_BASE_URL}/open-academic-analytics/coauthors/${authorName}?filter_big_papers=${filterBigPapers}`);
    if (!response.ok) error(404, 'Not found');
    const coauthors = await response.json();
    const processedCoauthors = coauthors.map(coauthor => ({
          ...coauthor,
          pub_date: new Date(coauthor.publication_date).toISOString().split('T')[0]
    }));
    return processedCoauthors;
  });

export const loadAvailableAuthors = query(async () => {
    const response = await fetch(`${API_BASE_URL}/open-academic-analytics/authors`);
    if (!response.ok) error(404, 'Not found');
    const authors = await response.json();
    return authors;
  });