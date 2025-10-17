"""
Enhanced paper processing asset combining SQL efficiency with pandas flexibility
"""
import dagster as dg
from dagster_duckdb import DuckDBResource
import numpy as np
from pathlib import Path
from backend.defs.resources import StaticDataPathResource


# Data filtering settings
ACCEPTED_WORK_TYPES = ['article', 'preprint', 'book-chapter', 'book', 'report']

FILTER_TITLE_PATTERNS = [
    "^Table", "Appendix", "Issue Cover", "This Week in Science",
    "^Figure ", "^Data for ", "^Author Correction: ", "supporting information",
    "^supplementary material", "^list of contributors"
]

def filter_no_title(df):
    """Remove papers without titles"""
    initial_count = len(df)
    df_filtered = df[~df.title.isna()]
    print(f"After removing papers without titles: {len(df_filtered)} papers ({initial_count - len(df_filtered)} removed)")
    return df_filtered

def deduplicate_papers(df):
    """Remove duplicate papers based on ego_author_id and title"""
    before_dedup = len(df)
    df_dedup = df[~df[['ego_author_id', 'title']].duplicated()]
    print(f"After deduplication: {len(df_dedup)} papers ({before_dedup - len(df_dedup)} duplicates removed)")
    return df_dedup

def filter_work_type(df):
    """Filter by accepted work types"""
    print(f"Filtering by work types: {ACCEPTED_WORK_TYPES}")
    before_work_filter = len(df)
    df_filtered = df[df.work_type.isin(ACCEPTED_WORK_TYPES)]
    print(f"After filtering by work type: {len(df_filtered)} papers ({before_work_filter - len(df_filtered)} filtered out)")
    return df_filtered

def filter_mislabeled_title(df):
    """Filter out mislabeled articles based on title patterns"""
    print("Filtering out mislabeled articles...")
    initial_count = len(df)
    df_filtered = df.copy()
    
    for pattern in FILTER_TITLE_PATTERNS:
        before_count = len(df_filtered)
        df_filtered = df_filtered[~df_filtered.title.str.contains(pattern, case=False, na=False)]
        filtered = before_count - len(df_filtered)
        if filtered > 0:
            print(f"  - Filtered {filtered} papers matching '{pattern}'")
    
    total_filtered = initial_count - len(df_filtered)
    print(f"  - Total mislabeled articles removed: {total_filtered}")
    return df_filtered

def calculate_number_authors(df):
    """Add column for number of coauthors"""
    print("Computing number of coauthors...")
    df_with_coauthors = df.copy()
    df_with_coauthors['nb_coauthors'] = df_with_coauthors.coauthor_names.apply(
        lambda x: len(x.split('; ')) if isinstance(x, str) and x.strip() else 0
    )
    return df_with_coauthors

def add_citation_percentiles(df):
    """Add citation percentiles for better scaling"""
    print("Computing citation percentiles...")
    df_with_percentiles = df.copy()
    
    citations = df_with_percentiles['cited_by_count'].fillna(0)
    df_with_percentiles['citation_percentile'] = citations.rank(pct=True) * 100
    
    # Also add categorical levels
    conditions = [
        citations == 0,
        (citations > 0) & (citations <= citations.quantile(0.5)),
        (citations > citations.quantile(0.5)) & (citations <= citations.quantile(0.8)),
        (citations > citations.quantile(0.8)) & (citations <= citations.quantile(0.95)),
        citations > citations.quantile(0.95)
    ]
    categories = ['uncited', 'low_impact', 'medium_impact', 'high_impact', 'very_high_impact']
    
    df_with_percentiles['citation_category'] = np.select(conditions, categories, default='uncited')
    return df_with_percentiles

def prepare_for_deduplication(df):
    """Sort by publication date and normalize titles for deduplication"""
    print("Preparing data for deduplication...")
    return (df
            .sort_values("publication_date", ascending=False)
            .reset_index(drop=True)
            .assign(title_normalized=lambda x: x.title.str.lower().str.strip())
           )

