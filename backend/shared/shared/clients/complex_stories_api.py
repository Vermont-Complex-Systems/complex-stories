import dagster as dg
import requests
from typing import List, Dict, Any, Optional
import pandas as pd

class ComplexStoriesAPIResource(dg.ConfigurableResource):
    """Resource for connecting to Complex Stories FastAPI backend"""

    base_url: str = "https://api.complexstories.uvm.edu"
    timeout: int = 30

    def get_academic_research_groups(
        self,
        inst_ipeds_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get academic research groups data with optional filtering"""

        params = {}
        if inst_ipeds_id is not None:
            params["inst_ipeds_id"] = inst_ipeds_id

        response = requests.get(
            f"{base_url}/datasets/academic-research-groups?format=parquet",
            params=params,
            timeout=timeout,
            verify=False
        )
        response.raise_for_status()
        return response

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