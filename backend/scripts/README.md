# Backend Scripts

This directory contains utility scripts for administrative tasks and external service setup.

## Label Studio Faculty Annotation

Scripts for setting up and managing faculty data annotation through Label Studio.

### Prerequisites

1. **Environment Variables** (in `.env` or shell):
   ```bash
   LABEL_STUDIO_URL=https://cclabel.uvm.edu
   LABEL_STUDIO_API_KEY=your_api_key_here
   ```

2. **Python Dependencies**:
   ```bash
   pip install label-studio-sdk pandas
   ```

### Setup Workflow

#### 1. Create Label Studio Project

```bash
cd backend/scripts
python setup_faculty_label_studio.py
```

This creates a new Label Studio project configured for faculty annotation with:
- Department and college selection
- Faculty status classification
- Research group information
- Demographics (optional)
- Career information
- Notes field

**Output**: Creates project and saves info to `faculty_project_info.txt`

#### 2. Import Current Faculty Data

```bash
# Set the project ID from step 1
export FACULTY_PROJECT_ID=123  # Use ID from faculty_project_info.txt

python import_faculty_data.py
```

This imports existing faculty data as annotation tasks with:
- Pre-populated fields from current data
- Ready for review/correction
- Batch import for efficiency

#### 3. Annotate Data

1. Visit the Label Studio project URL (shown in output)
2. Review and correct faculty information
3. Focus on department assignments, research group status, etc.
4. Complete annotations for all faculty

#### 4. Export Annotations

Use Label Studio UI or API to export completed annotations in JSON format.

### API Integration

Once annotations are complete, the `/datasets/faculty` endpoint can be updated to:

1. Query Label Studio for completed annotations
2. Transform annotations to faculty data format
3. Serve as authoritative faculty data source

### File Structure

```
backend/scripts/
├── README.md                       # This file
├── setup_faculty_label_studio.py   # Create LS project
├── import_faculty_data.py          # Import data to LS
└── faculty_project_info.txt        # Project details (generated)
```

### Data Sources

The import script looks for faculty data in:
- `backend/data/faculty-uvm-2023.parquet`
- `backend/data/faculty.parquet`
- `backend/data/uvm_profs_2023.parquet`
- `backend/data/faculty.csv`

### Troubleshooting

**Project creation fails**:
- Check Label Studio URL and API key
- Verify Label Studio instance is accessible
- Check API key permissions

**Import fails**:
- Ensure `FACULTY_PROJECT_ID` is set correctly
- Check faculty data file exists
- Verify project exists in Label Studio

**No data found**:
- Run Dagster pipeline to generate `uvm_profs_2023` data
- Export to parquet format in `backend/data/`
- Check file paths in import script

### Next Steps

1. **Automate exports**: Script to pull annotations from Label Studio
2. **Sync with API**: Update `/datasets/faculty` to use Label Studio data
3. **Multi-institution**: Extend for other universities
4. **Validation**: Add data quality checks for annotations