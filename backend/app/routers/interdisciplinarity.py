from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert, func, and_, or_
from typing import Optional, Tuple
from datetime import datetime

from ..core.database import get_db_session
from ..models.interdisciplinarity import (
    PaperAnnotation,
    AnnotationRequest,
    AnnotationResponse,
    UserAnnotationsResponse
)
from ..models.cached_papers import CachedPaper
from ..models.auth import User
from ..routers.auth import get_current_user

router = APIRouter()
security = HTTPBearer(auto_error=False)  # Don't auto-error on missing token


# Dual auth dependency: accepts JWT token OR fingerprint
async def get_user_or_fingerprint(
    request: AnnotationRequest,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> Tuple[Optional[User], Optional[str]]:
    """
    Get user from JWT token if provided, else use fingerprint.

    Priority: user_id > fingerprint
    - If JWT token provided → return (User, None)
    - Else if fingerprint provided → return (None, fingerprint)
    - Else → raise error

    Returns:
        Tuple of (User | None, fingerprint | None)
    """
    if credentials:
        # User is logged in - prefer user_id
        try:
            user = await get_current_user(credentials, db)
            return (user, None)
        except HTTPException:
            # Invalid token - fall back to fingerprint if provided
            if request.fingerprint:
                return (None, request.fingerprint)
            raise

    elif request.fingerprint:
        # Anonymous user with fingerprint
        return (None, request.fingerprint)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either authentication token or fingerprint is required"
        )


@router.post("/interdisciplinarity/annotate", response_model=AnnotationResponse)
async def annotate_paper(
    request: AnnotationRequest,
    user_fingerprint: Tuple[Optional[User], Optional[str]] = Depends(get_user_or_fingerprint),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create or update an interdisciplinarity annotation for a paper.

    Supports dual auth:
    - Logged-in users: provide JWT token in Authorization header
    - Anonymous users: provide fingerprint in request body

    Users can change their mind - UPSERT logic allows updating existing annotations.
    """
    user, fingerprint = user_fingerprint

    # Verify paper exists by checking OpenAlex
    # We don't validate against local DB since papers come from OpenAlex API
    # The paper_id format should be W followed by digits (e.g., W2118557509)
    if not request.paper_id.startswith("W") or not request.paper_id[1:].isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OpenAlex paper ID format: {request.paper_id}. Expected format: W1234567"
        )

    # Check if annotation already exists
    if user:
        # Logged-in user - check by user_id
        existing_query = select(PaperAnnotation).where(
            and_(
                PaperAnnotation.paper_id == request.paper_id,
                PaperAnnotation.user_id == user.id
            )
        )
    else:
        # Anonymous user - check by fingerprint
        existing_query = select(PaperAnnotation).where(
            and_(
                PaperAnnotation.paper_id == request.paper_id,
                PaperAnnotation.fingerprint == fingerprint
            )
        )

    result = await db.execute(existing_query)
    existing_annotation = result.scalar_one_or_none()

    if existing_annotation:
        # UPDATE existing annotation (user changed their mind)
        existing_annotation.interdisciplinarity_rating = request.interdisciplinarity_rating
        existing_annotation.confidence = request.confidence
        existing_annotation.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(existing_annotation)
        return existing_annotation

    else:
        # INSERT new annotation
        new_annotation = PaperAnnotation(
            paper_id=request.paper_id,
            user_id=user.id if user else None,
            fingerprint=fingerprint,
            interdisciplinarity_rating=request.interdisciplinarity_rating,
            confidence=request.confidence
        )

        db.add(new_annotation)
        await db.commit()
        await db.refresh(new_annotation)
        return new_annotation


@router.get("/interdisciplinarity/papers/{paper_id}")
async def get_paper_by_id(
    paper_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get paper details by OpenAlex ID with caching.

    First checks local cache, then fetches from OpenAlex API if not cached.
    Caches the result for future requests.

    Args:
        paper_id: OpenAlex work ID (e.g., "W2118557509")

    Returns:
        Paper with id, title, year, abstract, authors, topics
    """
    import httpx

    # Validate paper ID format
    if not paper_id.startswith("W") or not paper_id[1:].isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OpenAlex paper ID format: {paper_id}"
        )

    # Check cache first
    cache_query = select(CachedPaper).where(CachedPaper.id == paper_id)
    result = await db.execute(cache_query)
    cached_paper = result.scalar_one_or_none()

    if cached_paper:
        # Return from cache
        return cached_paper.to_dict()

    # Not in cache - fetch from OpenAlex
    openalex_url = f"https://openalex.org/{paper_id}"
    base_url = "https://api.openalex.org/works"

    params = {
        "filter": f"openalex:{openalex_url}",
        "select": "id,title,publication_year,abstract_inverted_index,authorships,topics,doi,open_access"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            base_url,
            params=params,
            headers={"User-Agent": "mailto:complex-stories@uvm.edu"},
            timeout=15.0
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"OpenAlex API error: {response.status_code}"
            )

        data = response.json()

    results = data.get("results", [])
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper {paper_id} not found in OpenAlex"
        )

    work = results[0]

    # Reconstruct abstract from inverted index
    abstract = ""
    if work.get("abstract_inverted_index"):
        inverted_index = work["abstract_inverted_index"]
        # Reconstruct abstract by position
        words = {}
        for word, positions in inverted_index.items():
            for pos in positions:
                words[pos] = word
        # Sort by position and join
        abstract = " ".join([words[i] for i in sorted(words.keys())])

    # Extract author names
    authors = []
    for authorship in work.get("authorships", [])[:5]:  # Limit to first 5 authors
        if authorship.get("author"):
            authors.append(authorship["author"].get("display_name", "Unknown"))

    # Extract topics
    topics = []
    for topic in work.get("topics", [])[:3]:  # Top 3 topics
        topics.append({
            "id": topic.get("id", ""),
            "display_name": topic.get("display_name", ""),
            "score": topic.get("score", 0)
        })

    paper_data = {
        "id": paper_id,
        "title": work.get("title", "Untitled"),
        "year": work.get("publication_year"),
        "abstract": abstract,
        "authors": authors,
        "topics": topics,
        "doi": work.get("doi"),
        "is_open_access": work.get("open_access", {}).get("is_oa", False)
    }

    # Cache the paper
    cached = CachedPaper(**paper_data)
    db.add(cached)
    await db.commit()

    return paper_data


