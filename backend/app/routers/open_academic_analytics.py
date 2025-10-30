from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from ..core.database import get_db_session
from ..routers.auth import get_admin_user
from ..models.auth import User
router = APIRouter()
admin_router = APIRouter()

@router.get("/papers/{author_name}")
async def get_papers_for_author(
    author_name: str,
    filter_big_papers: bool = Query(False, description="Filter out papers with >25 coauthors"),
    limit: Optional[int] = Query(None, description="Limit number of results"),
    db: AsyncSession = Depends(get_db_session)
) -> List[Dict[str, Any]]:
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

        return papers_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching papers: {str(e)}")

@router.get("/authors")
async def get_all_authors(
    ipeds_id: Optional[str] = Query(None, description="IPEDS ID to filter by institution (defaults to UVM)"),
    year: Optional[int] = Query(None, description="Year to filter faculty list (defaults to 2023)"),
    db: AsyncSession = Depends(get_db_session)
) -> List[Dict[str, Any]]:
    """
    Get all available authors with their current age, last publication year, and paper count.

    Supports filtering by institution (IPEDS ID) and faculty year for multi-tenant use.
    Currently defaults to UVM 2023 faculty list.
    """
    try:
        from ..models.academic import Coauthor
        from sqlalchemy import select, func

        # Set defaults for current UVM implementation
        # TODO: Extend data model to support multiple institutions and years
        effective_ipeds_id = ipeds_id or "uvm"  # Default to UVM
        effective_year = year or 2023  # Default to 2023

        # Query to get UVM faculty with their info (without expensive paper counts):
        # Fast query using just the coauthor table
        # Paper counts can be added later if needed via a separate endpoint

        query = select(
            Coauthor.ego_display_name,
            func.max(Coauthor.ego_age).label('current_age'),
            func.max(Coauthor.publication_year).label('last_pub_year')
        ).where(
            (Coauthor.ego_display_name.is_not(None)) &
            (Coauthor.ego_age.is_not(None))
            # TODO: Add institution and year filtering when data model supports it
            # & (Coauthor.institution_ipeds_id == effective_ipeds_id)
            # & (Coauthor.faculty_year == effective_year)
        ).group_by(
            Coauthor.ego_display_name
        ).order_by(
            Coauthor.ego_display_name
        )

        # Execute query
        result = await db.execute(query)
        authors_data = result.all()

        # Convert to list of dictionaries
        authors = []
        for row in authors_data:
            authors.append({
                "ego_display_name": row.ego_display_name,
                "current_age": row.current_age,
                "last_pub_year": row.last_pub_year
            })

        return authors

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching authors: {str(e)}")

@router.get("/coauthors/{author_name}")
async def get_coauthors_for_author(
    author_name: str,
    filter_big_papers: bool = Query(False, description="Filter out papers with >25 coauthors"),
    limit: Optional[int] = Query(None, description="Limit number of results"),
    db: AsyncSession = Depends(get_db_session)
) -> List[Dict[str, Any]]:
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

        return coauthors_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching coauthors: {str(e)}")

@router.get("/embeddings")
async def get_embeddings_data(db: AsyncSession = Depends(get_db_session)) -> List[Dict[str, Any]]:
    """
    Get processed embeddings data for research visualization.

    Returns papers with UMAP embeddings joined with training data from PostgreSQL database.
    """
    try:
            # Execute the complex SQL query using PostgreSQL
            query = text("""
                WITH exploded_depts AS (
                    SELECT
                        DISTINCT t.name,
                        t.oa_uid,
                        t.has_research_group,
                        trim(unnest(string_to_array(t.host_dept, ';'))) as host_dept,
                        t.perceived_as_male,
                        t.college,
                        t.group_url,
                        t.group_size
                    FROM training t
                    WHERE oa_uid IS NOT NULL
                )
                SELECT
                    p.doi,
                    p.id,
                    p.ego_author_id,
                    p.ego_display_name,
                    p.title,
                    p.publication_year,
                    p.publication_date,
                    TO_CHAR(p.publication_date, 'YYYY-MM-DD') as pub_date,
                    p.cited_by_count,
                    p.umap_1,
                    p.umap_2,
                    p.abstract,
                    p."s2FieldsOfStudy",
                    p."fieldsOfStudy",
                    p.coauthor_names,
                    e.host_dept,
                    e.college
                FROM papers p
                LEFT JOIN exploded_depts e ON (
                    p.ego_author_id = 'https://openalex.org/' || e.oa_uid OR
                    p.ego_author_id = e.oa_uid
                )
                WHERE p.umap_1 IS NOT NULL
                ORDER BY
                    CASE WHEN p.ego_author_id = 'https://openalex.org/A5040821463' THEN 0 ELSE 1 END,
                    RANDOM()
                LIMIT 6000
            """)

            result = await db.execute(query)
            rows = result.fetchall()

            # Convert to list of dictionaries
            embeddings_data = []
            for row in rows:
                embeddings_data.append({
                    "doi": row.doi,
                    "id": row.id,
                    "ego_author_id": row.ego_author_id,
                    "ego_display_name": row.ego_display_name,
                    "title": row.title,
                    "publication_year": row.publication_year,
                    "publication_date": row.publication_date.isoformat() if row.publication_date else None,
                    "pub_date": row.pub_date,
                    "cited_by_count": row.cited_by_count,
                    "umap_1": row.umap_1,
                    "umap_2": row.umap_2,
                    "abstract": row.abstract,
                    "s2FieldsOfStudy": row.s2FieldsOfStudy,
                    "fieldsOfStudy": row.fieldsOfStudy,
                    "coauthor_names": row.coauthor_names,
                    "host_dept": row.host_dept,
                    "college": row.college
                })

            return embeddings_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching embeddings data: {str(e)}")


