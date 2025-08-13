from dagster_duckdb import DuckDBResource
import dagster as dg
from typing import Optional

from backend.clients.semantic_scholar import SemanticScholarClient
from backend.clients.openalex import OpenAlexClient

database_resource = DuckDBResource(
    database="/tmp/oa.duckdb"
    )

class SemanticScholarResource(dg.ConfigurableResource):
    """Dagster resource for Semantic Scholar API access"""
    api_key: Optional[str] = None
    max_requests_per_second: int = 1
    max_requests_per_day: int = 5000
    base_url: str = "https://api.semanticscholar.org/graph/v1"
    
    def get_client(self) -> SemanticScholarClient:
        """Create and return a stateful client instance"""
        return SemanticScholarClient(
            api_key=self.api_key,
            max_requests_per_second=self.max_requests_per_second,
            max_requests_per_day=self.max_requests_per_day,
            base_url=self.base_url
        )

class OpenAlexResource(dg.ConfigurableResource):
    email: str
    api_key: Optional[str] = None
    max_requests_per_second: int = 10
    max_requests_per_day: int = 100000
    
    def get_client(self) -> OpenAlexClient:
        return SemanticScholarClient(
            api_key=self.api_key,
            max_requests_per_second=self.max_requests_per_second,
            max_requests_per_day=self.max_requests_per_day,
            base_url=self.base_url
        )
    
# Update your resources definition
@dg.definitions  
def resources():
    return dg.Definitions(
        resources={
            "duckdb": database_resource,
            "oa_client": OpenAlexResource(
                email="jonathanstonge7@gmail.com",
            ),
            "s2_client": SemanticScholarResource()
        }
    )

