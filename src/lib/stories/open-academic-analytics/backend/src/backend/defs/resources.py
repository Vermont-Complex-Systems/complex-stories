from dagster_duckdb import DuckDBResource
import dagster as dg
import requests
from requests import Response
import time
from threading import Lock
from collections import deque
from typing import Optional


database_resource = DuckDBResource(database="/tmp/oa.duckdb")

from dagster_duckdb import DuckDBResource
import dagster as dg
import requests
from requests import Response
import time
from threading import Lock
from collections import deque
from typing import Optional, List, Dict


database_resource = DuckDBResource(database="/tmp/oa.duckdb")

class OpenAlexResource(dg.ConfigurableResource):
    email: str
    api_key: Optional[str] = None
    max_requests_per_second: int = 10
    max_requests_per_day: int = 100000
    
    def model_post_init(self, __context) -> None:
        """Initialize rate limiting attributes after Pydantic model initialization"""
        # Thread-safe rate limiting
        self._lock = Lock()
        self._request_times = deque()
        self._daily_request_count = 0
        self._daily_reset_time = time.time() + 86400  # 24 hours from now

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
                raise dg.DagsterExecutionError(
                    f"Daily rate limit of {self.max_requests_per_day} requests exceeded"
                )
            
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

    def request(self, endpoint: str, params: Optional[dict] = None) -> Response:
        """Make a rate-limited request to OpenAlex API"""
        self._check_rate_limits()
        
        # Prepare parameters
        if params is None:
            params = {}
        
        # Add email to get into the "polite pool"
        params["mailto"] = self.email
        
        # Add API key if provided (for premium users)
        if self.api_key:
            params["api_key"] = self.api_key
        
        # Make the request
        response = requests.get(
            f"https://api.openalex.org/{endpoint}",
            params=params,
            headers={"user-agent": "dagster-openalex-client"},
        )
        
        # Handle rate limit responses
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            dg.get_dagster_logger().warning(
                f"Rate limited by OpenAlex. Waiting {retry_after} seconds before retry."
            )
            time.sleep(retry_after)
            return self.request(endpoint, params)  # Retry once
        
        response.raise_for_status()
        return response

    def get_works(self, **params) -> dict:
        """Helper method to get works with common parameters"""
        return self.request("works", params).json()
    
    def get_all_works(self, **params) -> List[Dict]:
        """Get ALL works with automatic pagination"""
        all_works = []
        cursor = None
        page = 1
        
        dg.get_dagster_logger().info("Starting to fetch all works with pagination...")
        
        while True:
            current_params = params.copy()
            current_params["per_page"] = 200
            
            if cursor:
                current_params["cursor"] = cursor
            else:
                current_params["page"] = page
            
            response_data = self.request("works", current_params).json()
            works = response_data.get('results', [])
            
            if not works:
                dg.get_dagster_logger().info(f"No more works found. Total fetched: {len(all_works)}")
                break
                
            all_works.extend(works)
            
            # Check for next page
            meta = response_data.get('meta', {})
            next_cursor = meta.get('next_cursor')
            
            if next_cursor:
                cursor = next_cursor
                dg.get_dagster_logger().info(f"Fetched {len(all_works)} works so far, using cursor for next page...")
            else:
                # Check if we've got everything using count
                total_count = meta.get('count', 0)
                if total_count > 0 and len(all_works) >= total_count:
                    dg.get_dagster_logger().info(f"Fetched all {len(all_works)} works (total count: {total_count})")
                    break
                    
                # Try page-based pagination as fallback
                page += 1
                if page > 100:  # Safety limit to prevent infinite loops
                    dg.get_dagster_logger().warning(f"Reached page limit of 100, stopping at {len(all_works)} works")
                    break
                    
                dg.get_dagster_logger().info(f"Fetched {len(all_works)} works so far, moving to page {page}...")
        
        dg.get_dagster_logger().info(f"Total works fetched: {len(all_works)}")
        return all_works
    
    def get_authors(self, **params) -> dict:
        """Helper method to get authors with common parameters"""
        return self.request("authors", params).json()
    
    def get_institutions(self, **params) -> dict:
        """Helper method to get institutions with common parameters"""
        return self.request("institutions", params).json()


@dg.definitions
def resources():
    return dg.Definitions(
        resources={
            "duckdb": database_resource,
            "oa_client": OpenAlexResource(
                email="jonathanstonge7@gmail.com",
            ),
        }
    )