.PHONY: all download parse reparse load create-tables create-papers-lookup create-papers-lookup-bg create-views enrich enrich-topics enrich-categories export-subset export

DATASET ?= papers
DB ?= semanticscholar
GROUP_BY ?= field
FIELD ?= all

# INPUT: Raw data acquisition
download_s2:
	@echo "=== INPUT: Download $(DATASET) ==="
	python input/download_s2.py $(DATASET)

download_oa:
	@echo "=== INPUT: Download OpenAlex snaptshot ==="
	aws s3 sync "s3://openalex" "openalex-snapshot" --no-sign-request

# IMPORT: Format standardization (JSON → parquet)
parse:
	@echo "=== IMPORT: Parse $(DATASET) (from $(DB)) ==="
	python import/parse.py $(DB) $(DATASET)

reparse:
	@echo "=== IMPORT: Force reparse $(DATASET) (from $(DB)) ==="
	python import/parse.py $(DB) $(DATASET) --force

# LOAD: Database ingestion (parquet → tables)
load:
	@echo "=== LOAD: Load to DuckLake ==="
	python load/load_to_ducklake.py --dataset $(DATASET)

create-tables:
	@echo "=== CREATE TABLES: Load parquet data with proper schemas ==="
	python load/create_tables.py --tables all
	
create-views:
	@echo "=== CREATE VIEWS ==="
	python load/create_views.py $(DB) $(DATASET)

# TRANSFORM: Data quality and deduplication
sync-papers-lookup:
	@echo "=== SYNC: Create DOI-based mapping table ==="
	python enrich/sync_db.py --operation lookup


# ENRICH: Feature engineering and derived fields
enrich:
	@echo "=== ENRICH: Add OpenAlex topics and concepts ==="
	python enrich/add_derived_fields.py --operation $(FIELD)

# EXPORT: Output syndication to endpoints
export:
	@echo "=== EXPORT: Export counts by $(GROUP_BY) ==="
	python export/counts.py --group-by $(GROUP_BY)

export-arxiv-fulltext:
	@echo "=== EXPORT: Create arXiv fulltext materialized view ==="
	python export/arxiv_fulltext.py

export-arxiv-fulltext-force:
	@echo "=== EXPORT: Force recreate arXiv fulltext materialized view ==="
	python export/arxiv_fulltext.py --force

