from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter()


class Professor(BaseModel):
    name: str
    department: str
    research_areas: List[str]
    publications_count: int


class ProfessorsFilter(BaseModel):
    research_area: Optional[str] = None
    department: Optional[str] = None
    min_publications: Optional[int] = None


@router.get("/profs", response_model=List[Professor])
async def get_professors(
    research_area: Optional[str] = Query(None, description="Filter by research area"),
    department: Optional[str] = Query(None, description="Filter by department"),
    min_publications: Optional[int] = Query(None, description="Minimum publication count")
):
    """
    Get professors data with optional filtering.

    This endpoint will eventually connect to the Dagster pipeline data.
    """
    # Mock data for now - will be replaced with actual data pipeline
    mock_profs = [
        Professor(
            name="Dr. Jane Smith",
            department="Computer Science",
            research_areas=["Machine Learning", "AI"],
            publications_count=45
        ),
        Professor(
            name="Dr. John Doe",
            department="Physics",
            research_areas=["Complex Systems", "Network Science"],
            publications_count=32
        )
    ]

    # Apply filters
    filtered_profs = mock_profs
    if research_area:
        filtered_profs = [p for p in filtered_profs if research_area.lower() in [ra.lower() for ra in p.research_areas]]
    if department:
        filtered_profs = [p for p in filtered_profs if department.lower() in p.department.lower()]
    if min_publications:
        filtered_profs = [p for p in filtered_profs if p.publications_count >= min_publications]

    return filtered_profs


@router.post("/profs", response_model=List[Professor])
async def get_professors_post(filters: ProfessorsFilter):
    """
    Get professors data with POST body filtering.

    Alternative endpoint for complex filtering via request body.
    """
    # Call the GET endpoint logic with the filter parameters
    return await get_professors(
        research_area=filters.research_area,
        department=filters.department,
        min_publications=filters.min_publications
    )


@router.get("/departments")
async def get_departments():
    """Get list of all departments."""
    return {
        "departments": [
            "Computer Science",
            "Physics",
            "Biology",
            "Mathematics",
            "Chemistry"
        ]
    }


@router.get("/research-areas")
async def get_research_areas():
    """Get list of all research areas."""
    return {
        "research_areas": [
            "Machine Learning",
            "AI",
            "Complex Systems",
            "Network Science",
            "Bioinformatics",
            "Data Science"
        ]
    }