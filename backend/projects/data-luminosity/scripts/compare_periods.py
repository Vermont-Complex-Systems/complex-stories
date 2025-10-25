#!/usr/bin/env python3
"""
Compare query performance across different time periods.

Analyzes trends in data availability statement prevalence over time by normalizing
hit rates against total papers per period.

Usage:
    python scripts/compare_periods.py --results-dir scripts/results/
    python scripts/compare_periods.py --files result1.json result2.json
"""

import argparse
import json
import pandas as pd
from pathlib import Path
from tabulate import tabulate
import matplotlib.pyplot as plt

def load_results(file_path):
    """Load results from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_summary_data(results):
    """Extract summary data from results"""
    summaries = []

    for category_name, category_data in results.items():
        if 'summary' in category_data:
            summary = category_data['summary']
            summaries.append({
                'category': category_name,
                'venue': summary.get('venue'),
                'years': summary.get('years'),
                'total_queries': summary.get('total_queries', 0),
                'successful_queries': summary.get('successful_queries', 0),
                'total_papers': summary.get('total_papers', 0),
                'average_hits': summary.get('average_hits', 0),
                'success_rate': summary.get('success_rate', 0)
            })

    return summaries

def extract_query_data(results):
    """Extract individual query performance data"""
    query_data = []

    for category_name, category_data in results.items():
        if 'results' in category_data:
            for query, papers in category_data['results'].items():
                hit_count = len(papers) if papers else 0

                # NOTE: summary 'total_papers' is sum of hits, not baseline!
                # We need the actual baseline from count_papers_in_venue
                baseline_papers = None

                # Try to find baseline in the results metadata
                # This would be added by the updated script that calls count_papers_in_venue
                if 'baseline_papers' in category_data:
                    baseline_papers = category_data['baseline_papers']

                # Fallback: estimate from context (not ideal)
                if baseline_papers is None:
                    print(f"⚠️  Warning: No baseline count found for {category_name}. Using estimated baseline.")
                    baseline_papers = 10000  # Conservative estimate

                hit_rate = (hit_count / baseline_papers) * 100 if baseline_papers > 0 else 0

                query_data.append({
                    'category': category_name,
                    'query': query,
                    'venue': category_data.get('summary', {}).get('venue', 'Unknown'),
                    'years': category_data.get('summary', {}).get('years', 'Unknown'),
                    'hit_count': hit_count,
                    'baseline_papers': baseline_papers,
                    'hit_rate': hit_rate
                })

    return query_data

def compare_time_periods(results_files):
    """Compare query performance across time periods"""

    print(f"\n{'='*80}")
    print(f"📅 TEMPORAL ANALYSIS: DATA AVAILABILITY STATEMENT TRENDS")
    print(f"{'='*80}")

    all_summaries = []
    all_query_data = []

    # Load all results
    for file_path in results_files:
        print(f"📂 Loading: {file_path}")
        results = load_results(file_path)

        summaries = extract_summary_data(results)
        query_data = extract_query_data(results)

        all_summaries.extend(summaries)
        all_query_data.extend(query_data)

    # Create summary comparison table
    summary_df = pd.DataFrame(all_summaries)

    if not summary_df.empty:
        print(f"\n📊 SUMMARY BY TIME PERIOD:")

        # Group by venue and years
        grouped = summary_df.groupby(['venue', 'years']).agg({
            'total_papers': 'sum',
            'average_hits': 'mean',
            'success_rate': 'mean'
        }).round(3)

        print(tabulate(grouped, headers=grouped.columns, tablefmt="grid"))

    # Create query-level comparison
    query_df = pd.DataFrame(all_query_data)

    if not query_df.empty:
        print(f"\n🔍 QUERY PERFORMANCE COMPARISON:")

        # Focus on common queries across time periods
        query_counts = query_df['query'].value_counts()
        common_queries = query_counts[query_counts > 1].index.tolist()

        if common_queries:
            print(f"Found {len(common_queries)} queries tested across multiple periods")

            # Create pivot table showing hit rates by query and time period
            pivot_data = []

            for query in common_queries[:10]:  # Top 10 common queries
                query_subset = query_df[query_df['query'] == query]

                for _, row in query_subset.iterrows():
                    pivot_data.append({
                        'Query': query[:30] + "..." if len(query) > 30 else query,
                        'Period': row['years'],
                        'Venue': row['venue'],
                        'Hit Count': row['hit_count'],
                        'Hit Rate (%)': round(row['hit_rate'], 3)
                    })

            pivot_df = pd.DataFrame(pivot_data)

            if not pivot_df.empty:
                # Show hit rate trends
                print(f"\n📈 HIT RATE TRENDS (normalized by total papers):")

                comparison_table = pivot_df.pivot_table(
                    index='Query',
                    columns='Period',
                    values='Hit Rate (%)',
                    aggfunc='mean'
                ).fillna(0)

                print(tabulate(comparison_table, headers=comparison_table.columns, tablefmt="grid"))

                # Calculate trend analysis
                print(f"\n📊 TREND ANALYSIS:")

                for query in comparison_table.index:
                    periods = comparison_table.columns.tolist()
                    rates = comparison_table.loc[query].tolist()

                    # Simple trend calculation
                    if len([r for r in rates if r > 0]) >= 2:
                        first_rate = next(r for r in rates if r > 0)
                        last_rate = rates[-1] if rates[-1] > 0 else rates[-2]

                        if last_rate > first_rate * 1.5:
                            trend = "📈 INCREASING"
                        elif last_rate < first_rate * 0.67:
                            trend = "📉 DECREASING"
                        else:
                            trend = "➡️  STABLE"

                        print(f"   {query[:40]:40} {trend} ({first_rate:.3f}% → {last_rate:.3f}%)")

    # Insights and recommendations
    print(f"\n💡 KEY INSIGHTS:")

    if not query_df.empty:
        # Calculate overall hit rate by period
        period_stats = query_df.groupby('years').agg({
            'hit_count': 'sum',
            'hit_rate': 'mean'
        }).round(3)

        print(f"   📅 Time Period Analysis:")
        for period, stats in period_stats.iterrows():
            print(f"      {period}: {stats['hit_rate']:.3f}% avg hit rate, {stats['hit_count']:,} total hits")

        # Find queries with biggest time-based changes
        if len(common_queries) > 0:
            print(f"\n   🔍 Most Dynamic Queries (changing over time):")

            query_variance = {}
            for query in common_queries:
                query_subset = query_df[query_df['query'] == query]
                if len(query_subset) > 1:
                    hit_rates = query_subset['hit_rate'].tolist()
                    variance = max(hit_rates) - min(hit_rates)
                    query_variance[query] = variance

            # Show top 5 most variable queries
            sorted_variance = sorted(query_variance.items(), key=lambda x: x[1], reverse=True)
            for query, variance in sorted_variance[:5]:
                print(f"      {query[:50]}: {variance:.3f}% range")

    print(f"\n   📋 Recommendations for Annotation Dataset:")
    print(f"      1. Consider temporal bias when comparing hit rates")
    print(f"      2. Use normalized hit rates (%) rather than raw counts")
    print(f"      3. Focus on queries that show consistent performance across periods")
    print(f"      4. Account for evolving data sharing practices in academic publishing")

def main():
    parser = argparse.ArgumentParser(description="Compare query performance across time periods")
    parser.add_argument("--results-dir", help="Directory containing result files")
    parser.add_argument("--files", nargs="+", help="Specific result files to compare")

    args = parser.parse_args()

    if args.results_dir:
        # Load all JSON files from directory
        results_dir = Path(args.results_dir)
        json_files = list(results_dir.glob("query_test_results_*.json"))

        if not json_files:
            print(f"❌ No result files found in {results_dir}")
            return

        print(f"📂 Found {len(json_files)} result files")
        compare_time_periods(json_files)

    elif args.files:
        # Load specific files
        file_paths = [Path(f) for f in args.files]
        compare_time_periods(file_paths)

    else:
        parser.error("Must specify either --results-dir or --files")

if __name__ == "__main__":
    main()