@dg.asset(
    kinds={"export"},
    deps=["uvm_publications", "umap_embeddings"],
)
def paper_parquet(duckdb: DuckDBResource, static_data_path: StaticDataPathResource) -> dg.MaterializeResult:
    """Export publications data as parquet for static frontend"""
    
    output_file = Path(static_data_path.get_path()) / "paper.parquet"
    
    print("🔍 Phase 1: SQL-based data extraction and joining...")
    
    with duckdb.get_connection() as conn:
        
        df_raw=conn.execute("""
        SELECT 
            a.author_id as ego_author_id,
            a.author_display_name as ego_display_name,
            
            -- Publication info
            p.id,
            p.title,
            p.publication_year,
            p.publication_date,
            p.cited_by_count,
            p.type as work_type,
            p.language,
            p.doi,
                            
            -- Author-specific info
            a.author_position,
            a.is_corresponding,
                                            
            -- Publication details
            p.primary_location.is_oa as is_open_access,
            p.primary_location.landing_page_url,
            p.primary_location.pdf_url,
            p.primary_location.license,
            p.primary_location.source.display_name as journal_name,
            p.primary_location.source.type as source_type,
                            
            p.open_access.oa_status,
            p.open_access.oa_url,
                            
            p.primary_topic.id as topic_id,
            p.primary_topic.display_name as topic_name,
            p.primary_topic.score as topic_score,
                            
            p.biblio.volume,
            p.biblio.issue,
            p.biblio.first_page,
            p.biblio.last_page,
                            
            p.fwci,
            p.has_fulltext,
            p.fulltext_origin,
            p.is_retracted,
            p.countries_distinct_count,
            p.institutions_distinct_count,
            p.locations_count,
            p.referenced_works_count,
                            
            p.updated_date,
            p.created_date,
                            
            -- Coauthor count (subquery)
            (SELECT COUNT(*) - 1, 
            FROM oa.raw.authorships a2 
            WHERE a2.work_id = p.id) as nb_coauthors_raw,
            -- Coauthor names (subquery) 
            (SELECT STRING_AGG(a3.author_display_name, '; ' ORDER BY a3.author_position)
            FROM oa.raw.authorships a3 
            WHERE a3.work_id = p.id AND a3.author_id != a.author_id) as coauthor_names,
            -- UMAP data
            u.umap_1, u.umap_2, u.abstract, u.s2FieldsOfStudy, u.fieldsOfStudy
        FROM oa.raw.publications p
        JOIN oa.raw.authorships a ON p.id = a.work_id
        LEFT JOIN oa.transform.umap_embeddings u ON p.doi = u.doi
        WHERE p.ego_author_id IS NOT NULL  -- Only UVM authors
        AND p.doi IS NOT NULL 
        AND p.title IS NOT NULL
        ORDER BY a.author_id DESC, p.publication_year
        """).df()

    
    # Apply pandas transformation pipeline
    df_processed = (df_raw
                    .pipe(filter_no_title)
                    .pipe(prepare_for_deduplication)
                    .pipe(lambda df: df.drop_duplicates(subset=['ego_author_id', 'title_normalized']))  # Use normalized title
                    .pipe(filter_work_type)
                    .pipe(filter_mislabeled_title)
                    .pipe(calculate_number_authors)
                    .pipe(add_citation_percentiles)
                   )
    
    # Clean up temporary columns
    if 'title_normalized' in df_processed.columns:
        df_processed = df_processed.drop('title_normalized', axis=1)
    
    print(f"📈 Processing pipeline complete: {len(df_processed)} final records")
    
    # Generate comprehensive statistics
    work_type_dist = df_processed.work_type.value_counts().to_dict()
    year_range = f"{int(df_processed.publication_year.min())}-{int(df_processed.publication_year.max())}"
    avg_coauthors = float(df_processed.nb_coauthors.mean()) if 'nb_coauthors' in df_processed.columns else 0
    unique_authors = int(df_processed.ego_author_id.nunique())
    
    citation_stats = {
        'median_citations': float(df_processed.cited_by_count.median()),
        'mean_citations': float(df_processed.cited_by_count.mean()),
        'max_citations': int(df_processed.cited_by_count.max()),
        'uncited_papers': int((df_processed.cited_by_count == 0).sum())
    }
    
    # UMAP embedding statistics
    final_umap_coverage = df_processed['umap_1'].notna().sum()
    umap_stats = {
        'papers_with_embeddings': int(final_umap_coverage),
        'embedding_coverage_percent': round(100 * final_umap_coverage / len(df_processed), 1),
        'umap_1_range': [float(df_processed['umap_1'].min()), float(df_processed['umap_1'].max())] if final_umap_coverage > 0 else [0, 0],
        'umap_2_range': [float(df_processed['umap_2'].min()), float(df_processed['umap_2'].max())] if final_umap_coverage > 0 else [0, 0]
    }
    
    # Save processed data
    df_processed.to_parquet(output_file, index=False)
    print(f"💾 Saved processed data to {output_file}")
    print(f"🗺️  Final UMAP coverage: {final_umap_coverage}/{len(df_processed)} papers ({umap_stats['embedding_coverage_percent']}%)")
    
    return dg.MaterializeResult(
        metadata={
            "papers_processed": len(df_processed),
            "unique_authors": unique_authors,
            "year_range": year_range,
            "work_type_distribution": work_type_dist,
            "avg_coauthors_per_paper": round(avg_coauthors, 2),
            "citation_statistics": citation_stats,
            "umap_embedding_stats": umap_stats,
            "processing_stages": {
                "sql_extraction": len(df_raw),
                "after_title_filter": "applied",
                "after_deduplication": "applied", 
                "after_work_type_filter": "applied",
                "after_mislabel_filter": "applied",
                "final_count": len(df_processed)
            },
            "output_file": str(output_file),
            "file_size_mb": round(output_file.stat().st_size / (1024*1024), 2) if output_file.exists() else 0,
            "configuration_used": {
                "accepted_work_types": ACCEPTED_WORK_TYPES,
                "filter_patterns_count": len(FILTER_TITLE_PATTERNS)
            }
        }
    )