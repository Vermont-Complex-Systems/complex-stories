.PHONY: help parse import-data clean all status

# Configuration
BACKEND_DIR = ../../../..
IMPORT_DIR = import
INPUT_DIR = input
PDF_FILE = $(INPUT_DIR)/Final_FY24_Base_Pay.pdf
CSV_FILE = $(IMPORT_DIR)/uvm_salaries.csv
API_BASE = http://localhost:8000/datasets/academic-research-groups

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

import-data: parse	## Import parsed CSV data into PostgreSQL database
	@echo "📤 Importing CSV data to PostgreSQL..."
	@echo "🌐 Calling API endpoint: $(API_BASE)/import-csv"
	@curl -X POST $(API_BASE)/import-csv -s | \
		python3 -c "import sys, json; data=json.load(sys.stdin); print(f'✅ {data[\"message\"]}: {data[\"imported_count\"]} records')" || \
		(echo "❌ Import failed. Is the FastAPI server running?"; exit 1)

clean:	## Clean up generated files
	@echo "🧹 Cleaning up..."
	@rm -f $(CSV_FILE)
	@echo "✅ Removed $(CSV_FILE)"

all: parse import-data	## Run complete workflow: parse → import

# Default target
.DEFAULT_GOAL := help