@router.get("/interdisciplinarity/my-annotations", response_model=UserAnnotationsResponse)
async def get_user_annotations(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    fingerprint: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get all annotations for the current user or fingerprint.

    Supports dual auth:
    - Logged-in users: provide JWT token in Authorization header
    - Anonymous users: provide fingerprint as query parameter
    """
    if credentials:
        # Logged-in user
        user = await get_current_user(credentials, db)
        query = select(PaperAnnotation).where(
            PaperAnnotation.user_id == user.id
        ).order_by(PaperAnnotation.created_at.desc())

    elif fingerprint:
        # Anonymous user
        query = select(PaperAnnotation).where(
            PaperAnnotation.fingerprint == fingerprint
        ).order_by(PaperAnnotation.created_at.desc())

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either authentication token or fingerprint is required"
        )

    result = await db.execute(query)
    annotations = result.scalars().all()

    return UserAnnotationsResponse(
        annotations=annotations,
        total=len(annotations)
    )


@router.get("/interdisciplinarity/stats")
async def get_annotation_stats(db: AsyncSession = Depends(get_db_session)):
    """
    Get aggregate statistics about annotations.

    Returns:
        - Total annotations
        - Annotations by logged-in users vs. anonymous
        - Average interdisciplinarity rating
        - Distribution of ratings
    """
    # Total annotations
    total_query = select(func.count(PaperAnnotation.id))
    total_result = await db.execute(total_query)
    total_annotations = total_result.scalar()

    # Logged-in vs. anonymous
    logged_in_query = select(func.count(PaperAnnotation.id)).where(
        PaperAnnotation.user_id.isnot(None)
    )
    logged_in_result = await db.execute(logged_in_query)
    logged_in_count = logged_in_result.scalar()

    anonymous_count = total_annotations - logged_in_count

    # Average rating
    avg_query = select(func.avg(PaperAnnotation.interdisciplinarity_rating))
    avg_result = await db.execute(avg_query)
    avg_rating = avg_result.scalar()

    # Rating distribution
    distribution_query = select(
        PaperAnnotation.interdisciplinarity_rating,
        func.count(PaperAnnotation.id)
    ).group_by(PaperAnnotation.interdisciplinarity_rating).order_by(
        PaperAnnotation.interdisciplinarity_rating
    )
    distribution_result = await db.execute(distribution_query)
    rating_distribution = {
        rating: count for rating, count in distribution_result.fetchall()
    }

    return {
        "total_annotations": total_annotations,
        "logged_in_annotations": logged_in_count,
        "anonymous_annotations": anonymous_count,
        "average_rating": float(avg_rating) if avg_rating else 0,
        "rating_distribution": rating_distribution
    }
