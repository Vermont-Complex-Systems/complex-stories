from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, List, Optional, Any
from ..core.query_utils import load_system, resolve_entity
from datetime import datetime, timedelta
from pydantic import BaseModel
import time
import asyncio
from urllib.parse import quote
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.database import get_mongo_client, get_db_session
from ..core.duckdb_client import get_duckdb_client
from ..core.parquet_utils import compute_partition_starts
from ..models.registry import Dataset, EntityMapping
from better_profanity import profanity

router = APIRouter()

WikimediaDataset = select(Dataset).where(Dataset.domain == "wikimedia")

class NgramResult(BaseModel):
    types: str
    counts: int
    probs: Optional[float] = None
    totalunique: Optional[int] = None

# ── mongoDB endpoints ────────────────────────────────────────────────

@router.get("/top-ngrams", response_model_exclude_unset=True)
async def get_top_ngrams(
    dates: str = Query("2024-10-10,2024-10-20", description="Date or comma-separated dates (ISO format)"),
    countries: str = Query("United States", description="Country or comma-separated countries"),
    topN: int = Query(10000, description="Number of ngrams to return"),
    include_probs: bool = Query(False, description="Include probability calculations"),
    include_totalunique: bool = Query(False, description="Include total unique count")
) -> Dict[str, List[NgramResult]]:
    """
    Get top N-grams for given dates and countries.
    Can compare multiple dates OR multiple countries, but not both simultaneously.
    """
    try:
        client = get_mongo_client()
        wikimedia_db = client.get_database("wikimedia")
        coll = wikimedia_db.get_collection("en_1grams")

        start_time = time.time()

        # Parse comma-separated inputs into arrays
        try:
            date_strings = [d.strip() for d in dates.split(",")]
            date_array = [datetime.fromisoformat(d.replace('Z', '+00:00')) for d in date_strings]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")

        country_array = [c.strip() for c in countries.split(",")]

        # Determine which dimension we're comparing
        comparing_dates = len(date_array) > 1
        comparing_countries = len(country_array) > 1

        if comparing_dates and comparing_countries:
            raise HTTPException(
                status_code=400,
                detail="Cannot compare both dates and countries simultaneously"
            )

        # Set up iteration: which dimension varies, which is fixed
        varying_dimension = date_array if comparing_dates else country_array
        fixed_date = date_array[0]
        fixed_country = country_array[0]

        results = {}

        # Execute queries for each dimension value
        def execute_mongo_query(item):
            date = item if comparing_dates else fixed_date
            country = item if comparing_countries else fixed_country

            # Execute the MongoDB query (synchronous)
            cursor = coll.find(
                {"date": date, "country": country}
            ).sort("pv_rank", 1).limit(topN)

            docs = list(cursor)
            key = date.isoformat() if comparing_dates else country
            return (key, docs)

        # Run MongoDB queries in thread pool for async compatibility
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(None, execute_mongo_query, item)
            for item in varying_dimension
        ]
        
        query_results = await asyncio.gather(*tasks)

        # Process results
        for key, docs in query_results:
            if not docs:
                continue
                
            # Extract pv_counts once upfront using list comprehension
            pv_counts = [
                int(doc["pv_count"]["$numberLong"]) if isinstance(doc.get("pv_count"), dict) 
                else int(doc.get("pv_count", 0))
                for doc in docs
            ]
            
            # Calculate aggregates only if needed
            total_count = sum(pv_counts) if include_probs else None
            total_unique = len(docs) if include_totalunique else None

            # Build results efficiently with list comprehension
            ngram_results = []
            for doc, pv_count in zip(docs, pv_counts):
                result_kwargs = {
                    "types": profanity.censor(str(doc.get("ngram", ""))),
                    "counts": pv_count
                }

                if include_probs and total_count and total_count > 0:
                    result_kwargs["probs"] = pv_count / total_count

                if include_totalunique:
                    result_kwargs["totalunique"] = total_unique

                ngram_results.append(NgramResult(**result_kwargs))

            results[key] = ngram_results
            
        # Log performance and payload info
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        mode = "dates" if comparing_dates else ("countries" if comparing_countries else "single")
        total_results = sum(len(result_list) for result_list in results.values())
        print(f"getTopNgrams query ({mode}) took {duration:.2f}ms (topN: {topN}, returned: {total_results} results)")

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search-term/{term}")
async def search_term(
    term: str,
    country: str = Query("United States", description="Country to search in"),
    date: Optional[str] = Query(None, description="Optional date filter (YYYY-MM-DD)")
):
    """
    Search for a specific ngram term.

    Args:
        term: The ngram term to search for
        country: Country to search in (default: "United States")
        date: Optional date filter in YYYY-MM-DD format. If provided, returns data for only that date.
              If omitted, returns all available dates for the term and country.

    Returns:
        Dictionary containing termData array and query duration
    """
    try:
        client = get_mongo_client()
        wikimedia_db = client.get_database("wikimedia")
        coll = wikimedia_db.get_collection("en_1grams")

        start_time = time.time()

        # Build query based on whether date is provided
        query = {
            "country": country,
            "ngram": term
        }

        # Add date filter if provided
        if date:
            try:
                parsed_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                query["date"] = parsed_date
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD: {e}")

        # Execute search query in thread pool
        def execute_search():
            cursor = coll.find(query).max_time_ms(25000)
            return list(cursor)

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, execute_search)

        if not results:
            raise HTTPException(status_code=404, detail="Search term not found")

        duration = (time.time() - start_time) * 1000
        print(f"searchTerm query took {duration:.2f}ms")

        # Clean up the results (convert ObjectId to string, handle special types)
        clean_results = []
        for doc in results:
            clean_doc = {}
            for key, value in doc.items():
                if key == "_id":
                    clean_doc[key] = str(value)
                elif isinstance(value, dict) and "$numberLong" in value:
                    clean_doc[key] = int(value["$numberLong"])
                elif isinstance(value, dict) and "$date" in value:
                    clean_doc[key] = value["$date"]
                else:
                    clean_doc[key] = value
            clean_results.append(clean_doc)

        return {
            "termData": clean_results,
            "duration": duration
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rank-divergence")
async def get_rank_divergence(
    country: str = Query(..., description="Country name"),
    date_delta: int = Query(..., description="Date delta for comparison"),
    alpha: float = Query(..., description="Alpha parameter"),
    date: str = Query(..., description="Date in ISO format (YYYY-MM-DD)"),
    topN: int = Query(10, ge=1, le=1000, description="Number of results to return")
):
    """Get rank divergence data"""
    try:
        client = get_mongo_client()
        wikimedia_db = client.get_database("wikimedia")
        coll = wikimedia_db.get_collection("en_1grams_rd")

        start_time = time.time()

        # Parse date
        try:
            parsed_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")

        # Execute rank divergence queries in thread pool
        def execute_rank_divergence():
            query = {
                "country": country,
                "date_delta": date_delta,
                "alpha": alpha,
                "date": parsed_date
            }

            return list(coll.find(query)
                        .sort("abs_divergence", -1)
                        .limit(topN))

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, execute_rank_divergence)

        duration = (time.time() - start_time) * 1000
        print(f"getRankDivergence query took {duration:.2f}ms")

        # Clean up the results (convert ObjectId to string, handle special types)
        clean_results = []
        for doc in results:
            clean_doc = {}
            for key, value in doc.items():
                if key == "_id":
                    clean_doc[key] = str(value)
                elif isinstance(value, dict) and "$numberLong" in value:
                    clean_doc[key] = int(value["$numberLong"])
                elif isinstance(value, dict) and "$date" in value:
                    clean_doc[key] = value["$date"]
                else:
                    clean_doc[key] = value
            clean_results.append(clean_doc)

        return {
            "results": clean_results,
            "duration": duration
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-ngrams2")
async def get_wikigrams_top_ngrams(
    dates: str = Query(default="2024-11-01,2024-11-07"),
    dates2: Optional[str] = Query(default=None),
    locations: str = Query(default="wikidata:Q30"),
    granularity: str = Query(default="daily"),
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """Get top Wikipedia n-grams with flexible comparative analysis.

    Supports single or dual date ranges, single location, and granularity selection.
    Replaces /datalakes/wikigrams/top-ngrams.
    """
    if granularity not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="granularity must be one of: daily, weekly, monthly")

    date_ranges = []
    dates_str1 = dates.split(',')
    if len(dates_str1) == 1:
        dates_str1.append(dates_str1[0])
    date_ranges.append(dates_str1)

    if dates2:
        dates_str2 = dates2.split(',')
        if len(dates_str2) == 1:
            dates_str2.append(dates_str2[0])
        date_ranges.append(dates_str2)

    location_list = [locations]

    query = WikimediaDataset.where(Dataset.dataset_id == "ngrams")
    result = await db.execute(query)
    dataset_obj = result.scalar_one_or_none()
    if not dataset_obj:
        raise HTTPException(status_code=404, detail="'ngrams' dataset not found")

    time_column = {"daily": "date", "weekly": "week", "monthly": "month"}[granularity]

    try:
        conn = get_duckdb_client().connect()

        results = {}
        queried_partitions_metadata = []

        for date_range in date_ranges:
            for location in location_list:
                em_result = await db.execute(
                    select(EntityMapping).where(
                        EntityMapping.domain == "wikimedia",
                        EntityMapping.dataset_id == "ngrams",
                        EntityMapping.entity_id == location,
                    )
                )
                em = em_result.scalar_one_or_none()
                if not em:
                    raise HTTPException(status_code=400, detail=f"Location '{location}' not found in entity mappings")
                encoded_country = quote(em.local_id, safe='')

                partition_starts = compute_partition_starts(date_range[0], date_range[1], granularity)
                queried_partitions_metadata.append({"date_range": date_range, "partitions": partition_starts})

                if len(date_ranges) > 1:
                    key = date_range[0] if date_range[0] == date_range[1] else f"{date_range[0]}_{date_range[1]}"
                elif len(location_list) > 1:
                    key = location.replace(":", "_").replace("-", "_")
                else:
                    key = "data"

                glob_path = f"{dataset_obj.data_location}/{granularity}/country={encoded_country}/{time_column}=*/data_0.parquet"

                rows = conn.execute(f"""
                    SELECT ngram, SUM(pv_count) as counts
                    FROM read_parquet('{glob_path}')
                    WHERE {time_column} BETWEEN ? AND ?
                    GROUP BY ngram
                    ORDER BY counts DESC
                    LIMIT ?
                """, [date_range[0], date_range[1], limit]).fetchall()

                formatted = [{"types": r[0], "counts": r[1]} for r in rows]

                if key == "data":
                    return {
                        "data": formatted,
                        "metadata": {"granularity": granularity, "time_column": time_column, "queried_partitions": partition_starts}
                    }
                else:
                    results[key] = formatted

        return {
            **results,
            "metadata": {"granularity": granularity, "time_column": time_column, "queries": queried_partitions_metadata}
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")


@router.get("/top-ngrams3")
async def get_wikigrams_top_ngrams3(
    dates: str = Query(default="2024-11-01,2024-11-07"),
    dates2: Optional[str] = Query(default=None),
    locations: str = Query(default="wikidata:Q30"),
    granularity: str = Query(default="daily"),
    limit: int = Query(default=100),
    db: AsyncSession = Depends(get_db_session),
):
    """Get top Wikipedia n-grams.

    Differences from /top-ngrams2:
    - Column names (ngram, pv_count) come from the registry, not hardcoded
    - No queried_partitions_metadata in the response
    - ~half the lines of code
    """
    query = WikimediaDataset.where(Dataset.dataset_id == "ngrams")
    result = await db.execute(query)
    dataset_obj = result.scalar_one_or_none()
    if not dataset_obj:
        raise HTTPException(status_code=404, detail="'ngrams' dataset not found")

    ep = dataset_obj.endpoint_schema or {}
    granularities = ep.get("granularities", {})
    if granularity not in granularities:
        raise HTTPException(
            status_code=400,
            detail=f"granularity must be one of {sorted(granularities)}",
        )

    em = await resolve_entity(db, "wikimedia", "ngrams", locations)

    def parse_dr(s: str) -> List[str]:
        parts = s.split(",")
        return [parts[0], parts[0]] if len(parts) == 1 else [parts[0], parts[1]]

    try:
        conn = get_duckdb_client().connect()
        dr1 = parse_dr(dates)
        sys1 = load_system(conn, dataset_obj, em.local_id, dr1, {}, granularity, limit)
        formatted1 = [{"types": t, "counts": c} for t, c in zip(sys1["types"], sys1["counts"])]

        if dates2:
            dr2 = parse_dr(dates2)
            sys2 = load_system(conn, dataset_obj, em.local_id, dr2, {}, granularity, limit)
            formatted2 = [{"types": t, "counts": c} for t, c in zip(sys2["types"], sys2["counts"])]
            key1 = dr1[0] if dr1[0] == dr1[1] else f"{dr1[0]}_{dr1[1]}"
            key2 = dr2[0] if dr2[0] == dr2[1] else f"{dr2[0]}_{dr2[1]}"
            return {
                key1: formatted1,
                key2: formatted2,
                "metadata": {"granularity": granularity, "location": locations},
            }

        return {
            "data": formatted1,
            "metadata": {"granularity": granularity, "location": locations},
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")


# ── DuckDB endpoints ────────────────────────────────────────────────

async def _get_revisions_path(db: AsyncSession) -> str:
    """Look up revisions data path from dataset registry."""
    query = WikimediaDataset.where(Dataset.dataset_id == "revisions")
    result = await db.execute(query)
    rev_dataset = result.scalar_one_or_none()
    if not rev_dataset:
        raise HTTPException(status_code=404, detail="'revisions' dataset not found")
    return rev_dataset.data_location


@router.get("/search-terms2")
async def search_terms_batch(
    types: str = Query(..., description="Comma-separated list of ngram terms"),
    date: Optional[str] = Query(None, description="First system focus date (YYYY-MM-DD)"),
    date2: Optional[str] = Query(None, description="Second system focus date (YYYY-MM-DD)"),
    location: str = Query("wikidata:Q30", description="First system location entity ID"),
    location2: Optional[str] = Query(None, description="Second system location entity ID (defaults to location)"),
    granularity: str = Query("daily", description="Granularity: daily, weekly, monthly"),
    window_size: int = Query(7, description="Number of granularity periods before/after each focus date"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Batch sparkline lookup for multiple ngram terms across one or two systems.

    Two comparison modes:
    - Temporal (date + date2, same location): ONE DuckDB scan — both windows' paths merged.
    - Geographic (date, location + location2): TWO DuckDB scans — paths live in separate geo dirs.

    Results are keyed as system1/system2 so the frontend can render both sides
    without coordinating parallel calls.
    """
    if granularity not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="granularity must be one of: daily, weekly, monthly")

    for d_str in [date, date2]:
        if d_str:
            try:
                datetime.fromisoformat(d_str)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD: {e}")

    terms = [t.strip() for t in types.split(",") if t.strip()]
    if not terms:
        raise HTTPException(status_code=400, detail="At least one term is required")

    systems_input: Dict[str, Dict] = {}
    if date:
        systems_input["system1"] = {"date": date, "location": location}
    if date2:
        systems_input["system2"] = {"date": date2, "location": location2 or location}
    if not systems_input:
        raise HTTPException(status_code=400, detail="At least one of date or date2 must be provided")

    query = WikimediaDataset.where(Dataset.dataset_id == "ngrams")
    result = await db.execute(query)
    dataset_obj = result.scalar_one_or_none()

    if not dataset_obj:
        raise HTTPException(status_code=404, detail="Wikigrams dataset not found")

    time_column = {"daily": "date", "weekly": "week", "monthly": "month"}[granularity]

    has_top_articles = granularity == "daily"

    try:
        duckdb_client = get_duckdb_client()
        conn = duckdb_client.connect()

        path_prefix_index: Dict[str, List[str]] = {}

        placeholders = ",".join(["?" for _ in terms])
        start_time = time.time()

        unique_locations = {s["location"] for s in systems_input.values()}
        geo_map: Dict[str, str] = {}
        t_adapter = time.time()
        for loc in unique_locations:
            em_result = await db.execute(
                select(EntityMapping).where(
                    EntityMapping.domain == "wikimedia",
                    EntityMapping.dataset_id == "ngrams",
                    EntityMapping.entity_id == loc,
                )
            )
            em = em_result.scalar_one_or_none()
            if not em:
                raise HTTPException(status_code=400, detail=f"Location '{loc}' not found in entity mappings")
            encoded_country = quote(em.local_id, safe='')
            geo_map[loc] = encoded_country
            glob_pat = f"{dataset_obj.data_location}/{granularity}/country={encoded_country}/{time_column}=*/data_0.parquet"
            for (p,) in conn.execute("SELECT * FROM glob(?)", [glob_pat]).fetchall():
                dir_path = p.rsplit("/", 1)[0]
                path_prefix_index.setdefault(dir_path, []).append(p)
        t_adapter_ms = (time.time() - t_adapter) * 1000

        window_unit_days = {"daily": 1, "weekly": 7, "monthly": 30}[granularity]
        effective_window = window_size * window_unit_days

        per_system: Dict[str, Dict] = {}
        t_filter = time.time()
        for sys_key, system in systems_input.items():
            loc = system["location"]
            local_geo = geo_map[loc]
            focus_date = datetime.fromisoformat(system["date"])
            w_start = (focus_date - timedelta(days=effective_window)).strftime("%Y-%m-%d")
            w_end = (focus_date + timedelta(days=effective_window)).strftime("%Y-%m-%d")
            window_partitions = compute_partition_starts(w_start, w_end, granularity)
            focus_partition = compute_partition_starts(system["date"], system["date"], granularity)[0]

            base = f"{dataset_obj.data_location}/{granularity}/country={local_geo}"
            query_paths = []
            for ps in window_partitions:
                query_paths.extend(path_prefix_index.get(f"{base}/{time_column}={ps}", []))

            if not query_paths:
                raise HTTPException(status_code=404, detail=f"No data found for {sys_key} ({system['date']}, {loc})")

            focus_paths = path_prefix_index.get(f"{base}/{time_column}={focus_partition}", [])

            per_system[sys_key] = {
                "loc": loc,
                "focus_date_str": system["date"],
                "window_partitions": window_partitions,
                "window_set": set(window_partitions),
                "focus_partition": focus_partition,
                "query_paths": query_paths,
                "focus_paths": focus_paths,
            }
        t_filter_ms = (time.time() - t_filter) * 1000

        all_geos = {geo_map[s["location"]] for s in systems_input.values()}
        temporal_comparison = len(systems_input) == 2 and len(all_geos) == 1
        total_paths = sum(len(v) for v in path_prefix_index.values())
        print(f"  setup: adapter+paths={t_adapter_ms:.0f}ms, filter={t_filter_ms:.0f}ms | total_paths={total_paths}")

        system_results: Dict[str, Dict] = {}

        if temporal_comparison:
            s1 = per_system["system1"]
            s2 = per_system["system2"]
            combined_paths = sorted(set(s1["query_paths"]) | set(s2["query_paths"]))
            range_start = min(s1["window_partitions"][0], s2["window_partitions"][0])
            range_end = max(s1["window_partitions"][-1], s2["window_partitions"][-1])

            spark_sql = f"""
                SELECT
                    w.ngram,
                    w.{time_column},
                    MIN(w.pv_rank) AS rank,
                    SUM(w.pv_count) AS counts
                FROM read_parquet(?) w
                WHERE w.{time_column} BETWEEN ? AND ?
                  AND w.ngram IN ({placeholders})
                GROUP BY w.ngram, w.{time_column}
                ORDER BY w.ngram, w.{time_column}
            """
            t_query = time.time()
            cursor = conn.execute(spark_sql, [combined_paths, range_start, range_end] + terms)
            t_spark_ms = (time.time() - t_query) * 1000

            rows = cursor.fetchall()
            cols = [desc[0] for desc in cursor.description]

            for sys_key, meta in per_system.items():
                system_results[sys_key] = {
                    "date": meta["focus_date_str"],
                    "location": meta["loc"],
                    "sparkData": {t: [] for t in terms},
                    "topArticles": {},
                }

            for row in rows:
                d = dict(zip(cols, row))
                term = d["ngram"]
                date_val = str(d[time_column])
                point = {time_column: d[time_column], "rank": d["rank"], "counts": d["counts"]}
                if date_val in s1["window_set"]:
                    system_results["system1"]["sparkData"][term].append(point)
                if date_val in s2["window_set"]:
                    system_results["system2"]["sparkData"][term].append(point)

            t_articles = time.time()
            if has_top_articles:
                focus_paths = sorted(set(s1["focus_paths"]) | set(s2["focus_paths"]))
                if focus_paths:
                    try:
                        art_cursor = conn.execute(f"""
                            SELECT
                                w.ngram,
                                ARG_MIN(w.top_articles, w.pv_rank) FILTER (WHERE w.{time_column} = ?) AS top_articles_s1,
                                ARG_MIN(w.top_articles, w.pv_rank) FILTER (WHERE w.{time_column} = ?) AS top_articles_s2
                            FROM read_parquet(?) w
                            WHERE w.ngram IN ({placeholders})
                            GROUP BY w.ngram
                        """, [s1["focus_partition"], s2["focus_partition"], focus_paths] + terms)
                        for row in art_cursor.fetchall():
                            d = dict(zip([c[0] for c in art_cursor.description], row))
                            if d.get("top_articles_s1") is not None:
                                system_results["system1"]["topArticles"][d["ngram"]] = d["top_articles_s1"]
                            if d.get("top_articles_s2") is not None:
                                system_results["system2"]["topArticles"][d["ngram"]] = d["top_articles_s2"]
                    except Exception:
                        pass
            t_articles_ms = (time.time() - t_articles) * 1000

            print(f"  temporal: {len(combined_paths)} paths, spark={t_spark_ms:.0f}ms, articles={t_articles_ms:.0f}ms ({len(s1['focus_paths'])+len(s2['focus_paths'])} focus files)")

        else:
            for sys_key, meta in per_system.items():
                query_paths = meta["query_paths"]

                t_query = time.time()
                cursor = conn.execute(f"""
                    SELECT
                        w.ngram,
                        w.{time_column},
                        MIN(w.pv_rank) AS rank,
                        SUM(w.pv_count) AS counts
                    FROM read_parquet(?) w
                    WHERE w.{time_column} BETWEEN ? AND ?
                      AND w.ngram IN ({placeholders})
                    GROUP BY w.ngram, w.{time_column}
                    ORDER BY w.ngram, w.{time_column}
                """, [query_paths, meta["window_partitions"][0], meta["window_partitions"][-1]] + terms)
                t_query_ms = (time.time() - t_query) * 1000

                rows = cursor.fetchall()
                cols = [desc[0] for desc in cursor.description]

                spark_data: Dict[str, List[Dict]] = {t: [] for t in terms}
                for row in rows:
                    d = dict(zip(cols, row))
                    spark_data[d["ngram"]].append({
                        time_column: d[time_column],
                        "rank": d["rank"],
                        "counts": d["counts"],
                    })

                top_articles: Dict[str, Any] = {}
                t_articles = time.time()
                if has_top_articles and meta["focus_paths"]:
                    try:
                        art_cursor = conn.execute(f"""
                            SELECT
                                w.ngram,
                                ARG_MIN(w.top_articles, w.pv_rank) AS top_articles
                            FROM read_parquet(?) w
                            WHERE w.{time_column} = ?
                              AND w.ngram IN ({placeholders})
                            GROUP BY w.ngram
                        """, [meta["focus_paths"], meta["focus_partition"]] + terms)
                        for row in art_cursor.fetchall():
                            d = dict(zip([c[0] for c in art_cursor.description], row))
                            if d.get("top_articles") is not None:
                                top_articles[d["ngram"]] = d["top_articles"]
                    except Exception:
                        pass
                t_articles_ms = (time.time() - t_articles) * 1000

                system_results[sys_key] = {
                    "date": meta["focus_date_str"],
                    "location": meta["loc"],
                    "sparkData": spark_data,
                    "topArticles": top_articles,
                }
                print(f"  {sys_key}: {len(query_paths)} paths, spark={t_query_ms:.0f}ms, articles={t_articles_ms:.0f}ms ({len(meta['focus_paths'])} focus files)")

        duration = (time.time() - start_time) * 1000
        print(f"searchTermsBatch total={duration:.2f}ms — {'temporal' if temporal_comparison else 'geographic'} for {len(terms)} terms × {len(systems_input)} systems")

        return {**system_results, "duration": duration}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")


@router.get("/revisions")
async def list_revision_articles(
    min_revisions: int = Query(default=1, description="Minimum revision count filter"),
    limit: int = Query(default=100, description="Max articles to return"),
    db: AsyncSession = Depends(get_db_session),
):
    """List articles with extracted revision histories."""
    try:
        query = WikimediaDataset.where(Dataset.dataset_id == "revisions")
        result = await db.execute(query)
        rev_dataset = result.scalar_one_or_none()
        if not rev_dataset:
            raise HTTPException(status_code=404, detail="'revisions' dataset not found")

        fc = rev_dataset.format_config or {}
        article_index = fc.get("partitioning", {}).get("article_index", [])
        if not article_index:
            raise HTTPException(status_code=500, detail="Missing article_index in format_config. Please re-register.")

        start_time = time.time()

        articles = [
            a for a in article_index
            if a["revision_count"] >= min_revisions
        ][:limit]

        duration = (time.time() - start_time) * 1000
        return {"articles": articles, "total": len(articles), "duration": duration}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/revisions/{identifier}")
async def get_revision_deltas(
    identifier: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Delta-encoded revision history for one article.

    Returns one entry per revision. The first revision (revision_idx=0) contains
    the full token map. Subsequent revisions contain only changed tokens
    (value 0 = token removed).
    """
    try:
        revisions_path = await _get_revisions_path(db)
        duckdb_client = get_duckdb_client()
        conn = duckdb_client.connect()

        start_time = time.time()

        rows = conn.execute(f"""
            WITH ordered AS (
                SELECT *,
                    ROW_NUMBER() OVER (ORDER BY revision_id::BIGINT) - 1 AS rev_seq,
                    json(ngram_counts)::MAP(VARCHAR, INTEGER) AS m
                FROM read_parquet('{revisions_path}/identifier={identifier}/*.parquet')
            ),
            curr AS (
                SELECT rev_seq,
                       unnest(map_keys(m)) AS token,
                       unnest(map_values(m)) AS curr_count
                FROM ordered
            ),
            prev AS (
                SELECT rev_seq + 1 AS rev_seq,
                       unnest(map_keys(m)) AS token,
                       unnest(map_values(m)) AS prev_count
                FROM ordered
            ),
            diffs AS (
                SELECT COALESCE(c.rev_seq, p.rev_seq) AS rev_seq,
                       COALESCE(c.token, p.token) AS token,
                       COALESCE(c.curr_count, 0) AS new_count
                FROM curr c
                FULL OUTER JOIN prev p
                    ON c.rev_seq = p.rev_seq AND c.token = p.token
                WHERE prev_count IS NULL
                   OR curr_count IS NULL
                   OR curr_count != prev_count
            ),
            delta_agg AS (
                SELECT rev_seq,
                       json_group_object(token, new_count) AS delta
                FROM diffs
                GROUP BY rev_seq
            )
            SELECT o.revision_id,
                   o.name,
                   o.date_modified,
                   o.revision_comment,
                   o.categories,
                   COALESCE(d.delta, '{{}}') AS token_diff
            FROM ordered o
            LEFT JOIN delta_agg d ON o.rev_seq = d.rev_seq
            ORDER BY o.rev_seq
        """).fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail=f"No revisions found for identifier {identifier}")

        duration = (time.time() - start_time) * 1000

        return {
            "revisions": [
                {
                    "revision_id": r[0],
                    "name": r[1],
                    "date_modified": r[2],
                    "revision_comment": r[3],
                    "categories": r[4],
                    "token_diff": r[5],
                }
                for r in rows
            ],
            "duration": duration,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
