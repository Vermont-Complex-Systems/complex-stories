.PHONY: all download parse reparse load create-tables create-papers-lookup create-papers-lookup-bg create-views enrich enrich-topics enrich-categories export-subset export

DATASET ?= papers
DB ?= semanticscholar
GROUP_BY ?= field

download_s2:
	@echo "=== INPUT: Download $(DATASET) ==="
	python input/download_s2.py $(DATASET)

download_oa:
	@echo "=== INPUT: Download OpenAlex snaptshot ==="
	aws s3 sync "s3://openalex" "openalex-snapshot" --no-sign-request

parse:
	@echo "=== IMPORT: Parse $(DATASET) (from $(DB)) ==="
	python import/parse.py $(DB) $(DATASET)

reparse:
	@echo "=== IMPORT: Force reparse $(DATASET) (from $(DB)) ==="
	python import/parse.py $(DB) $(DATASET) --force

load:
	@echo "=== LOAD: Load to DuckLake ==="
	python load/load_to_ducklake.py --dataset $(DATASET)

create-tables:
	@echo "=== CREATE TABLES: Load parquet data with proper schemas ==="
	python load/create_tables.py --tables all

sync-papers-lookup:
	@echo "=== SYNC: Create DOI-based mapping table ==="
	python enrich/sync_db.py --operation lookup

sync-openalex-ids:
	@echo "=== SYNC: Add OpenAlex IDs to s2_papers ==="
	python enrich/sync_db.py --operation workid

sync-all:
	@echo "=== SYNC: All S2 ↔ OpenAlex operations ==="
	python enrich/sync_db.py --operation all
	
# Create optimized views with proper schema handling
create-views:
	@echo "=== CREATE VIEWS ==="
	python load/create_views.py $(DB) $(DATASET)

enrich:
	@echo "=== ENRICH: Add derived fields ==="
	python enrich/add_derived_fields.py --dataset $(DATASET)

enrich-topics:
	@echo "=== ENRICH: Add OpenAlex topics and concepts ==="
	python enrich/add_derived_fields.py --dataset $(DATASET) --operation openalex_topics

enrich-categories:
	@echo "=== ENRICH: Extract topic categories ==="
	python enrich/add_derived_fields.py --dataset $(DATASET) --operation topic_categories

export:
	@echo "=== EXPORT: Export counts by $(GROUP_BY) ==="
	python export/counts.py --group-by $(GROUP_BY)

