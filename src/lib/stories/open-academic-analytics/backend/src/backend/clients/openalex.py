"""
OpenAlex API Client
Standalone client for interacting with OpenAlex API with rate limiting.
"""

import requests
from requests import Response
import time
from threading import Lock
from collections import deque
from typing import Optional, List, Dict
import pandas as pd


class OpenAlexClient:
    def __init__(self, api_key: Optional[str] = None, max_requests_per_second: int = 1, email = "jonathanstonge7@gmail.com",
                 max_requests_per_day: int = 5000, base_url: str = "https://api.openalex.org"):
        self.api_key = api_key
        self.max_requests_per_second = max_requests_per_second
        self.max_requests_per_day = max_requests_per_day
        self.base_url = base_url
        self.email = email
        
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
        
        params["mailto"] = self.email

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

    def get_works(self, **params) -> dict:
        """Helper method to get works with common parameters"""
        return self.request("works", params).json()
    
    def get_authors(self, **params) -> dict:
        """Helper method to get authors with common parameters"""
        return self.request("authors", params).json()
    
    def get_institutions(self, **params) -> dict:
        """Helper method to get institutions with common parameters"""
        return self.request("institutions", params).json()
