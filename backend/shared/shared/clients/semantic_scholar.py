"""
Semantic Scholar API Client
Standalone client for interacting with Semantic Scholar API with rate limiting.
"""

import requests
from requests import Response
import time
from threading import Lock
from collections import deque
from typing import Optional, List, Dict
import pandas as pd


class SemanticScholarClient:
    """Stateful client for Semantic Scholar API with rate limiting"""
    
    def __init__(self, api_key: Optional[str] = None, max_requests_per_second: int = 1, 
                 max_requests_per_day: int = 5000, base_url: str = "https://api.semanticscholar.org/graph/v1"):
        self.api_key = api_key
        self.max_requests_per_second = max_requests_per_second
        self.max_requests_per_day = max_requests_per_day
        self.base_url = base_url
        
        # Thread-safe rate limiting
        self._lock = Lock()
        self._request_times = deque()
        self._daily_request_count = 0
        self._daily_reset_time = time.time() + 86400  # 24 hours from now
        
        # Set up headers
        self.headers = {}
        if self.api_key:
            self.headers["x-api-key"] = self.api_key
            # Higher limits with API key
            if self.max_requests_per_second == 1:  # Only if using default
                self.max_requests_per_second = 2
            if self.max_requests_per_day == 5000:  # Only if using default
                self.max_requests_per_day = 10000

    def _check_rate_limits(self):
        """Check and enforce rate limits"""
        current_time = time.time()
        
        with self._lock:
            # Reset daily counter if 24 hours have passed
            if current_time > self._daily_reset_time:
                self._daily_request_count = 0
                self._daily_reset_time = current_time + 86400
            
            # Check daily limit
            if self._daily_request_count >= self.max_requests_per_day:
                raise Exception(f"Daily rate limit of {self.max_requests_per_day} requests exceeded")
            
            # Remove requests older than 1 second
            while self._request_times and current_time - self._request_times[0] > 1.0:
                self._request_times.popleft()
            
            # Check per-second limit
            if len(self._request_times) >= self.max_requests_per_second:
                sleep_time = 1.0 - (current_time - self._request_times[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    # Remove the old request after sleeping
                    self._request_times.popleft()
            
            # Record this request
            self._request_times.append(current_time)
            self._daily_request_count += 1

    def request(self, endpoint: str, params: Optional[dict] = None, method: str = "GET", json_data: Optional[dict] = None) -> Response:
        """Make a rate-limited request to Semantic Scholar API"""
        self._check_rate_limits()
        
        # Prepare parameters
        if params is None:
            params = {}
        
        # Make the request
        url = f"{self.base_url}/{endpoint}"
        
        if method.upper() == "POST":
            response = requests.post(
                url,
                params=params,
                json=json_data,
                headers=self.headers
            )
        else:
            response = requests.get(
                url,
                params=params,
                headers=self.headers
            )
        
        # Handle rate limit responses
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"Rate limited by Semantic Scholar. Waiting {retry_after} seconds before retry.")
            time.sleep(retry_after)
            return self.request(endpoint, params, method, json_data)  # Retry once
        
        if response.status_code == 404:
            print(f"Resource not found: {endpoint}")
            return response  # Return 404 response for handling by caller
        
        response.raise_for_status()
        return response

    def clean_doi(self, doi: str) -> str:
        """Clean DOI by removing common prefixes."""
        prefixes_to_remove = [
            "https://doi.org/",
            "http://doi.org/",
            "doi.org/",
            "doi:",
            "DOI:"
        ]
        
        cleaned_doi = doi.strip()
        for prefix in prefixes_to_remove:
            if cleaned_doi.lower().startswith(prefix.lower()):
                cleaned_doi = cleaned_doi[len(prefix):]
                break
        
        return cleaned_doi

    def get_paper(self, paper_id: str, fields: List[str] = None) -> Optional[dict]:
        """Get a single paper by ID"""
        if fields is None:
            fields = ["paperId", "title", "abstract", "embedding"]
        
        params = {"fields": ",".join(fields)}
        response = self.request(f"paper/{paper_id}", params)
        
        if response.status_code == 404:
            return None
        
        return response.json()

    def get_papers_batch(self, dois: List[str], fields: List[str] = None, batch_size: int = 500) -> List[Optional[Dict]]:
        """Retrieve multiple papers using the batch endpoint with DOI identifiers."""
        if fields is None:
            fields = ["paperId", "title", "embedding"]
        
        all_results = []
        
        total_batches = (len(dois) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(dois))
            batch_dois = dois[start_idx:end_idx]
            
            # Clean and format DOIs for the batch API
            cleaned_dois = [self.clean_doi(doi) for doi in batch_dois]
            doi_ids = [f"DOI:{cleaned_doi}" for cleaned_doi in cleaned_dois]
            
            print(f"Processing batch {batch_num + 1}/{total_batches} ({len(batch_dois)} DOIs)")
            
            if batch_num == 0 and len(cleaned_dois) > 0:
                print(f"Example cleaned DOI: {batch_dois[0]} -> {cleaned_dois[0]}")
            
            params = {"fields": ",".join(fields)}
            json_data = {"ids": doi_ids}
            
            response = self.request("paper/batch", params, method="POST", json_data=json_data)
            
            if response.status_code == 200:
                batch_results = response.json()
                
                # Add original DOI to each result for reference
                for i, result in enumerate(batch_results):
                    if result is not None:  # Some papers might not be found
                        result["original_doi"] = batch_dois[i]
                
                all_results.extend(batch_results)
                found_count = len([r for r in batch_results if r is not None])
                print(f"Successfully retrieved {found_count} papers from batch")
            else:
                print(f"Batch request failed with status {response.status_code}")
        
        return all_results

    def get_multiple_embeddings(self, dois: List[str], batch_size: int = 500) -> List[Dict]:
        """Get embeddings for multiple papers using their DOIs via batch API."""
        print(f"Processing {len(dois)} DOIs using batch API...")
        
        # Get papers in batches
        all_papers = self.get_papers_batch(
            dois, 
            fields=["paperId", "title", "abstract", "embedding", "fieldsOfStudy", "s2FieldsOfStudy"], 
            batch_size=batch_size
        )
        
        # Process results and extract embeddings
        results = []
        found_count = 0
        
        for paper in all_papers:
            if paper is not None and "embedding" in paper:
                embedding_data = {
                    "paperId": paper.get("paperId"),
                    "title": paper.get("title"),
                    "abstract": paper.get("abstract"),
                    "fieldsOfStudy": paper.get("fieldsOfStudy"),
                    "s2FieldsOfStudy": paper.get("s2FieldsOfStudy"),
                    "doi": paper.get("original_doi"),
                    "embedding": paper["embedding"]["vector"] if paper["embedding"] else None
                }
                
                if embedding_data["embedding"] is not None:
                    results.append(embedding_data)
                    found_count += 1
                    if found_count % 50 == 0:
                        print(f"Processed {found_count} embeddings so far...")
        
        print(f"Successfully retrieved {len(results)} embeddings out of {len(dois)} DOIs")
        print(f"{len(dois) - len(results)} DOIs failed or had no embeddings")
        
        return results

    def save_embeddings_to_parquet(self, embeddings: List[Dict], filename: str = "paper_embeddings.parquet"):
        """Save embeddings to a Parquet file for efficient storage and loading."""
        if not embeddings:
            print("No embeddings to save")
            return
        
        try:
            # Prepare data for DataFrame
            data = []
            for emb in embeddings:
                if emb['embedding'] is not None:
                    row = {
                        'paper_id': emb['paperId'],
                        'title': emb['title'],
                        'doi': emb['doi'],
                        'embedding_dim': len(emb['embedding']),
                        'embedding': emb['embedding']
                    }
                    data.append(row)
            
            if not data:
                print("No valid embeddings found to save")
                return
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Save to Parquet
            df.to_parquet(filename, index=False, compression='snappy')
            print(f"Embeddings saved to {filename}")
            print(f"Saved {len(df)} papers with embeddings")
            print(f"Embedding dimension: {df['embedding_dim'].iloc[0] if len(df) > 0 else 'N/A'}")
            
        except Exception as e:
            print(f"Error saving embeddings to Parquet: {e}")
            raise Exception(f"Failed to save embeddings: {e}")

