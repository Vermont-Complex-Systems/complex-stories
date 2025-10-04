// src/routes/datasets/preview.remote.ts

import { query } from '$app/server';
import * as v from 'valibot';

export const getDatasets = query(async() => {
  const apiUrl = `http://127.0.0.1:8000/datasets/`;

  const response = await fetch(apiUrl);

  if (!response.ok) {
    throw new Error(`Failed to fetch datasets: ${response.status} ${response.statusText}`);
  }

  return await response.json();
});


export const previewDataset = query(
  v.object({
    datasetName: v.string(),
    limit: v.optional(v.number(), 10)
  }),
  async ({ datasetName, limit }) => {
    console.log('previewDataset called with:', datasetName, limit);

    const filename = `${datasetName}.parquet`;
    const apiUrl = `http://127.0.0.1:8000/datasets/data/${filename}/preview?limit=${limit}`;

    console.log('Fetching from:', apiUrl);

    const response = await fetch(apiUrl);

    if (!response.ok) {
      console.error('API response not ok:', response.status, response.statusText);
      throw new Error(`Failed to fetch dataset: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    console.log('API result:', result);
    return result;
  }
);