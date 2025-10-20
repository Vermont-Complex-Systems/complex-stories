#!/usr/bin/env python3
"""
Script to create Label Studio project for Academic Department data annotation.

This script creates a Label Studio project for annotating/correcting Academic Department information
including departments, colleges, research group status, and other metadata.
"""

import os
import yaml
from label_studio_sdk import LabelStudio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
LABEL_STUDIO_URL = os.getenv('LABEL_STUDIO_URL', 'https://cclabel.uvm.edu')
LABEL_STUDIO_API_KEY = os.getenv('LABEL_STUDIO_API_KEY')

if not LABEL_STUDIO_API_KEY:
    raise ValueError("LABEL_STUDIO_API_KEY environment variable is required")

# Initialize Label Studio client
client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_KEY)

# Label configuration for Academic Department data annotation
label_config = """
<View>
  <Header value="Institution Info"/>
  <View style="display: flex; gap: 8px; margin-bottom: 1.5em; flex-wrap: wrap; align-items: center;">
    <Text name="year" value="$year"/>
    <Text name="inst_ipeds_id" value="$inst_ipeds_id"/>
  </View>

    <View style="border: 1px solid #ccc; border-radius: 5px;">
      <Header value="Department"/>
      <TextArea name="department" toName="department" value="$department"/>

      <Header value="College"/>
      <TextArea name="college" toName="college" value="$college"/>

      <Header value="Category"/>
      <TextArea name="category" toName="category" value="$category"/>
  </View>
</View>
"""

def create_academic_department_project():
    """Create the academic department annotation project in Label Studio."""

    try:
        # Create the project
        project = client.projects.create(
            title="Academic Department",
            description="Academic department information and classifications.",
            label_config=label_config,
            # Enable expert mode for better UI
            expert_instruction="Please review and correct the department information."
        )

        print(f"✅ Successfully created Label Studio project!")
        print(f"   Project ID: {project.id}")
        print(f"   Project Title: {project.title}")
        print(f"   Project URL: {LABEL_STUDIO_URL}/projects/{project.id}")
        print(f"\n📝 Next steps:")
        print(f"   1. Import Academic Department data using the import script")
        print(f"   2. Start annotating at {LABEL_STUDIO_URL}/projects/{project.id}")
        print(f"   3. Export annotations when complete")

        return project

    except Exception as e:
        print(f"❌ Error creating Label Studio project: {e}")
        return None

def main():
    """Main function to set up the Academic Department Label Studio project."""
    print(f"🚀 Setting up Academic Department Annotation Project")
    print(f"   Label Studio URL: {LABEL_STUDIO_URL}")
    print(f"   API Key: {'✅ Set' if LABEL_STUDIO_API_KEY else '❌ Missing'}")

    if not LABEL_STUDIO_API_KEY:
        print("\n❌ Please set LABEL_STUDIO_API_KEY environment variable")
        return

    project = create_academic_department_project()

    if project:
        # Prepare project info as dictionary
        project_info = {
            "project_title": project.title,
            "project_description": project.description,
            "project_url": f"{LABEL_STUDIO_URL}/projects/{project.id}",
            "project_id": project.id
            
        }

        # Write project info to YAML file
        info_file = Path(__file__).parent / "Academic Department_project_info.yaml"
        with open(info_file, 'w') as f:
            yaml.dump(project_info, f, default_flow_style=False, sort_keys=False)

        print(f"\n💾 Project info saved to: {info_file}")

if __name__ == "__main__":
    main()