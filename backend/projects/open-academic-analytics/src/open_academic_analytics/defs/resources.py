from dagster_duckdb import DuckDBResource
import dagster as dg
from typing import Optional
import os

from shared.clients.semantic_scholar import SemanticScholarClient
from shared.clients.openalex import OpenAlexClient
from shared.clients.complex_stories_api import ComplexStoriesAPIResource

database_resource = DuckDBResource(
    database="/tmp/oa.duckdb"
)

class SemanticScholarResource(dg.ConfigurableResource):
    """https://www.semanticscholar.org/product/api"""
    api_key: Optional[str] = os.environ.get('S2')
    max_requests_per_second: int = 1
    max_requests_per_day: int = 100_000
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
    """https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication"""
    email: str
    max_requests_per_second: int = 10
    max_requests_per_day: int = 100_000
    base_url: str = "https://api.openalex.org"   # add base_url

    def get_client(self) -> OpenAlexClient:
        return OpenAlexClient(
            email=self.email,
            max_requests_per_second=self.max_requests_per_second,
            max_requests_per_day=self.max_requests_per_day,
            base_url=self.base_url,
        )

# class StaticDataPathResource(dg.ConfigurableResource):
#     """Resource for managing static data output paths"""
#     static_data_path: str = "../../../../../static/data"
    
#     def get_path(self) -> str:
#         return self.static_data_path

@dg.definitions  
def resources():
    return dg.Definitions(
        resources={
            "duckdb": database_resource,
            "oa_resource": OpenAlexResource(
                email="jonathanstonge7@gmail.com",
            ),
            "s2_resource": SemanticScholarResource(),
            "complex_stories_api": ComplexStoriesAPIResource()
            # "static_data_path": StaticDataPathResource()
        }
    )
