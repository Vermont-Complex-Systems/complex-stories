.PHONY: help input upload

# Configuration
BACKEND_DIR = ../../../..
IMPORT_DIR = import
INPUT_DIR = input
EXPORT_DIR = export
API_BASE = http://localhost:8000

scrape_google:	## Scrape Google Scholar venues by field
	@echo "=== INPUT: Scrape Google Scholar venues ==="
	python input/google-scholar.py

upload:	## Upload Google Scholar venues data to API
	@echo "=== EXPORT: Upload venues data to API ==="
	python export/upload_dataset.py --parquet-file input/google-scholar.parquet --api-base $(API_BASE)

all: scrape_google upload	## Run complete workflow: scrape → upload