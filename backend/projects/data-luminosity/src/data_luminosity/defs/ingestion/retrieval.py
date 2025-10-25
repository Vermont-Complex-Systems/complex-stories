
"""
S2ORC dark data collection asset.

Processes S2ORC scientific papers to extract text paragraphs containing specific keywords
and loads them into MongoDB for annotation tasks.
"""
from textwrap import wrap
import dagster as dg
import numpy as np
from dagster_duckdb import DuckDBResource
from data_luminosity.defs.resources import SemanticScholarResource
import pandas as pd
from itertools import combinations
import matplotlib.pyplot as plt
from tabulate import tabulate

@dg.asset(
    kinds={"mongodb"}, 
    deps=["gscholar_venues"],
    group_name="ingestion"
)
def retrieval(
    duckdb: DuckDBResource, s2_resource: SemanticScholarResource
) -> dg.MaterializeResult:
    """Filter works_oa collection to get venues of interest and papers with s2orc_parsed=True"""


    with duckdb.get_connection() as conn: 
        # import duckdb
        # conn=duckdb.connect("~/data_luminosity.duckdb")
        df = conn.sql("SELECT * FROM raw.gscholar_venues").df()

    # s2_resource = SemanticScholarResource()
    s2_client = s2_resource.get_client()

    # Query categories for systematic testing
    query_categories = {
        'baseline': [
            'data',
            "data availability statement",
            "data available",
            "data available on reasonable request",
            "data accessibility",
            "data repository",
            "data cannot be shared",
            "data sharing",
            "all data underlying",
            "supplementary information data",
            "data deposited in repository",
            "datasets publicly available",
            "data archived",
            "data can be accessed",
        ],
        'restrictions': [
            "data not available",
            "data unavailable",
            "proprietary data",
            "ethical restrictions",
            "privacy constraints",
            "confidential data"
        ],
        'platforms': [
            "GitHub repository",
            "Zenodo",
            "Dryad repository",
            "figshare",
            "supplementary materials",
            "institutional repository"
        ],
        'domain_specific': [
            "patient privacy",
            "deidentified data",
            "survey data",
            "code available",
            "analysis scripts",
            "raw data files"
        ],
        'conditional': [
            "data will be made available",
            "available upon request",
            "following publication",
            "embargo period",
            "contact corresponding author",
            "reasonable request"
        ]
    }

    # Choose which category to test (can change this easily)
    active_category = 'baseline'  # Change this to test different categories
    top_10_queries = query_categories[active_category]

    jn, year_string = 'Synthese', '2015-2016'
    results = {(jn, year_string): {} }
    for query in top_10_queries:
        print(query)
        snippet = s2_client.get_snippet(
            query = query,
            year = year_string,
            venue = jn,
            minCitationCount = 3,
        )
        
        if len(snippet) > 0:
            results[(jn, year_string)][query] = snippet['data']
        else:
            results[(jn, year_string)][query] = [] 

    
    # Query performance tracking
    def track_query_performance():
        performance_log = []
        total_papers = 0

        print(f"\n{'='*60}")
        print(f"QUERY PERFORMANCE REPORT - {active_category.upper()} CATEGORY")
        print(f"Venue: {jn} | Years: {year_string}")
        print(f"{'='*60}")

        for query in top_10_queries:
            if query in results[(jn, year_string)]:
                hit_count = len(results[(jn, year_string)][query])
                performance_log.append({
                    'category': active_category,
                    'query': query,
                    'hits': hit_count,
                    'venue': jn,
                    'years': year_string
                })
                total_papers += hit_count
                status = "✅ GOOD" if hit_count > 10 else "⚠️  LOW" if hit_count > 0 else "❌ NONE"
                print(f"{query:35} | {hit_count:3d} hits | {status}")
            else:
                print(f"{query:35} | {0:3d} hits | ❌ NONE")

        print(f"\n📊 SUMMARY:")
        print(f"   Total queries tested: {len(top_10_queries)}")
        print(f"   Total papers found: {total_papers}")
        print(f"   Average per query: {total_papers/len(top_10_queries):.1f}")
        print(f"   Success rate: {sum(1 for q in top_10_queries if q in results[(jn, year_string)] and len(results[(jn, year_string)][q]) > 0)}/{len(top_10_queries)}")

        return performance_log

    performance_data = track_query_performance()
    

    def extract_intersecting_corpusid():
        """Extract corpus IDs for each query and create overlap matrix"""
        # First, extract all corpus IDs for each query
        query_corpus_ids = {}
        for query in top_10_queries:
            corpus_ids = set()
            if query in results[(jn, year_string)] and results[(jn, year_string)][query]:
                for result in results[(jn, year_string)][query]:
                    if 'paper' in result and 'corpusId' in result['paper']:
                        corpus_ids.add(result['paper']['corpusId'])
            query_corpus_ids[query] = corpus_ids
            print(f"{query}: {len(corpus_ids)} unique papers")

        # Create pairwise intersection matrix
        overlap_data = []
        for comb in combinations(top_10_queries, 2):
            query1, query2 = comb
            set_query1 = query_corpus_ids[query1]
            set_query2 = query_corpus_ids[query2]
            intersection_corpusid = set_query1 & set_query2
            overlap_data.append((query1, query2, len(intersection_corpusid), len(set_query1), len(set_query2)))

        # Create full matrix (including diagonal)
        matrix_data = []
        for query1 in top_10_queries:
            row = []
            for query2 in top_10_queries:
                if query1 == query2:
                    # Diagonal: total unique papers for this query
                    overlap = len(query_corpus_ids[query1])
                else:
                    # Find intersection between query1 and query2
                    intersection = query_corpus_ids[query1] & query_corpus_ids[query2]
                    overlap = len(intersection)
                row.append(overlap)
            matrix_data.append(row)

        # Create DataFrame for the matrix
        overlap_matrix = pd.DataFrame(matrix_data, index=top_10_queries, columns=top_10_queries)

        return overlap_matrix, overlap_data

    def print_top10(x):
        results[(jn, year_string)][x] = sorted(results[(jn, year_string)][x], key = lambda x: x['score'], reverse=True)

        for res in results[(jn, year_string)][x]:
            text = res['snippet']['text']
            score = res['score']

            print(f"Score: {score}")
            print(f"==============")
            print('\n'.join(wrap(text.replace("data", "**data**"))), end="\n\n")
            
    # Visualize the overlap matrix
    overlap_matrix, overlap_data = extract_intersecting_corpusid()
    print("\nQuery Overlap Matrix:")
    print(tabulate(overlap_matrix, headers=overlap_matrix.columns, tablefmt="grid"))

    # # Create heatmap visualization
    # plt.figure(figsize=(12, 10))
    # plt.imshow(overlap_matrix.values, cmap='Blues', interpolation='nearest')
    # plt.colorbar(label='Number of overlapping papers')
    # plt.title('Query Overlap Matrix')
    # plt.xticks(range(len(top_10_queries)), [q[:20] + '...' if len(q) > 20 else q for q in top_10_queries], rotation=45, ha='right')
    # plt.yticks(range(len(top_10_queries)), [q[:20] + '...' if len(q) > 20 else q for q in top_10_queries])
    # plt.tight_layout()
    # plt.show()
