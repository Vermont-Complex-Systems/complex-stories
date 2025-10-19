#!/usr/bin/env python3
"""
Script to create Label Studio project for faculty data annotation.

This script creates a Label Studio project for annotating/correcting faculty information
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

# Label configuration for faculty data annotation
label_config = """
<View>
  <!-- Reference info for context -->
  <Header value="Researcher Info"/>
  <View style="display: flex; gap: 8px; margin-bottom: 1.5em; flex-wrap: wrap; align-items: center;">
    <Text name="payroll_name" value="$payroll_name" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 500; box-shadow: 0 2px 4px rgba(0,0,0,0.1); letter-spacing: 0.3px;"/>
    <Text name="payroll_year" value="$payroll_year" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 500; box-shadow: 0 2px 4px rgba(0,0,0,0.1); letter-spacing: 0.3px;"/>
    <Text name="inst_ipeds_id" value="$inst_ipeds_id" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 500; box-shadow: 0 2px 4px rgba(0,0,0,0.1); letter-spacing: 0.3px;"/>
  </View>

  <!-- Two-column form -->
  <View style="display: flex; flex-direction: row; gap: 2em; align-items: flex-start;">
    
    <!-- LEFT COLUMN: Choices -->
    <View style="flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
      <Header value="Position"/>
      <Choices name="position" toName="payroll_name" choice="single-radio">
        <Choice value="Professor"/>
        <Choice value="Assistant Professor"/>
        <Choice value="Associate Professor"/>
        <Choice value="Research Professor"/>
      </Choices>

      <Header value="Perceived Gender"/>
      <Choices name="perceived_as_male" toName="payroll_name" choice="single-radio">
        <Choice value="Male" alias="1"/>
        <Choice value="Female" alias="0"/>
      </Choices>

      <Header value="Has Research Group"/>
      <Choices name="has_research_group" toName="payroll_name" choice="single-radio">
        <Choice value="Yes" alias="1"/>
        <Choice value="No" alias="0"/>
      </Choices>
    </View>
    
    <!-- RIGHT COLUMN: Text Areas -->
    <View style="flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
      <Header value="Host Department"/>
      <TextArea name="host_dept" toName="payroll_name" value="$host_dept" editable="true"/>

      <Header value="Group Size"/>
      <TextArea name="group_size" toName="payroll_name" value="$group_size" editable="true"/>

      <Header value="Group URL"/>
      <TextArea name="group_url" toName="payroll_name" value="$group_url" editable="true"/>

      <Header value="First Publication Year"/>
      <TextArea name="first_pub_year" toName="payroll_name" value="$first_pub_year" editable="true"/>

      <Header value="OpenAlex user id"/>
      <TextArea name="oa_uid" toName="payroll_name" value="$oa_uid" editable="true"/>

      <Header value="Notes"/>
      <TextArea name="notes" toName="payroll_name" value="$notes" editable="true"/>
    </View>

  </View>
</View>
"""

def create_faculty_project():
    """Create the faculty annotation project in Label Studio."""

    try:
        # Create the project
        project = client.projects.create(
            title="Academic Research Groups",
            description="Annotate and correct faculty information including departments, colleges, research groups, and metadata.",
            label_config=label_config,
            # Enable expert mode for better UI
            expert_instruction="Please review and correct the faculty information. Focus on:\n"
                             "1. Correct department and college assignments\n"
                             "2. Research group status and size\n"
                             "3. Faculty vs staff classification\n"
                             "4. Any additional corrections or notes"
        )

        print(f"✅ Successfully created Label Studio project!")
        print(f"   Project ID: {project.id}")
        print(f"   Project Title: {project.title}")
        print(f"   Project URL: {LABEL_STUDIO_URL}/projects/{project.id}")
        print(f"\n📝 Next steps:")
        print(f"   1. Import faculty data using the import script")
        print(f"   2. Start annotating at {LABEL_STUDIO_URL}/projects/{project.id}")
        print(f"   3. Export annotations when complete")

        return project

    except Exception as e:
        print(f"❌ Error creating Label Studio project: {e}")
        return None

def main():
    """Main function to set up the faculty Label Studio project."""
    print(f"🚀 Setting up Faculty Annotation Project")
    print(f"   Label Studio URL: {LABEL_STUDIO_URL}")
    print(f"   API Key: {'✅ Set' if LABEL_STUDIO_API_KEY else '❌ Missing'}")

    if not LABEL_STUDIO_API_KEY:
        print("\n❌ Please set LABEL_STUDIO_API_KEY environment variable")
        return

    project = create_faculty_project()

    if project:
        # Prepare project info as dictionary
        project_info = {
            "project_title": project.title,
            "project_description": project.description,
            "project_url": f"{LABEL_STUDIO_URL}/projects/{project.id}",
            "project_id": project.id
            
        }

        # Write project info to YAML file
        info_file = Path(__file__).parent / "faculty_project_info.yaml"
        with open(info_file, 'w') as f:
            yaml.dump(project_info, f, default_flow_style=False, sort_keys=False)

        print(f"\n💾 Project info saved to: {info_file}")

if __name__ == "__main__":
    main()