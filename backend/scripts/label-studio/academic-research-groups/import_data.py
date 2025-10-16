#!/usr/bin/env python3
"""
Script to import current faculty data into Label Studio project.

This script reads the current uvm_profs_2023 data and imports it as tasks
into the Label Studio project for annotation/correction.
"""

import os
import pandas as pd
from label_studio_sdk import LabelStudio
from label_studio_sdk.label_interface.objects import PredictionValue
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
LABEL_STUDIO_URL = os.getenv('LABEL_STUDIO_URL', 'https://cclabel.uvm.edu')
LABEL_STUDIO_API_KEY = os.getenv('LABEL_STUDIO_API_KEY')
FACULTY_PROJECT_ID = os.getenv('FACULTY_PROJECT_ID')

if not LABEL_STUDIO_API_KEY:
    raise ValueError("LABEL_STUDIO_API_KEY environment variable is required")

if not FACULTY_PROJECT_ID:
    print("⚠️  FACULTY_PROJECT_ID not set. Please run setup_faculty_label_studio.py first")
    print("   or set FACULTY_PROJECT_ID manually from the project info file")
    exit(1)

# Initialize Label Studio client
client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_KEY)

def load_faculty_data():
    """Load faculty data from various possible sources."""
    df = pd.read_parquet("../../../data/academic-research-groups.parquet")
    return df

def prepare_tasks(df):
    """Convert faculty dataframe to Label Studio tasks format."""

    # Fill NaN/None values with empty strings
    df = df.fillna('')

    tasks = []
    task_data_list = []  # Keep original data for predictions

    for _, row in df.iterrows():
        # Simple task data without predictions
        task_data = {
            "payroll_name": str(row.get('payroll_name', '')),
            "payroll_year": str(row.get('payroll_year', '')),
            "inst_ipeds_id": str(row.get('inst_ipeds_id', '')),
            "oa_uid": str(row.get('oa_uid', '')),
            "host_dept": str(row.get('host_dept', '')),
            "college": str(row.get('college', '')),
            "group_size": str(row.get('group_size', '')),
            "group_url": str(row.get('group_url', '')),
            "first_pub_year": str(row.get('first_pub_year', '')),
            "notes": str(row.get('notes', ''))
        }

        tasks.append(task_data)
        task_data_list.append(row)  # Keep original data for creating predictions

    return tasks, task_data_list

def import_tasks(project_id, tasks):
    """Import tasks into Label Studio project."""

    try:
        print(f"📤 Importing {len(tasks)} tasks into project ID: {project_id}")

        # Import tasks without preannotations
        response = client.projects.import_tasks(
            id=project_id,
            request=tasks,
            return_task_ids=True
        )

        print(f"📊 Import response: {response}")

        print(f"✅ Successfully imported all {len(tasks)} tasks!")
        print(f"🔗 View project: {LABEL_STUDIO_URL}/projects/{project_id}")

        # Return task count instead of task_ids since we'll get tasks from the API
        return response.task_count

    except Exception as e:
        print(f"❌ Error importing tasks: {e}")
        return 0

def create_predictions(project_id, task_data_list):
    """Create predictions for imported tasks."""

    try:
        print(f"🔮 Creating predictions for tasks...")

        # Get the project and its label interface
        project = client.projects.get(id=project_id)
        li = project.get_label_interface()

        # Get all tasks in the project
        tasks = client.tasks.list(project=project_id, include=["id"])

        prediction_count = 0
        for i, task in enumerate(tasks):
            if i >= len(task_data_list):
                break

            row_data = task_data_list[i]
            predictions = []

            # Create position prediction
            if row_data.get('is_prof') == 1:
                position_pred = li.get_control('position').label(['Professor'])
                predictions.append(position_pred)

            # Create gender prediction - use alias values
            if pd.notna(row_data.get('perceived_as_male')):
                gender_value = '1' if row_data.get('perceived_as_male') == 1 else '0'
                gender_pred = li.get_control('perceived_as_male').label([gender_value])
                predictions.append(gender_pred)

            # Create research group prediction - use alias values
            if pd.notna(row_data.get('has_research_group')):
                group_value = '1' if row_data.get('has_research_group') == 1 else '0'
                group_pred = li.get_control('has_research_group').label([group_value])
                predictions.append(group_pred)

            # Create prediction if we have any
            if predictions:
                prediction = PredictionValue(
                    model_version="faculty-data-import",
                    score=0.99,
                    result=predictions
                )

                client.predictions.create(task=task.id, **prediction.model_dump())
                prediction_count += 1

        print(f"✅ Created {prediction_count} predictions!")
        return True

    except Exception as e:
        print(f"❌ Error creating predictions: {e}")
        return False

def main():
    """Main function to import faculty data into Label Studio."""

    print(f"🚀 Importing Faculty Data to Label Studio")
    print(f"   Label Studio URL: {LABEL_STUDIO_URL}")
    print(f"   Project ID: {FACULTY_PROJECT_ID}")

    # Load faculty data
    df = load_faculty_data()
    if df is None:
        return

    print(f"📊 Loaded {len(df)} faculty records")
    print(f"   Columns: {list(df.columns)}")

    # Prepare tasks
    tasks, task_data_list = prepare_tasks(df)
    print(f"🔄 Prepared {len(tasks)} annotation tasks")

    # Import to Label Studio
    task_count = import_tasks(FACULTY_PROJECT_ID, tasks)

    if task_count > 0:
        print(f"\n🔮 Creating predictions for {task_count} tasks...")

        # Create predictions for the imported tasks
        prediction_success = create_predictions(FACULTY_PROJECT_ID, task_data_list)

        if prediction_success:
            print(f"\n🎉 Import and prediction creation complete! Next steps:")
            print(f"   1. Visit {LABEL_STUDIO_URL}/projects/{FACULTY_PROJECT_ID}")
            print(f"   2. Review pre-filled predictions and make corrections")
            print(f"   3. Export completed annotations when done")
        else:
            print(f"\n⚠️  Tasks imported but predictions failed. You can still annotate manually.")
    else:
        print(f"\n❌ Import failed.")

if __name__ == "__main__":
    main()