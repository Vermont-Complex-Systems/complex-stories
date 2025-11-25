.PHONY: all download parse reparse load load-view load-table sync create-tables create-views enrich export export-arxiv-fulltext export-arxiv-fulltext-force sync-papers-lookup

DATASET ?= papers
DB ?= s2
TABLE ?= all
GROUP_BY ?= field
FIELD ?= all
FORCE ?=
RELEASE ?=

# ============================================================================
# DOWNLOAD: Raw data acquisition
# ============================================================================
download:
	@echo "=== DOWNLOAD: $(DATASET) ==="
	python input/download.py $(DATASET) $(if $(FORCE),--clean-slate)

# ============================================================================
# PARSE: Format standardization (JSON → Parquet)
# ============================================================================
parse:
	@echo "=== PARSE: $(DB) $(DATASET) ==="
	python import/parse.py $(DB) $(DATASET) $(if $(FORCE),--force)

reparse: FORCE=1
reparse: parse

# ============================================================================
# LOAD: Database ingestion (Parquet → DuckLake)
# ============================================================================

# Create views (simple, recommended)
load-view:
	@echo "=== LOAD VIEW: $(DB) $(DATASET) ==="
	python load/load.py view $(DB) $(DATASET) $(if $(FORCE),--force)

# Create tables (special schema handling)
load-table:
	@echo "=== LOAD TABLE: $(TABLE) ==="
	python load/load.py table $(TABLE) $(if $(FORCE),--force)


# ============================================================================
# SYNC: Incremental database updates
# ============================================================================
sync:
	@echo "=== SYNC: $(DB) $(DATASET) ==="
	python load/sync.py $(DB) $(DATASET) $(if $(RELEASE),--release $(RELEASE))

sync-papers-lookup:
	@echo "=== SYNC: Create DOI-based mapping table ==="
	python enrich/sync_db.py --operation lookup

# ============================================================================
# ENRICH: Feature engineering and derived fields
# ============================================================================
enrich:
	@echo "=== ENRICH: Add derived fields ($(FIELD)) ==="
	python enrich/add_derived_fields.py --operation $(FIELD)

# ============================================================================
# EXPORT: Output syndication to endpoints
# ============================================================================
export:
	@echo "=== EXPORT: Export counts by $(GROUP_BY) ==="
	python export/counts.py --group-by $(GROUP_BY)

export-arxiv-fulltext:
	@echo "=== EXPORT: Create arXiv fulltext materialized view ==="
	python export/arxiv_fulltext.py

export-arxiv-fulltext-force:
	@echo "=== EXPORT: Force recreate arXiv fulltext materialized view ==="
	python export/arxiv_fulltext.py --force

# ============================================================================
# HELPERS
# ============================================================================

# Full pipeline for new dataset
pipeline:
	@echo "=== FULL PIPELINE: $(DB) $(DATASET) ==="
	@make download DATASET=$(DATASET)
	@make parse DB=$(DB) DATASET=$(DATASET)
	@make load-view DB=$(DB) DATASET=$(DATASET)
	@echo "✅ Pipeline complete!"

# Help
help:
	@echo "Available targets:"
	@echo "  download          - Download raw dataset"
	@echo "  parse             - Parse JSON to Parquet"
	@echo "  load-view         - Create view in DuckLake (recommended)"
	@echo "  load-table        - Create table with special handling"
	@echo "  sync              - Incrementally update existing table"
	@echo "  enrich            - Add derived fields"
	@echo "  export            - Export processed data"
	@echo ""
	@echo "Examples:"
	@echo "  make download DATASET=openalex-works"
	@echo "  make parse DB=openalex DATASET=works"
	@echo "  make load DB=openalex DATASET=works"
	@echo "  make load-table TABLE=oa_sources FORCE=1"
	@echo "  make sync DB=openalex DATASET=works RELEASE=2024-01-15"
	@echo "  make pipeline DB=openalex DATASET=works"