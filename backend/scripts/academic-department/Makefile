.PHONY: help parse import-data clean all status

# Configuration
BACKEND_DIR = ../../../..
IMPORT_DIR = import
INPUT_DIR = input
CSV_FILE = $(IMPORT_DIR)/uvm_departments.csv
API_BASE = https://complexstories.uvm.edu/datasets

parse:	## Extract and parse UVM salary data from PDF to CSV
	@echo "⚙️ Scraping UVM departments..."
	@mkdir -p $(IMPORT_DIR)
	@echo "📊 CSV file: $(CSV_FILE)"

export-data: parse	## Import parsed CSV data into PostgreSQL database
	@echo "📤 Uploading CSV data to PostgreSQL..."
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