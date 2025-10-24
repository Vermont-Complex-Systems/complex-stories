// src/routes/datasets/preview.remote.ts

import { query } from '$app/server';
import * as v from 'valibot';
import { API_BASE } from '$env/static/private';

const API_BASE_URL = API_BASE || 'http://localhost:3001';

export const getDatasets = query(async() => {
  // API base URL - automatically switches based on environment
  const apiUrl = `${API_BASE_URL}/datasets/`;

  const response = await fetch(apiUrl);

  if (!response.ok) {
    throw new Error(`Failed to fetch datasets: ${response.status} ${response.statusText}`);
  }

  return await response.json();
});


export const previewDataset = query(v.string(), async (slug) => {
    console.log('previewDataset called with:', slug);

    // API base URL - automatically switches based on environment
    const apiBase = `${API_BASE_URL}/datasets`;
    let response;

    if (slug === 'academic-research-groups') {
      // Use the new annotations endpoint without limit to show all records
      response = await fetch(`${apiBase}/academic-research-groups`);
    } else {
      // Fallback for other datasets
      response = await fetch(`${apiBase}/${slug}`);
    }

    if (!response.ok) {
      console.error('API response not ok:', response.status, response.statusText);
      throw new Error(`Failed to fetch dataset: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }
);