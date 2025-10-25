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
import hashlib
import json
import sqlite3
from pathlib import Path


class SemanticScholarClient:
    """Stateful client for Semantic Scholar API with rate limiting"""
    
    def __init__(self, api_key: Optional[str] = None, max_requests_per_second: int = 1,
                 max_requests_per_day: int = 5000, base_url: str = "https://api.semanticscholar.org/graph/v1",
                 cache_db_path: str = "~/.semantic_scholar_cache.db"):
        self.api_key = api_key
        self.max_requests_per_second = max_requests_per_second
        self.max_requests_per_day = max_requests_per_day
        self.base_url = base_url

        # Thread-safe rate limiting
        self._lock = Lock()
        self._request_times = deque()
        self._daily_request_count = 0
        self._daily_reset_time = time.time() + 86400  # 24 hours from now

        # Persistent cache for venue counts
        self.cache_db_path = Path(cache_db_path).expanduser()
        self._init_cache_db()

        # Simple in-memory cache for venue counts (legacy - now backed by DB)
        self._venue_count_cache = {}
        
        # Set up headers with User-Agent to avoid bot detection
        self.headers = {
            "User-Agent": "SemanticScholarClient/1.0 (Academic Research; Contact: research@complexstories.uvm.edu)"
        }
        if self.api_key:
            self.headers["x-api-key"] = self.api_key
            # Higher limits with API key
            if self.max_requests_per_second == 1:  # Only if using default
                self.max_requests_per_second = 2
            if self.max_requests_per_day == 5000:  # Only if using default
                self.max_requests_per_day = 10000

    def _init_cache_db(self):
        """Initialize the SQLite cache database"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS venue_counts (
                        cache_key TEXT PRIMARY KEY,
                        venue TEXT NOT NULL,
                        year TEXT,
                        min_citations INTEGER,
                        total_papers INTEGER NOT NULL,
                        requests_made INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_venue_year
                    ON venue_counts(venue, year, min_citations)
                """)
                conn.commit()
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize cache database: {e}")
            print(f"   Cache will fall back to in-memory only")

    def _get_cached_venue_count(self, venue: str, year: str = None, min_citations: int = None) -> Optional[dict]:
        """Get cached venue count from database"""
        cache_key = f"{venue}|{year}|{min_citations}"

        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.execute("""
                    SELECT total_papers, requests_made, created_at
                    FROM venue_counts
                    WHERE cache_key = ?
                """, (cache_key,))

                row = cursor.fetchone()
                if row:
                    return {
                        "total_papers": row[0],
                        "venue": venue,
                        "year": year,
                        "min_citations": min_citations,
                        "requests_made": row[1],
                        "cached": True,
                        "cache_date": row[2]
                    }
        except Exception as e:
            print(f"⚠️  Warning: Cache lookup failed: {e}")

        return None

    def _save_venue_count(self, venue: str, year: str = None, min_citations: int = None,
                         total_papers: int = 0, requests_made: int = 0):
        """Save venue count to database cache"""
        cache_key = f"{venue}|{year}|{min_citations}"

        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO venue_counts
                    (cache_key, venue, year, min_citations, total_papers, requests_made, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (cache_key, venue, year, min_citations, total_papers, requests_made))
                conn.commit()
        except Exception as e:
            print(f"⚠️  Warning: Cache save failed: {e}")

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

    def get_snippet(
        self, 
        query: str = None, 
        venue: str = None, 
        year: str = None, 
        minCitationCount: int = 5,
        fields: List[str] = None) -> Optional[dict]:
        """Get text snippets by venue and year"""
        
        if fields is None:
            fields = ["snippet.text","snippet.section","snippet.annotations.sentences","snippet.snippetKind"]
        
        params = {
            "query": query,
            "fields": ",".join(fields),
            "minCitationCount": minCitationCount,
            "limit": 1_000, # max
            "year": year,
            "venue": venue
            }
        response = self.request(f"snippet/search", params)

        if response.status_code == 404:
            return None

        return response.json()

    def get_bulk_papers(
        self,
        query: str = None,
        venue: str = None,
        year: str = None,
        minCitationCount: int = None,
        maxCitationCount: int = None,
        fields: List[str] = None,
        limit: int = 1000,
        token: str = None,
        get_all: bool = False
    ) -> dict:
        """
        Get papers using bulk search endpoint for basic paper data without search relevance.

        Args:
            query: Optional text query with boolean logic support
            venue: Journal/venue name filter
            year: Year or year range (e.g., "2020" or "2020-2022")
            minCitationCount: Minimum citation count filter
            maxCitationCount: Maximum citation count filter
            fields: Paper fields to return (default: basic paper info)
            limit: Number of papers per request (max 1000)
            token: Continuation token for pagination
            get_all: If True, automatically fetch all pages using pagination

        Returns:
            Dict with 'data' (papers list), 'total' (if available), 'token' (for pagination)
        """
        if fields is None:
            fields = ["paperId", "title", "abstract", "year", "citationCount", "venue"]

        params = {
            "fields": ",".join(fields),
            "limit": min(limit, 1000)  # API max is 1000
        }

        # Add optional filters
        if query:
            params["query"] = query
        if venue:
            params["venue"] = venue
        if year:
            params["year"] = year
        if minCitationCount is not None:
            params["minCitationCount"] = minCitationCount
        if maxCitationCount is not None:
            params["maxCitationCount"] = maxCitationCount
        if token:
            params["token"] = token

        if get_all:
            return self._get_all_bulk_papers(params, fields)
        else:
            response = self.request("paper/search/bulk", params)
            if response.status_code == 404:
                return {"data": [], "total": 0, "token": None}
            return response.json()

    def _get_all_bulk_papers(self, base_params: dict, fields: List[str]) -> dict:
        """
        Helper method to fetch all pages of bulk search results.
        """
        all_papers = []
        total_requests = 0
        current_token = None

        print(f"📊 Starting bulk paper collection...")

        while True:
            # Update params with current token
            params = base_params.copy()
            if current_token:
                params["token"] = current_token

            response = self.request("paper/search/bulk", params)
            total_requests += 1

            if response.status_code == 404:
                break

            data = response.json()
            papers = data.get("data", [])

            if not papers:
                break

            all_papers.extend(papers)
            print(f"   Fetched {len(papers)} papers (total: {len(all_papers)})")

            # Check for continuation token
            current_token = data.get("token")
            if not current_token:
                break

        print(f"✅ Bulk collection complete: {len(all_papers)} papers in {total_requests} requests")

        return {
            "data": all_papers,
            "total": len(all_papers),
            "token": None,
            "requests_made": total_requests
        }

    def count_papers_in_venue(
        self,
        venue: str,
        year: str = None,
        minCitationCount: int = None
    ) -> dict:
        """
        Count total papers in a venue/year to understand dataset size.
        Results are cached persistently to avoid redundant API calls.

        Returns:
            Dict with 'total_papers', 'venue', 'year', 'cached', 'requests_made'
        """

        # Check persistent cache first
        cached_result = self._get_cached_venue_count(venue, year, minCitationCount)
        if cached_result:
            print(f"📊 Using cached count for {venue} ({year}): {cached_result['total_papers']:,} papers (cached {cached_result.get('cache_date', 'unknown')})")
            return cached_result

        print(f"📊 Counting papers in {venue} ({year})...")

        # Get count by fetching all papers
        result = self.get_bulk_papers(
            venue=venue,
            year=year,
            minCitationCount=minCitationCount,
            fields=["paperId"],  # Minimal fields for counting
            limit=1000,
            get_all=True
        )

        # Prepare result
        count_result = {
            "total_papers": result["total"],
            "venue": venue,
            "year": year,
            "min_citations": minCitationCount,
            "requests_made": result.get("requests_made", 1),
            "cached": False
        }

        # Save to persistent cache
        self._save_venue_count(
            venue=venue,
            year=year,
            min_citations=minCitationCount,
            total_papers=result["total"],
            requests_made=result.get("requests_made", 1)
        )

        # Also save to in-memory cache for this session
        cache_key = f"{venue}|{year}|{minCitationCount}"
        self._venue_count_cache[cache_key] = count_result

        print(f"💾 Cached venue count: {venue} ({year}) = {result['total']:,} papers")

        return count_result

    def clear_venue_cache(self, persistent: bool = False):
        """Clear the venue count cache"""
        self._venue_count_cache.clear()

        if persistent:
            try:
                with sqlite3.connect(self.cache_db_path) as conn:
                    conn.execute("DELETE FROM venue_counts")
                    conn.commit()
                print("🗑️ Persistent venue cache cleared")
            except Exception as e:
                print(f"⚠️  Warning: Could not clear persistent cache: {e}")
        else:
            print("🗑️ In-memory venue cache cleared")

    def list_cached_venues(self) -> pd.DataFrame:
        """List all cached venue counts"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                df = pd.read_sql_query("""
                    SELECT venue, year, min_citations, total_papers, requests_made,
                           created_at, updated_at
                    FROM venue_counts
                    ORDER BY updated_at DESC
                """, conn)
                return df
        except Exception as e:
            print(f"⚠️  Warning: Could not list cached venues: {e}")
            return pd.DataFrame()