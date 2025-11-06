.PHONY: all download parse load enrich export-subset

DATASET ?= papers
DB ?= semanticscholar

# Full pipeline
all: download_s2 download_oa parse load enrich

download_s2:
	@echo "=== INPUT: Download $(DATASET) ==="
	python input/download_s2.py $(DATASET)

download_oa:
	@echo "=== INPUT: Download OpenAlex snaptshot ==="
	aws s3 sync "s3://openalex" "openalex-snapshot" --no-sign-request

parse:
	@echo "=== IMPORT: Parse $(DATASET) (from $(DB)) ==="
	python import/parse.py $(DB) $(DATASET)

load:
	@echo "=== LOAD: Load to DuckLake ==="
	python load/load_to_ducklake.py --dataset $(DATASET)

enrich:
	@echo "=== ENRICH: Add derived fields ==="
	python enrich/add_derived_fields.py --dataset $(DATASET)

# Optional: Export subsets for FastAPI
# export-ml-papers:
# 	@echo "=== EXPORT: ML papers subset ==="
# 	python export/export_ml_papers.py

# export-author-index:
# 	@echo "=== EXPORT: Author index ==="
# 	python export/export_author_index.py