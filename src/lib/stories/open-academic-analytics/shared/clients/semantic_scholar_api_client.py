import requests
import time
import pandas as pd
from typing import List, Dict, Optional

import logging

logger = logging.getLogger(__name__)

class SemanticScholarEmbeddings:
    """
    A class to retrieve paper embeddings from Semantic Scholar API using DOI identifiers.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the SemanticScholarEmbeddings client.
        
        Args:
            api_key (str, optional): Your Semantic Scholar API key for higher rate limits
        """
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.headers = {}
        if api_key:
            self.headers["x-api-key"] = api_key
        
        # Rate limiting: 1 request per second with API key, lower without
        # Batch requests are more efficient, so we can use shorter delays
        self.rate_limit_delay = 1.0 if api_key else 2.0
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Semantic Scholar API with error handling.
        
        Args:
            url (str): The API endpoint URL
            params (dict, optional): Query parameters
            
        Returns:
            dict: JSON response from the API
            
        Raises:
            Exception: If the API request fails
        """
        try:
            response = requests.get(url, params=params, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"Paper not found: {url}")
                return None
            elif response.status_code == 429:
                print("Rate limit exceeded. Waiting...")
                time.sleep(5)  # Wait 5 seconds before retrying
                return self._make_request(url, params)
            else:
                print(f"Request failed with status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
    
    def clean_doi(self, doi: str) -> str:
        """
        Clean DOI by removing common prefixes.
        
        Args:
            doi (str): Raw DOI string
            
        Returns:
            str: Cleaned DOI
        """
        # Remove common prefixes
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
    
    def get_papers_batch(self, dois: List[str], fields: List[str] = None, batch_size: int = 500) -> List[Dict]:
        """
        Retrieve multiple papers using the batch endpoint with DOI identifiers.
        
        Args:
            dois (list): List of DOI strings
            fields (list, optional): List of fields to retrieve
            batch_size (int): Number of papers per batch request (max 500)
            
        Returns:
            list: List of paper information dictionaries
        """
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
            # Show first few cleaned DOIs for verification
            if batch_num == 0 and len(cleaned_dois) > 0:
                print(f"Example cleaned DOI: {batch_dois[0]} -> {cleaned_dois[0]}")
            
            try:
                response = requests.post(
                    f"{self.base_url}/paper/batch",
                    params={"fields": ",".join(fields)},
                    json={"ids": doi_ids},
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    batch_results = response.json()
                    
                    # Add original DOI to each result for reference
                    for i, result in enumerate(batch_results):
                        if result is not None:  # Some papers might not be found
                            result["original_doi"] = batch_dois[i]
                    
                    all_results.extend(batch_results)
                    print(f"✓ Successfully retrieved {len([r for r in batch_results if r is not None])} papers from batch")
                    
                elif response.status_code == 429:
                    print("Rate limit exceeded. Waiting...")
                    time.sleep(10)  # Wait longer for batch requests
                    # Retry the same batch
                    continue
                else:
                    print(f"Batch request failed with status {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Request error for batch {batch_num + 1}: {e}")
            
            # Rate limiting between batches
            time.sleep(self.rate_limit_delay)
        
        return all_results
    
    def get_multiple_embeddings(self, dois: List[str], batch_size: int = 500) -> List[Dict]:
        """
        Get embeddings for multiple papers using their DOIs via batch API.
        
        Args:
            dois (list): List of DOI strings
            batch_size (int): Number of papers per batch request (max 500)
            
        Returns:
            list: List of dictionaries containing paper info and embeddings
        """
        print(f"Processing {len(dois)} DOIs using batch API...")
        
        # Get papers in batches
        all_papers = self.get_papers_batch(dois, fields=["paperId", "title", "embedding"], batch_size=batch_size)
        
        # Process results and extract embeddings
        results = []
        found_count = 0
        
        for paper in all_papers:
            if paper is not None and "embedding" in paper:
                embedding_data = {
                    "paperId": paper.get("paperId"),
                    "title": paper.get("title"),
                    "doi": paper.get("original_doi"),  # Use the original DOI we added
                    "embedding": paper["embedding"]["vector"] if paper["embedding"] else None
                }
                
                if embedding_data["embedding"] is not None:
                    results.append(embedding_data)
                    found_count += 1
                    if found_count % 50 == 0:  # Progress update every 50 successful embeddings
                        print(f"✓ Processed {found_count} embeddings so far...")
        
        print(f"\nFinal results:")
        print(f"✓ Successfully retrieved {len(results)} embeddings out of {len(dois)} DOIs")
        print(f"✗ {len(dois) - len(results)} DOIs failed or had no embeddings")
        
        return results
    
    def save_embeddings_to_parquet(self, embeddings: List[Dict], filename: str = "paper_embeddings.parquet"):
        """
        Save embeddings to a Parquet file for efficient storage and loading.
        
        Args:
            embeddings (list): List of embedding dictionaries
            filename (str): Output filename
        """
        try:
            if not embeddings:
                print("No embeddings to save")
                return
            
            # Prepare data for DataFrame
            data = []
            for emb in embeddings:
                if emb['embedding'] is not None:
                    row = {
                        'paper_id': emb['paperId'],
                        'title': emb['title'],
                        'doi': emb['doi'],
                        'embedding_dim': len(emb['embedding']),
                        'embedding': emb['embedding']  # Store as list/array
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
            print("Make sure you have pandas and pyarrow installed:")
            print("pip install pandas pyarrow")
