
import { query } from "$app/server";
import * as v from "valibot"
import { error } from '@sveltejs/kit';
import { API_BASE } from '$env/static/private'

const API_BASE_URL = API_BASE || 'http://localhost:3001'

export const loadDoddsPaperData = query(async () => {
    const response = await fetch(`${API_BASE_URL}/open-academic-analytics/papers/Peter%20Sheridan%20Dodds?filter_big_papers=false`);
    if (!response.ok) error(404, 'Not found');
    const papers = await response.json();
    const processedPapers = papers.map(paper => ({
          ...paper,
          pub_date: new Date(paper.publication_date).toISOString().split('T')[0]
    }));
    return processedPapers;
  });

export const loadDoddsCoauthorData = query(async () => {
    const response = await fetch(`${API_BASE_URL}/open-academic-analytics/coauthors/Peter%20Sheridan%20Dodds?filter_big_papers=false`);
    if (!response.ok) error(404, 'Not found');
    const coauthors = await response.json();
    const processedCoauthors = coauthors.map(coauthor => ({
          ...coauthor,
          pub_date: new Date(coauthor.publication_date).toISOString().split('T')[0]
    }));
    return processedCoauthors;
  });

export const loadUvmProfsData = query(async () => {
    const response = await fetch(`${API_BASE_URL}/datasets/academic-research-groups?skip=0&payroll_year=2023&format=json`);
    if (!response.ok) error(404, 'Not found');
    const uvmProfs = await response.json();
    return uvmProfs;
  });

export const loadEmbeddingsData = query(async () => {
    const response = await fetch(`${API_BASE_URL}/open-academic-analytics/embeddings`);
    if (!response.ok) error(404, 'Not found');
    const embeddings = await response.json();
    return embeddings;
  });