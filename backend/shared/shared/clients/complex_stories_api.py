import requests
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class ComplexStoriesAPIClient:
    """Client for connecting to Complex Stories FastAPI backend"""

    def __init__(self, base_url: str = "https://api.complexstories.uvm.edu", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers using admin token from environment"""
        admin_token = os.getenv('FASTAPI_ADMIN_TOKEN')
        if not admin_token:
            raise Exception("FASTAPI_ADMIN_TOKEN environment variable not set")

        return {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }

    def get_academic_research_groups(
        self,
        inst_ipeds_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get academic research groups data with optional filtering"""

        params = {}
        if inst_ipeds_id is not None:
            params["inst_ipeds_id"] = inst_ipeds_id

        response = requests.get(
            f"{self.base_url}/datasets/academic-research-groups?format=parquet",
            params=params,
            timeout=self.timeout,
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

    def bulk_upload(self,
                   endpoint: str,
                   data: List[Dict[str, Any]],
                   batch_size: int = 10000,
                   timeout: int = 120) -> Dict[str, Any]:
        """Generic bulk upload method for any admin endpoint"""
        headers = self._get_auth_headers()
        total_uploaded = 0
        total_batches = (len(data) + batch_size - 1) // batch_size

        print(f"Starting bulk upload of {len(data)} records to {endpoint} in {total_batches} batches")

        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            batch_num = (i // batch_size) + 1

            response = requests.post(
                f"{self.base_url}/admin/{endpoint}",
                json=batch,
                headers=headers,
                timeout=timeout,
                verify=False
            )

            print(f"Batch {batch_num}/{total_batches}: Status {response.status_code}")
            if response.status_code != 200:
                print(f"Batch {batch_num} failed: {response.text[:1000]}")

            response.raise_for_status()
            total_uploaded += len(batch)

        print(f"Successfully uploaded {total_uploaded} records to {endpoint}")
        return {"records_uploaded": total_uploaded, "batches_processed": total_batches}