"""
data_collection.py

Stage 1: Collect raw academic data from external sources
"""
import pandas as pd
import dagster as dg
from dagster import MaterializeResult, MetadataValue

from config import config

@dg.asset(
    group_name="import",
    description="📋 Load list of UVM researchers to analyze for collaboration patterns"
)
def researcher_list():
    """Convert researchers parquet to TSV format for processing"""
    input_file = config.data_raw_path / config.researchers_input_file
    output_file = config.data_raw_path / config.researchers_tsv_file

    # Load and process
    d = pd.read_parquet(input_file)
    
    # Handle column name variations
    if 'host_dept (; delimited if more than one)' in d.columns:
        d = d.rename(columns={'host_dept (; delimited if more than one)': 'host_dept'})
    
    # Select and save
    cols = ['oa_display_name', 'is_prof', 'group_size', 'perceived_as_male', 
            'host_dept', 'has_research_group', 'oa_uid', 'group_url', 'first_pub_year']
    
    d[cols].to_csv(output_file, sep="\t", index=False)
    
    print(f"✅ Created researcher list with {len(d)} researchers")
    
    return MaterializeResult(
        metadata={
            "researchers_loaded": MetadataValue.int(len(d)),
            "output_file": MetadataValue.path(str(output_file)),
            "research_value": MetadataValue.md(
                "**Foundation dataset** for academic collaboration analysis. "
                "Contains UVM faculty with OpenAlex IDs for paper retrieval."
            )
        }
    )
