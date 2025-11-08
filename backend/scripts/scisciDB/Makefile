.PHONY: all download parse reparse load enrich export-subset create-views

DATASET ?= papers
DB ?= semanticscholar

# Full pipeline
all: download_s2 download_oa parse load enrich create-views

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

enrich:
	@echo "=== ENRICH: Add derived fields ==="
	python enrich/add_derived_fields.py --dataset $(DATASET)

# Create optimized views with proper schema handling
create-views:
	@echo "=== CREATE VIEWS: OpenAlex works with schema fixes ==="
	python load/create_views.py --openalex-works

create-openalex-views:
	@echo "=== CREATE VIEWS: OpenAlex works ==="
	python load/create_views.py --openalex-works

create-s2-views:
	@echo "=== CREATE VIEWS: Semantic Scholar papers ==="
	python load/create_views.py --s2-papers

create-all-views:
	@echo "=== CREATE VIEWS: All available views ==="
	python load/create_views.py --openalex-works --s2-papers

list-views:
	@echo "=== LIST VIEWS: Available views in DuckLake ==="
	python load/create_views.py --list-views

# Optional: Export subsets for FastAPI
# export-ml-papers:
# 	@echo "=== EXPORT: ML papers subset ==="
# 	python export/export_ml_papers.py

# export-author-index:
# 	@echo "=== EXPORT: Author index ==="
# 	python export/export_author_index.py