#!/usr/bin/env python3
"""
Query Testing Script for Data Availability Statements

Systematically test different query categories and venues to find optimal queries.
Run from CLI to avoid Dagster overhead.

Usage:
    python scripts/test_queries.py --category restrictions --venue "Nature" --years "2020-2022"
    python scripts/test_queries.py --all-categories --venue "PLOS ONE" --years "2018-2020"
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from shared.clients.semantic_scholar import SemanticScholarClient
from tabulate import tabulate
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# Query categories for systematic testing
QUERY_CATEGORIES = {
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
    'baseline-restrictions': [
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

def create_overlap_matrix(results, queries):
    """Create overlap matrix showing corpus ID overlaps between queries"""
    # Extract corpus IDs for each query
    query_corpus_ids = {}
    for query in queries:
        corpus_ids = set()
        if query in results and results[query]:
            for result in results[query]:
                if 'paper' in result and 'corpusId' in result['paper']:
                    corpus_ids.add(result['paper']['corpusId'])
        query_corpus_ids[query] = corpus_ids

    # Create overlap matrix
    matrix_data = []
    for query1 in queries:
        row = []
        for query2 in queries:
            if query1 == query2:
                # Diagonal: total unique papers for this query
                overlap = len(query_corpus_ids[query1])
            else:
                # Intersection between query1 and query2
                intersection = query_corpus_ids[query1] & query_corpus_ids[query2]
                overlap = len(intersection)
            row.append(overlap)
        matrix_data.append(row)

    # Create DataFrame for the matrix
    overlap_matrix = pd.DataFrame(matrix_data, index=queries, columns=queries)

    # Calculate exclusivity stats
    exclusivity_stats = {}
    for query in queries:
        unique_to_query = query_corpus_ids[query]
        for other_query in queries:
            if other_query != query:
                unique_to_query = unique_to_query - query_corpus_ids[other_query]

        total_papers = len(query_corpus_ids[query])
        unique_papers = len(unique_to_query)
        exclusivity_rate = unique_papers / total_papers if total_papers > 0 else 0

        exclusivity_stats[query] = {
            'total_papers': total_papers,
            'unique_papers': unique_papers,
            'exclusivity_rate': exclusivity_rate
        }

    return overlap_matrix, exclusivity_stats

def test_query_category(s2_client, category_name, queries, venue, years, min_citations=3):
    """Test all queries in a category and return results"""
    print(f"\n{'='*70}")
    print(f"TESTING CATEGORY: {category_name.upper()}")
    print(f"Venue: {venue} | Years: {years} | Min Citations: {min_citations}")
    print(f"{'='*70}")

    results = {}
    performance_log = []
    total_papers = 0

    for query in queries:
        print(f"Testing: {query:35}", end=" | ")

        try:
            snippet = s2_client.get_snippet(
                query=query,
                year=years,
                venue=venue,
                minCitationCount=min_citations,
            )

            hit_count = len(snippet.get('data', []))
            results[query] = snippet.get('data', [])
            total_papers += hit_count

            # Performance assessment
            status = "✅ GOOD" if hit_count > 10 else "⚠️  LOW" if hit_count > 0 else "❌ NONE"
            print(f"{hit_count:3d} hits | {status}")

            performance_log.append({
                'category': category_name,
                'query': query,
                'hits': hit_count,
                'venue': venue,
                'years': years,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            print(f"ERROR: {str(e)}")
            results[query] = []
            performance_log.append({
                'category': category_name,
                'query': query,
                'hits': 0,
                'venue': venue,
                'years': years,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })

    # Summary stats - note: total_papers here is sum of hits, not baseline papers
    successful_queries = sum(1 for q in queries if q in results and len(results[q]) > 0)
    avg_hits = total_papers / len(queries) if queries else 0

    print(f"\n📊 CATEGORY SUMMARY:")
    print(f"   Total queries: {len(queries)}")
    print(f"   Successful queries: {successful_queries}")
    print(f"   Total papers found: {total_papers}")
    print(f"   Average hits per query: {avg_hits:.1f}")
    print(f"   Success rate: {successful_queries}/{len(queries)} ({100*successful_queries/len(queries):.1f}%)")

    # Generate overlap matrix and exclusivity analysis
    if successful_queries > 1:  # Only if we have multiple successful queries
        print(f"\n📊 GENERATING OVERLAP MATRIX...")
        overlap_matrix, exclusivity_stats = create_overlap_matrix(results, queries)

        # Display overlap matrix
        print(f"\nQuery Overlap Matrix:")
        print(tabulate(overlap_matrix, headers=overlap_matrix.columns, tablefmt="grid"))

        # Display exclusivity stats
        print(f"\n🎯 QUERY EXCLUSIVITY ANALYSIS:")
        exclusivity_table = []
        for query, stats in exclusivity_stats.items():
            if stats['total_papers'] > 0:
                exclusivity_table.append([
                    query[:30] + "..." if len(query) > 30 else query,
                    stats['total_papers'],
                    stats['unique_papers'],
                    f"{stats['exclusivity_rate']:.1%}"
                ])

        headers = ['Query', 'Total Papers', 'Unique Papers', 'Exclusivity Rate']
        print(tabulate(exclusivity_table, headers=headers, tablefmt="grid"))

    else:
        overlap_matrix = None
        exclusivity_stats = {}

    return {
        'results': results,
        'performance': performance_log,
        'overlap_matrix': overlap_matrix.to_dict() if overlap_matrix is not None else None,
        'exclusivity_stats': exclusivity_stats,
        'summary': {
            'category': category_name,
            'venue': venue,
            'years': years,
            'total_queries': len(queries),
            'successful_queries': successful_queries,
            'total_papers': total_papers,
            'average_hits': avg_hits,
            'success_rate': successful_queries/len(queries) if queries else 0
        }
    }

def create_annotation_dataset_summary(all_results, baseline_count, categories_tested):
    """
    Create summary focused on building annotation dataset with maximum recall.
    Goal: Find queries that capture most data availability statements.
    """
    print(f"\n{'='*80}")
    print(f"📋 ANNOTATION DATASET SUMMARY")
    print(f"{'='*80}")

    total_papers = baseline_count['total_papers']
    venue = baseline_count['venue']
    years = baseline_count['year']

    print(f"📊 BASELINE CONTEXT:")
    print(f"   Venue: {venue} | Years: {years}")
    print(f"   Total papers in venue/period: {total_papers:,}")
    print(f"   Min citations: {baseline_count['min_citations']}")

    # Collect all successful queries across categories
    all_query_performance = []
    total_unique_papers = set()

    for category_name, result in all_results.items():
        if 'results' in result:
            for query, papers in result['results'].items():
                if papers:  # Only successful queries
                    # Extract corpus IDs
                    corpus_ids = set()
                    for paper in papers:
                        if 'paper' in paper and 'corpusId' in paper['paper']:
                            corpus_ids.add(paper['paper']['corpusId'])

                    hit_count = len(papers)
                    unique_papers = len(corpus_ids)
                    # Use baseline total papers for proper normalization
                    coverage_rate = (unique_papers / total_papers) * 100 if total_papers > 0 else 0

                    all_query_performance.append({
                        'category': category_name,
                        'query': query,
                        'hit_count': hit_count,
                        'unique_papers': unique_papers,
                        'coverage_rate': coverage_rate,
                        'corpus_ids': corpus_ids
                    })

                    total_unique_papers.update(corpus_ids)

    # Sort by coverage rate (recall proxy)
    all_query_performance.sort(key=lambda x: x['coverage_rate'], reverse=True)

    print(f"\n🎯 TOP QUERIES FOR ANNOTATION DATASET (normalized by total papers):")
    print(f"{'Rank':<4} {'Query':<35} {'Category':<12} {'Papers':<8} {'Hit Rate':<10} {'Potential'}")
    print(f"{'-'*4} {'-'*35} {'-'*12} {'-'*8} {'-'*10} {'-'*10}")

    for i, query_data in enumerate(all_query_performance[:15], 1):
        # Normalize by total papers in the venue/period
        hit_rate = query_data['coverage_rate']
        potential = "🟢 HIGH" if hit_rate > 1.0 else "🟡 MED" if hit_rate > 0.5 else "🔴 LOW"
        print(f"{i:<4} {query_data['query'][:34]:<35} {query_data['category']:<12} {query_data['unique_papers']:<8} {hit_rate:.3f}%{'':<5} {potential}")

    # Calculate optimal query combination for maximum coverage
    print(f"\n🔍 ANNOTATION DATASET OPTIMIZATION:")

    # Greedy approach: select queries that maximize unique coverage
    selected_queries = []
    covered_papers = set()
    remaining_queries = all_query_performance.copy()

    while remaining_queries and len(selected_queries) < 10:  # Max 10 queries
        # Find query that adds most new papers
        best_query = None
        best_new_coverage = 0

        for query_data in remaining_queries:
            new_papers = query_data['corpus_ids'] - covered_papers
            new_coverage = len(new_papers)

            if new_coverage > best_new_coverage:
                best_new_coverage = new_coverage
                best_query = query_data

        if best_query and best_new_coverage > 0:
            selected_queries.append(best_query)
            covered_papers.update(best_query['corpus_ids'])
            remaining_queries.remove(best_query)
        else:
            break

    total_coverage = (len(covered_papers) / total_papers) * 100 if total_papers > 0 else 0

    print(f"\n📈 RECOMMENDED QUERY SET ({len(selected_queries)} queries):")
    print(f"   Total unique papers captured: {len(covered_papers):,}")
    print(f"   Coverage of venue/period: {total_coverage:.2f}%")
    print(f"   Estimated annotation workload: {len(covered_papers):,} papers")

    print(f"\n📋 OPTIMAL QUERY LIST:")
    for i, query_data in enumerate(selected_queries, 1):
        print(f"   {i:2d}. {query_data['query']} ({query_data['unique_papers']} papers)")

    # Category performance summary
    print(f"\n📊 CATEGORY PERFORMANCE SUMMARY:")
    category_stats = {}
    for query_data in all_query_performance:
        cat = query_data['category']
        if cat not in category_stats:
            category_stats[cat] = {'queries': 0, 'total_papers': 0, 'avg_coverage': 0}

        category_stats[cat]['queries'] += 1
        category_stats[cat]['total_papers'] += query_data['unique_papers']

    for cat, stats in category_stats.items():
        avg_coverage = sum(q['coverage_rate'] for q in all_query_performance if q['category'] == cat) / stats['queries']
        print(f"   {cat:15}: {stats['queries']} queries, {stats['total_papers']:,} papers, {avg_coverage:.2f}% avg coverage")

    print(f"\n💡 ANNOTATION STRATEGY RECOMMENDATIONS:")
    print(f"   1. Use the {len(selected_queries)} recommended queries for maximum recall")
    print(f"   2. Expect ~{len(covered_papers):,} papers to annotate (mix of true/false positives)")
    print(f"   3. High-coverage queries likely contain more data availability statements")
    print(f"   4. Consider re-ranking/filtering to reduce false positives after initial collection")

    return {
        'baseline_papers': total_papers,
        'total_unique_captured': len(covered_papers),
        'coverage_rate': total_coverage,
        'recommended_queries': [q['query'] for q in selected_queries],
        'category_performance': category_stats
    }

def save_results(all_results, output_dir="results"):
    """Save results to JSON files for later analysis"""
    Path(output_dir).mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save full results
    with open(f"{output_dir}/query_test_results_{timestamp}.json", 'w') as f:
        json.dump(all_results, f, indent=2)

    # Save enhanced summary table with normalized metrics
    summaries = [result['summary'] for result in all_results.values()]
    summary_table = []
    normalized_table = []

    for category, result in all_results.items():
        summary = result['summary']
        baseline_papers = result.get('baseline_papers', summary.get('total_papers', 0))

        # Calculate normalized metrics
        avg_hit_rate = (summary['average_hits'] / baseline_papers * 100) if baseline_papers > 0 else 0
        total_unique_papers = 0

        # Count unique papers across all queries in this category
        if 'results' in result:
            unique_corpus_ids = set()
            for query, papers in result['results'].items():
                for paper in papers:
                    if 'paper' in paper and 'corpusId' in paper['paper']:
                        unique_corpus_ids.add(paper['paper']['corpusId'])
            total_unique_papers = len(unique_corpus_ids)

        coverage_rate = (total_unique_papers / baseline_papers * 100) if baseline_papers > 0 else 0

        # Raw metrics table
        summary_table.append([
            summary['category'],
            summary['venue'],
            summary['years'],
            summary['total_queries'],
            summary['successful_queries'],
            f"{summary['total_papers']:,}",  # Sum of hits
            f"{summary['average_hits']:.1f}",
            f"{summary['success_rate']:.1%}"
        ])

        # Normalized metrics table
        normalized_table.append([
            summary['category'],
            summary['venue'],
            summary['years'],
            f"{baseline_papers:,}",  # Actual baseline
            f"{total_unique_papers:,}",  # Unique papers found
            f"{coverage_rate:.3f}%",  # Coverage rate
            f"{avg_hit_rate:.3f}%",  # Avg hit rate
            f"{summary['success_rate']:.1%}"
        ])

    headers = ['Category', 'Venue', 'Years', 'Total Queries', 'Successful', 'Total Hits', 'Avg Hits', 'Success Rate']
    normalized_headers = ['Category', 'Venue', 'Years', 'Baseline Papers', 'Unique Found', 'Coverage Rate', 'Avg Hit Rate', 'Success Rate']

    with open(f"{output_dir}/summary_{timestamp}.txt", 'w') as f:
        f.write("QUERY TESTING SUMMARY\n")
        f.write("="*80 + "\n\n")

        f.write("RAW METRICS (Sum of Hits Across Queries)\n")
        f.write("-"*50 + "\n")
        f.write(tabulate(summary_table, headers=headers, tablefmt="grid"))

        f.write("\n\n")
        f.write("NORMALIZED METRICS (For Cross-Period/Journal Comparison)\n")
        f.write("-"*60 + "\n")
        f.write(tabulate(normalized_table, headers=normalized_headers, tablefmt="grid"))

        # Add overlap matrix if available
        overlap_matrix_data = None
        for result in all_results.values():
            if 'overlap_matrix' in result and result['overlap_matrix'] is not None:
                overlap_matrix_data = result['overlap_matrix']
                break

        if overlap_matrix_data:
            f.write("\n\n")
            f.write("QUERY OVERLAP MATRIX (Number of Shared Papers)\n")
            f.write("-"*55 + "\n")

            # Convert dict back to DataFrame for tabulate
            overlap_df = pd.DataFrame(overlap_matrix_data)
            f.write(tabulate(overlap_df, headers=overlap_df.columns, tablefmt="grid"))

            # Calculate normalized overlap rates for classifier insights
            f.write("\n\nNORMALIZED OVERLAP RATES (For Classifier Development)\n")
            f.write("-"*60 + "\n")

            baseline_papers = next(iter(all_results.values())).get('baseline_papers', 0)
            if baseline_papers > 0:
                overlap_rates = []
                queries = list(overlap_df.columns)

                for i, query1 in enumerate(queries):
                    row = []
                    for j, query2 in enumerate(queries):
                        if i == j:
                            # Diagonal: query coverage rate
                            coverage = (overlap_df.iloc[i, j] / baseline_papers) * 100
                            row.append(f"{coverage:.1f}%")
                        else:
                            # Off-diagonal: overlap as % of smaller query
                            shared = overlap_df.iloc[i, j]
                            query1_total = overlap_df.iloc[i, i]
                            query2_total = overlap_df.iloc[j, j]
                            smaller_total = min(query1_total, query2_total)
                            if smaller_total > 0:
                                overlap_rate = (shared / smaller_total) * 100
                                row.append(f"{overlap_rate:.1f}%")
                            else:
                                row.append("0.0%")
                    overlap_rates.append(row)

                normalized_df = pd.DataFrame(overlap_rates, index=queries, columns=queries)
                f.write(tabulate(normalized_df, headers=normalized_df.columns, tablefmt="grid"))

            f.write("\n\nCLASSIFIER DEVELOPMENT INSIGHTS:\n")
            f.write("- Diagonal: Query coverage rate (% of venue papers captured)\n")
            f.write("- Off-diagonal: Overlap rate (% of smaller query that overlaps)\n")
            f.write("- High diagonal = good recall potential for training data\n")
            f.write("- Low off-diagonal = query finds unique patterns (less redundant)\n")
            f.write("- Compare these rates across time periods for stable query selection\n")

        f.write("\n\n")
        f.write("EXPLANATION:\n")
        f.write("- Baseline Papers: Total papers in venue/period (from bulk search)\n")
        f.write("- Unique Found: Unique papers found across all queries (removes overlap)\n")
        f.write("- Coverage Rate: % of venue/period papers captured by this query category\n")
        f.write("- Avg Hit Rate: Average % hit rate per query in this category\n")
        f.write("- Use normalized metrics for temporal/cross-journal comparisons\n")
        f.write("\nCLASSIFIER DEVELOPMENT RECOMMENDATIONS:\n")
        f.write("1. Focus on queries with stable coverage rates across time periods\n")
        f.write("2. Select queries with high coverage (diagonal) but low redundancy (off-diagonal)\n")
        f.write("3. Prioritize queries that show consistent performance patterns\n")
        f.write("4. Use coverage rate trends to identify evolving vs. stable terminology\n")

    print(f"\n💾 Results saved to {output_dir}/")
    print(f"   - Full results: query_test_results_{timestamp}.json")
    print(f"   - Summary table: summary_{timestamp}.txt")

def main():
    parser = argparse.ArgumentParser(description="Test semantic scholar queries systematically")
    parser.add_argument("--category", choices=list(QUERY_CATEGORIES.keys()),
                       help="Query category to test")
    parser.add_argument("--all-categories", action="store_true",
                       help="Test all query categories")
    parser.add_argument("--venue", required=True,
                       help="Journal/venue name (e.g., 'Nature', 'PLOS ONE')")
    parser.add_argument("--years", required=True,
                       help="Year range (e.g., '2020-2022', '2018')")
    parser.add_argument("--min-citations", type=int, default=3,
                       help="Minimum citation count (default: 3)")
    parser.add_argument("--output-dir", default="results",
                       help="Output directory for results (default: results)")

    args = parser.parse_args()

    if not args.category and not args.all_categories:
        parser.error("Must specify either --category or --all-categories")

    # Initialize Semantic Scholar client
    print("🔍 Initializing Semantic Scholar client...")
    api_key = os.getenv('S2_API_KEY')  # Get API key from environment
    if api_key:
        print("✅ Using API key for higher rate limits")
    else:
        print("⚠️  No API key found - using lower rate limits")

    s2_client = SemanticScholarClient(api_key=api_key)
    
    all_results = {}

    # Test specified category or all categories
    categories_to_test = [args.category] if args.category else list(QUERY_CATEGORIES.keys())

    for category in categories_to_test:
        # category='baseline'
        # queries = QUERY_CATEGORIES[baseline]
        # years='2015-2017'
        # min_citations=3
        # venue='Synthese'
        queries = QUERY_CATEGORIES[category]
        result = test_query_category(
            s2_client, category, queries, args.venue, args.years, args.min_citations
        )
        all_results[category] = result

    # Get baseline paper count for context
    print(f"\n📊 GETTING BASELINE PAPER COUNT...")
    baseline_count = s2_client.count_papers_in_venue(
        venue=args.venue,
        year=args.years,
        minCitationCount=args.min_citations
    )

    # Generate comprehensive annotation dataset summary
    annotation_summary = create_annotation_dataset_summary(all_results, baseline_count, categories_to_test)

    # Add baseline count to results for proper comparison later
    for category in all_results:
        all_results[category]['baseline_papers'] = baseline_count['total_papers']
        all_results[category]['baseline_metadata'] = baseline_count

    # Save results with baseline info
    save_results(all_results, args.output_dir)

    print(f"\n🏁 TESTING COMPLETE")
    print(f"Tested {sum(len(QUERY_CATEGORIES[cat]) for cat in categories_to_test)} total queries")
    print(f"across {len(categories_to_test)} categories")

if __name__ == "__main__":
    main()