.PHONY: help parse import-data clean all status

# Configuration
BACKEND_DIR = ../../../..
IMPORT_DIR = import
INPUT_DIR = input
PDF_FILE = $(INPUT_DIR)/Final_FY24_Base_Pay.pdf
CSV_FILE = $(IMPORT_DIR)/uvm_salaries.csv
API_BASE = http://localhost:8000/datasets

help:	## Show this help message
	@echo "Academic Research Groups Annotation Workflow"
	@echo "============================================="
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\\n", $$1, $$2}' $(MAKEFILE_LIST)

parse:	## Extract and parse UVM salary data from PDF to CSV
	@echo "⚙️ Parsing UVM salary data from PDF..."
	@if [ ! -f "$(PDF_FILE)" ]; then \
		echo "❌ PDF file not found: $(PDF_FILE)"; \
		echo "📄 Please place the UVM salary PDF in $(INPUT_DIR)/"; \
		exit 1; \
	fi
	@mkdir -p $(IMPORT_DIR)
	@cd $(IMPORT_DIR) && python ../parse.py
	@echo "✅ Parsed $(shell wc -l < $(CSV_FILE) | xargs echo $$(($$1 - 1))) faculty records"
	@echo "📊 CSV file: $(CSV_FILE)"

export-data: parse	## Import parsed CSV data into PostgreSQL database
	@echo "📤 Uploading CSV data to PostgreSQL..."
	@echo "🌐 Using improved upload script with API: $(API_BASE)"
	@python3 export/upload_dataset.py --csv-file "$(CSV_FILE)" --api-base $(API_BASE) || \
		(echo "❌ Import failed. Is the FastAPI server running on port 8001?"; exit 1)

dry-run: parse	## Parse CSV and show preview without importing
	@echo "🔍 Dry run - parsing CSV and showing preview..."
	@python3 export/upload_dataset.py --csv-file "$(CSV_FILE)" --dry-run

clean:	## Clean up generated files
	@echo "🧹 Cleaning up..."
	@rm -f $(CSV_FILE)
	@echo "✅ Removed $(CSV_FILE)"

all: parse export-data	## Run complete workflow: parse → import

# Default target
.DEFAULT_GOAL := help