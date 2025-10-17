// src/routes/datasets/preview.remote.ts

import { query } from '$app/server';
import * as v from 'valibot';

export const getDatasets = query(async() => {
  const apiUrl = `https://api.complexstories.uvm.edu/datasets/`;

  const response = await fetch(apiUrl);

  if (!response.ok) {
    throw new Error(`Failed to fetch datasets: ${response.status} ${response.statusText}`);
  }

  return await response.json();
});


export const previewDataset = query(v.string(), async (slug) => {
    console.log('previewDataset called with:', slug);

    const response = await fetch(`https://api.complexstories.uvm.edu/datasets/${slug}`);

    if (!response.ok) {
      console.error('API response not ok:', response.status, response.statusText);
      throw new Error(`Failed to fetch dataset: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }
);