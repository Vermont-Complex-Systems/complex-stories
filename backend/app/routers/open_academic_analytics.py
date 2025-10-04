from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from ..core.database import get_db_session

router = APIRouter()


# PostgreSQL-based endpoints for processed academic data

@router.get("/papers/{author_name}")
async def get_papers_for_author(
    author_name: str,
    filter_big_papers: bool = Query(False, description="Filter out papers with >25 coauthors"),
    limit: Optional[int] = Query(None, description="Limit number of results"),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Get processed papers data for a specific author.

    Replaces the loadPaperData function from the frontend.
    """
    try:
        from ..models.academic import Paper
        from sqlalchemy import select, and_

        # Build query with filters
        query = select(Paper).where(Paper.ego_display_name == author_name)

        # Apply coauthor filter
        if filter_big_papers:
            query = query.where(Paper.nb_coauthors < 25)

        # Order by publication date (most recent first)
        query = query.order_by(Paper.publication_date.desc())

        # Apply limit
        if limit:
            query = query.limit(limit)

        # Execute query
        result = await db.execute(query)
        papers = result.scalars().all()

        # Convert to dict format for JSON response - include ALL fields
        papers_data = []
        for paper in papers:
            paper_dict = {
                # Primary fields
                "id": paper.id,
                "ego_author_id": paper.ego_author_id,
                "ego_display_name": paper.ego_display_name,

                # Publication info
                "title": paper.title,
                "publication_year": paper.publication_year,
                "publication_date": paper.publication_date.isoformat() if paper.publication_date else None,
                "cited_by_count": paper.cited_by_count,
                "work_type": paper.work_type,
                "type": paper.work_type,  # Alias for frontend compatibility
                "language": paper.language,
                "doi": paper.doi,

                # Author-specific info
                "author_position": paper.author_position,
                "is_corresponding": paper.is_corresponding,

                # Publication details
                "is_open_access": paper.is_open_access,
                "landing_page_url": paper.landing_page_url,
                "pdf_url": paper.pdf_url,
                "license": paper.license,
                "journal_name": paper.journal_name,
                "source_type": paper.source_type,
                "oa_status": paper.oa_status,
                "oa_url": paper.oa_url,

                # Topic info
                "topic_id": paper.topic_id,
                "topic_name": paper.topic_name,
                "topic_score": paper.topic_score,

                # Biblio info
                "volume": paper.volume,
                "issue": paper.issue,
                "first_page": paper.first_page,
                "last_page": paper.last_page,

                # Metrics
                "fwci": paper.fwci,
                "has_fulltext": paper.has_fulltext,
                "fulltext_origin": paper.fulltext_origin,
                "is_retracted": paper.is_retracted,
                "countries_distinct_count": paper.countries_distinct_count,
                "institutions_distinct_count": paper.institutions_distinct_count,
                "locations_count": paper.locations_count,
                "referenced_works_count": paper.referenced_works_count,

                # Timestamps
                "updated_date": paper.updated_date.isoformat() if paper.updated_date else None,
                "created_date": paper.created_date.isoformat() if paper.created_date else None,

                # Collaboration metrics
                "nb_coauthors_raw": paper.nb_coauthors_raw,
                "nb_coauthors": paper.nb_coauthors,
                "coauthor_names": paper.coauthor_names,

                # Citation analysis
                "citation_percentile": paper.citation_percentile,
                "citation_category": paper.citation_category,

                # UMAP embeddings
                "umap_1": paper.umap_1,
                "umap_2": paper.umap_2,
                "abstract": paper.abstract,
                "s2FieldsOfStudy": paper.s2FieldsOfStudy,
                "fieldsOfStudy": paper.fieldsOfStudy,
            }
            papers_data.append(paper_dict)

        return {
            "author_name": author_name,
            "total_papers": len(papers_data),
            "filters_applied": {
                "filter_big_papers": filter_big_papers,
                "max_coauthors": 25 if filter_big_papers else None,
                "limit": limit
            },
            "papers": papers_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching papers: {str(e)}")


@router.get("/coauthors/{author_name}")
async def get_coauthors_for_author(
    author_name: str,
    filter_big_papers: bool = Query(False, description="Filter out papers with >25 coauthors"),
    limit: Optional[int] = Query(None, description="Limit number of results"),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Get processed coauthor data for a specific author.

    Replaces the loadCoauthorData function from the frontend.
    """
    try:
        from ..models.academic import Coauthor
        from sqlalchemy import select

        # Build query with filters
        query = select(Coauthor).where(Coauthor.ego_display_name == author_name)

        # Apply coauthor filter
        if filter_big_papers:
            query = query.where(Coauthor.nb_coauthors < 25)

        # Order by publication date (most recent first)
        query = query.order_by(Coauthor.publication_date.desc())

        # Apply limit
        if limit:
            query = query.limit(limit)

        # Execute query
        result = await db.execute(query)
        coauthors = result.scalars().all()

        # Convert to dict format for JSON response - include ALL fields
        coauthors_data = []
        for coauthor in coauthors:
            coauthor_dict = {
                # Primary key
                "id": coauthor.id,

                # UVM professor information
                "ego_author_id": coauthor.ego_author_id,
                "ego_display_name": coauthor.ego_display_name,
                "ego_department": coauthor.ego_department,
                "publication_year": coauthor.publication_year,
                "nb_coauthors": coauthor.nb_coauthors,

                # Publication info
                "publication_date": coauthor.publication_date.isoformat() if coauthor.publication_date else None,

                # Ego author information
                "ego_first_pub_year": coauthor.ego_first_pub_year,
                "ego_age": coauthor.ego_age,

                # Coauthor information
                "coauthor_id": coauthor.coauthor_id,
                "coauthor_display_name": coauthor.coauthor_display_name,
                "coauthor_age": coauthor.coauthor_age,
                "coauthor_first_pub_year": coauthor.coauthor_first_pub_year,

                # Age analysis
                "age_diff": coauthor.age_diff,
                "age_category": coauthor.age_category,

                # Collaboration metrics
                "yearly_collabo": coauthor.yearly_collabo,
                "all_times_collabo": coauthor.all_times_collabo,

                # Institution information
                "primary_institution": coauthor.primary_institution,
                "coauthor_institution": coauthor.coauthor_institution,
                "shared_institutions": coauthor.shared_institutions,
            }
            coauthors_data.append(coauthor_dict)

        return {
            "author_name": author_name,
            "total_coauthor_records": len(coauthors_data),
            "filters_applied": {
                "filter_big_papers": filter_big_papers,
                "max_coauthors": 25 if filter_big_papers else None,
                "limit": limit
            },
            "coauthors": coauthors_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching coauthors: {str(e)}")


# POST endpoints for Dagster to upload processed data
@router.post("/papers/bulk")
async def upload_papers_bulk(
    papers: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Bulk upload processed papers data from Dagster pipeline.
    """
    try:
        from ..models.academic import Paper
        from sqlalchemy import delete, text

        # Alternative approach: Use ON CONFLICT to handle duplicates
        from sqlalchemy.dialects.postgresql import insert

        # Insert papers with ON CONFLICT DO UPDATE (upsert)
        for paper_data in papers:
            stmt = insert(Paper).values(**paper_data)
            # Update all fields if conflict on primary key
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_={key: stmt.excluded[key] for key in paper_data.keys() if key != 'id'}
            )
            await db.execute(stmt)

        await db.commit()

        return {
            "status": "success",
            "papers_processed": len(papers),
            "message": f"Successfully processed {len(papers)} papers (inserted or updated)"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading papers: {str(e)}")


@router.post("/coauthors/bulk")
async def upload_coauthors_bulk(
    coauthors: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Bulk upload processed coauthor data from Dagster pipeline.
    """
    try:
        from ..models.academic import Coauthor
        from sqlalchemy import delete

        # Clear existing data
        await db.execute(delete(Coauthor))

        # Insert new coauthors
        coauthor_objects = []
        for coauthor_data in coauthors:
            coauthor = Coauthor(**coauthor_data)
            coauthor_objects.append(coauthor)

        if coauthor_objects:
            db.add_all(coauthor_objects)
            await db.commit()

        return {
            "status": "success",
            "coauthor_records_inserted": len(coauthor_objects),
            "message": f"Successfully uploaded {len(coauthor_objects)} coauthor records"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading coauthors: {str(e)}")