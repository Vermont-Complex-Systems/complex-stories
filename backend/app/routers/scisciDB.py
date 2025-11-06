from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy import text
from typing import List, Optional
import pandas as pd
from ..core.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from app.core.config import settings
from ..core.duckdb_client import get_duckdb_client

router = APIRouter()

@router.get("/field-year-counts")
async def get_field_year_counts(
    start_year: int = Query(default=2000, ge=1900, le=2030),
    end_year: int = Query(default=2024, ge=1900, le=2030)
) -> List[Dict[str, Any]]:
    """
    Query DuckLake directly.
    """

    client = get_duckdb_client()
    conn = client.connect()

    result = conn.execute(f"""
        SELECT
            year,
            list_filter(s2fieldsofstudy, x -> x.source = 's2-fos-model')[1].category as field,
            COUNT(*) as count
        FROM scisciDB.s2_papers
        WHERE s2fieldsofstudy IS NOT NULL
          AND (year >= {start_year}  AND year <= {end_year})
        GROUP BY year, field
        ORDER BY year DESC, count DESC
    """).fetchall()

    conn.close()

    return [{"year": r[0], "field": r[1], "count": r[2]} for r in result]

@router.get("/enrich-metadata")
async def enrich_metadata(
    dois: List[str] = Query(..., description="List of DOIs of interest for metadata enrichment")
) -> List[Dict[str, Any]]:
    """
    Enrich metadata from the smaller Postgres 'pg.works_meta' table using fields from
    the larger DuckLake 's2.works' table via DOI match.
    """

    # Normalize DOIs
    normalized_dois = [
        doi.lower().replace("https://doi.org/", "").strip()
        for doi in dois
    ]

    # Convert DOI list into a SQL-friendly VALUES clause
    dois_list = ', '.join(f"'{doi}'" for doi in normalized_dois)

    client = get_duckdb_client()
    conn = client.connect()

    # Step 1: Filter and normalize the small (Postgres) table
    conn.execute(f"""
        CREATE TEMP TABLE small_pg AS
        SELECT
            *,
            regexp_replace(lower(doi), '^https?://doi.org/', '') AS norm_doi
        FROM pg.papers
        WHERE regexp_replace(lower(doi), '^https?://doi.org/', '') IN ({dois_list});
    """)

    # Step 2: Enrich metadata with fields from the DuckLake table
    query = """
        SELECT
            pg.*,
            lake.corpusid,
            lake.externalids.DOI AS lake_doi,
            lake.title AS lake_title,
            lake.year AS lake_year,
            lake.citationcount AS lake_citations,
            lake.s2fieldsofstudy AS lake_fields
        FROM
            small_pg pg
        LEFT JOIN
            scisciDB.s2_papers lake
        ON
            regexp_replace(lower(lake.externalids.DOI), '^https?://doi.org/', '') = pg.norm_doi;
    """

    result = conn.execute(query).fetchall()
    columns = [col[0] for col in conn.description]

    conn.close()

    return [dict(zip(columns, row)) for row in result]
