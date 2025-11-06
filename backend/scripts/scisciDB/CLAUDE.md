# Summary: Building a Research Data Pipeline with DuckLake

## Context
We designed a data pipeline for large-scale academic datasets (S2ORC from Semantic Scholar, ~50GB+ of papers with full text). The goal was to enable fast analytical queries while maintaining update compatibility with upstream data sources.

## Key Architecture Decisions

1. DuckLake vs Vanilla DuckDB vs MongoDB

Chose DuckLake for incremental updates and version tracking
Why: S2ORC releases monthly updates (inserts, updates, deletes). DuckLake provides:

Version control (snapshots, time travel)
Schema evolution
Change tracking
ACID transactions
Metadata stored in PostgreSQL, data in Parquet files



2. Storage Strategy

Keep data on network mount (`/netfiles/compethicslab/`, 4.3TB available)
Local disk (95GB) only for code, PostgreSQL metadata, temp files
Set DuckDB temp directory to network storage: `SET temp_directory='/netfiles/.../duckdb_temp/'`

3. File Format: Parquet with Partitioning

Convert JSON → Parquet (3-5x compression)
Partition by year for query performance: `PARTITION_BY year`
DuckDB automatically prunes partitions (skip irrelevant years)
Keep ~30 files per dataset (200MB each) - sweet spot for parallel processing

4. Handle Nested JSON Fields
Critical decision: S2ORC ships nested structures as VARCHAR (for bandwidth), but you should convert to STRUCT locally:

```python
# Convert during parse step (do ONCE)
CAST(body.annotations.section_header AS JSON) as section_headers
```

**Why**: 
- 10-100x faster queries (no JSON parsing overhead)
- Parquet compresses structs better than strings
- Columnar access to nested fields
- Allen AI uses VARCHAR for distribution; you use STRUCT for storage

### 5. **Principled Data Processing Pipeline**
Following Patrick Ball's methodology:
```
scripts/s2orc/
├── input/          # Raw downloads (JSON.GZ from Semantic Scholar API)
│   └── download.py
├── import/         # Parse & validate (JSON → Parquet with structs)
│   ├── parse.py
│   └── validate.py
├── enrich/         # Add derived fields (like primary_s2field)
│   └── add_fields.py
├── export/         # Load to DuckLake
│   └── update_ducklake.py
└── Makefile        # Orchestrates: make all DATASET=papers
```

Each step is:

Auditable: Clear input → output
Reproducible: Makefile documents process
Testable: Validate before export
Versioned: Frozen snapshots for reproducibility

## Key Technical Patterns
Parse JSON to Parquet with DuckDB

```python
# Efficient conversion (streaming, no memory issues)
duckdb.execute(f"""
    COPY (SELECT * FROM read_json_auto('{input_file}'))
    TO '{output_file}' (FORMAT PARQUET, COMPRESSION 'zstd')
""")
```

Query Parquet Files Directly

```sql
-- Use VIEWs instead of TABLEs (no data duplication)
CREATE VIEW papers AS 
SELECT * FROM read_parquet('/path/to/papers/**/*.parquet');

-- Partition pruning happens automatically
SELECT * FROM papers WHERE year = 2023;  -- Only reads year=2023/ folder
```

Incremental Updates with DuckLake

```sql 
-- Monthly S2ORC update workflow
ATTACH 'ducklake:postgres:dbname=complex_stories ...' AS s2 (...);
USE s2;

-- Insert new papers
INSERT INTO papers SELECT * FROM read_parquet('new_release/*.parquet')
WHERE corpusid NOT IN (SELECT corpusid FROM papers);

-- Update existing
UPDATE papers SET ... FROM read_parquet('updates/*.parquet') WHERE ...;

-- DuckLake creates new snapshot automatically
-- Query historical: SELECT * FROM papers AT (VERSION => 2);
```

## FastAPI Integration: Two Approaches
Approach 1: DuckDB Client in FastAPI

```python
# Direct DuckDB connection for analytical queries
import duckdb
conn = duckdb.connect('/path/to/research.duckdb', read_only=True)

@app.get("/papers/author/{author_id}")
def get_author_papers(author_id: str):
    result = conn.execute("""
        SELECT corpusid, title FROM papers
        WHERE list_contains(list_transform(authors, a -> a.authorid), ?)
    """, [author_id]).fetchdf()
    return result.to_dict('records')
```

Approach 2: pg_duckdb (Recommended)
PostgreSQL extension that runs DuckDB queries. Use existing SQLAlchemy connections:

```sql
-- In PostgreSQL
CREATE EXTENSION duckdb_fdw;
CREATE SERVER duckdb_server FOREIGN DATA WRAPPER duckdb_fdw
OPTIONS (database '/path/to/research.duckdb');
IMPORT FOREIGN SCHEMA s2 FROM SERVER duckdb_server INTO public;
```

```python
# FastAPI uses normal PostgreSQL connection
@app.get("/analytics/trends")
def trends(db = Depends(get_db)):
    result = db.execute(text("SELECT year, COUNT(*) FROM papers GROUP BY year"))
    return [dict(row) for row in result]
```

No caching layer needed - DuckDB is fast enough for real-time analytical queries!

## Performance Considerations

### Memory Management

46GB RAM available
Set memory_limit='35GB' (leave headroom)
Set threads=8-16 (based on CPU cores)
Set preserve_insertion_order=false for better performance

### When Queries are Slow

Filter early: Add WHERE clauses before joins
**Don't SELECT ***: Especially avoid body.text (huge field) unless needed
Use VIEWs: Don't materialize unless necessary
Export subsets: For repeated analysis, export filtered results to smaller Parquet

### DuckDB vs MongoDB for Analytics

DuckDB wins: 86% faster aggregations, 10-100x faster for GROUP BY/joins
MongoDB better for: Document lookups by ID, transactional writes
For research: DuckDB is the clear winner

### Common Patterns
Join Large Tables

```sql
-- Join S2ORC papers (with text) to OpenAlex (with metadata)
SELECT s2.title, s2.abstract, oa.topics
FROM s2orc_papers s2
JOIN openalex_works oa ON s2.corpusid = oa.corpusid
WHERE oa.year >= 2020;
```

Text Analysis

```sql
-- Count papers mentioning "machine learning" by year
SELECT 
    year,
    SUM(CASE WHEN body_text ILIKE '%machine learning%' THEN 1 ELSE 0 END) as ml_papers,
    COUNT(*) as total_papers
FROM papers
WHERE year >= 2000
GROUP BY year;
```

Extract Nested Annotations

```sql
-- Extract section headers using struct positions
SELECT 
    corpusid,
    list_transform(
        section_headers,
        h -> SUBSTRING(body_text, h.start + 1, h.end - h.start)
    ) as extracted_sections
FROM papers;
```

### Key Lessons

VIEWs > TABLEs for large read-only datasets (no duplication)
Convert nested JSON to STRUCT during parse (one-time cost, forever benefit)
Partition strategically (by year for temporal data)
DuckLake when modifying, vanilla DuckDB when read-only
No premature caching - DuckDB is fast, add caching only if needed
Separate concerns: Data pipeline (scripts/) vs API (app/)

### Tools & Technologies

DuckDB: Analytical queries on Parquet
DuckLake: Version control for datasets
PostgreSQL: Metadata catalog + pg_duckdb for queries
FastAPI: REST API layer
Parquet: Columnar storage format
Makefile: Pipeline orchestration

This architecture handles 100GB+ datasets efficiently on a single VM with 46GB RAM and 4.3TB network storage.