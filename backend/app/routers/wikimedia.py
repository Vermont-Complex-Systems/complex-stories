from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import time
import asyncio
from ..core.database import get_mongo_client
from better_profanity import profanity

router = APIRouter()


class NgramResult(BaseModel):
    types: str
    counts: int
    probs: Optional[float] = None
    totalunique: Optional[int] = None


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
            # dates = "2025-06-23,2025-09-12"
            date_strings = [d.strip() for d in dates.split(",")]
            date_array = [datetime.fromisoformat(d.replace('Z', '+00:00')) for d in date_strings]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")

        # country_array = ["United States"]
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
            # topN=1_000_000
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

        # Process results with optimizations
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

            # Get top results (highest divergence)
            top_results = list(coll.find(query)
                             .sort("abs_divergence", -1)
                             .limit(topN))

            # Get bottom results (lowest divergence)
            bottom_results = list(coll.find(query)
                                .sort("abs_divergence", 1)
                                .limit(topN))

            return top_results + bottom_results

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
