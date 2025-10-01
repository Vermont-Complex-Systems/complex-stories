import dagster as dg
import requests
from typing import List, Dict, Any, Optional


class ComplexStoriesAPIResource(dg.ConfigurableResource):
    """Resource for connecting to Complex Stories FastAPI backend"""

    base_url: str = "http://localhost:8000"
    timeout: int = 30

    def get_academic_research_groups(
        self,
        limit: Optional[int] = None,
        department: Optional[str] = None,
        year: Optional[int] = None,
        inst_ipeds_id: Optional[int] = None,
        college: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get academic research groups data with optional filtering"""

        params = {}
        if limit is not None:
            params["limit"] = limit
        if department is not None:
            params["department"] = department
        if year is not None:
            params["year"] = year
        if inst_ipeds_id is not None:
            params["inst_ipeds_id"] = inst_ipeds_id
        if college is not None:
            params["college"] = college

        response = requests.get(
            f"{self.base_url}/datasets/academic-research-groups",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def get_academic_departments(
        self,
        college: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get academic department data with optional filtering"""

        params = {}
        if college is not None:
            params["college"] = college

        response = requests.get(
            f"{self.base_url}/datasets/academic-department",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def get_dataset_stats(self) -> Dict[str, Any]:
        """Get statistics about all datasets"""
        response = requests.get(
            f"{self.base_url}/datasets/stats",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()