# ================================
# Admin Operations
# ================================

@admin_router.post("/papers/bulk")
async def upload_papers_bulk(
    papers: List[Dict[str, Any]],
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Bulk upload processed papers data from Dagster pipeline.
    Uses efficient batch processing instead of individual inserts.
    """
    try:
        from ..models.academic import Paper
        from sqlalchemy.dialects.postgresql import insert
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Starting bulk upload of {len(papers)} papers")

        if not papers:
            return {"status": "success", "papers_processed": 0, "message": "No papers to process"}

        # Validate a sample record to check field compatibility
        sample_paper = papers[0]
        expected_fields = set(Paper.__table__.columns.keys())
        provided_fields = set(sample_paper.keys())

        # Log field differences for debugging
        missing_fields = expected_fields - provided_fields
        extra_fields = provided_fields - expected_fields

        if missing_fields:
            logger.warning(f"Missing fields in paper data: {missing_fields}")
        if extra_fields:
            logger.warning(f"Extra fields in paper data (will be ignored): {extra_fields}")

        # Filter paper data to only include valid fields
        filtered_papers = []
        for paper_data in papers:
            filtered_data = {k: v for k, v in paper_data.items() if k in expected_fields}
            filtered_papers.append(filtered_data)

        # Use efficient bulk insert with correct composite key
        try:
            stmt = insert(Paper)
            stmt = stmt.on_conflict_do_update(
                index_elements=['id', 'ego_author_id'],
                set_={col.name: stmt.excluded[col.name] for col in Paper.__table__.columns if col.name not in ['id', 'ego_author_id']}
            )

            # Execute bulk insert
            await db.execute(stmt, filtered_papers)
            await db.commit()
            successful_inserts = len(filtered_papers)

        except Exception as e:
            logger.error(f"Bulk insert failed: {str(e)}")
            await db.rollback()
            successful_inserts = 0

        logger.info(f"Successfully processed {successful_inserts}/{len(filtered_papers)} papers")

        return {
            "status": "success",
            "papers_processed": successful_inserts,
            "papers_received": len(papers),
            "papers_attempted": len(filtered_papers),
            "missing_fields": list(missing_fields) if missing_fields else [],
            "extra_fields": list(extra_fields) if extra_fields else [],
            "message": f"Successfully processed {successful_inserts}/{len(filtered_papers)} papers (inserted or updated)"
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"Error in bulk upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading papers: {str(e)}")


@admin_router.post("/coauthors/bulk")
async def upload_coauthors_bulk(
    coauthors: List[Dict[str, Any]],
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Bulk upload processed coauthor data from Dagster pipeline.
    """
    try:
        from ..models.academic import Coauthor
        from sqlalchemy.dialects.postgresql import insert

        # Use upsert approach instead of delete + insert to handle batching
        for coauthor_data in coauthors:
            stmt = insert(Coauthor).values(**coauthor_data)
            # Update all fields if conflict on primary key
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_={key: stmt.excluded[key] for key in coauthor_data.keys() if key != 'id'}
            )
            await db.execute(stmt)

        await db.commit()

        return {
            "status": "success",
            "coauthor_records_processed": len(coauthors),
            "message": f"Successfully processed {len(coauthors)} coauthor records (inserted or updated)"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading coauthors: {str(e)}")


@admin_router.post("/training/bulk")
async def upload_training_bulk(
    training_records: List[Dict[str, Any]],
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Bulk upload processed training data from Dagster pipeline.
    """
    try:
        from ..models.academic import Training
        from sqlalchemy.dialects.postgresql import insert

        # Use upsert approach with composite key
        for training_data in training_records:
            stmt = insert(Training).values(**training_data)
            # Update all fields if conflict on composite primary key (aid, pub_year)
            stmt = stmt.on_conflict_do_update(
                index_elements=['aid', 'pub_year'],
                set_={key: stmt.excluded[key] for key in training_data.keys() if key not in ['aid', 'pub_year']}
            )
            await db.execute(stmt)

        await db.commit()

        return {
            "status": "success",
            "training_processed": len(training_records),
            "message": f"Successfully processed {len(training_records)} training records (inserted or updated)"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading training data: {str(e)}")

