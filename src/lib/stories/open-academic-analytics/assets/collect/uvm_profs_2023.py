import requests
import pandas as pd
from datetime import timedelta

from dagster import asset, get_dagster_logger
from dagster.preview.freshness import FreshnessPolicy
from dagster import MaterializeResult, MetadataValue

from config import config

@asset(
    group_name="import",
    description="📋 UVM Professors 2023 dataset from Vermont Complex Systems",
    freshness_policy=FreshnessPolicy.time_window(
        fail_window=timedelta(hours=168),  # Fail if no update in 7 days
        warn_window=timedelta(hours=144)   # Warn if no update in 6 days
    )
)
def uvm_profs_2023():
    """
    Fetches and processes UVM professors dataset from Vermont Complex Systems.
    Includes data processing and freshness monitoring.
    """
    logger = get_dagster_logger()
    
    dataset_url = "https://vermont-complex-systems.github.io/datasets/data/academic-research-groups.csv"
    
    try:
        # Check availability and get metadata
        logger.info(f"Checking availability: {dataset_url}")
        head_response = requests.head(dataset_url, timeout=10)
        
        if head_response.status_code == 200:
            file_size = head_response.headers.get('content-length', 'Unknown')
            last_modified = head_response.headers.get('last-modified', 'Unknown')
            etag = head_response.headers.get('etag', 'Unknown')
            
            logger.info(f"✓ Dataset available")
            logger.info(f"  File size: {file_size} bytes")
            logger.info(f"  Last modified: {last_modified}")
            logger.info(f"  ETag: {etag}")
        else:
            raise Exception(f"Dataset not available. HTTP {head_response.status_code}")
    
    except Exception as e:
        logger.warning(f"Availability check failed: {e}")
        logger.info("Proceeding with download attempt...")
        
    # Download and process the CSV
    logger.info(f"Downloading and processing CSV...")
    
    try:
        input_file = config.data_raw_path / config.departments_file
        output_file = config.data_raw_path / config.uvm_profs_2023_file

        df = pd.read_csv(dataset_url)
        logger.info(f"✓ Successfully loaded {len(df)} records")

        # Filter just 2023 and UVM
        df = df[(df.payroll_year == 2023) & (df.inst_ipeds_id == 231174)]
        
        # Save a copy in export
        df.to_parquet(config.data_export_path / config.uvm_profs_2023_file)
        
        # Reorder columns for pipeline consistency
        column_order = [
            'oa_display_name', 'is_prof', 'group_size', 'perceived_as_male', 
            'host_dept', 'college', 'has_research_group', 'oa_uid', 'group_url', 'first_pub_year',
            'payroll_name', 'position', 'notes'
        ]
        
        # Reorder columns
        df = df[column_order]
        
        # Filter researchers without OpenAlex ID and normalize
        initial_count = len(df)
        df = df[~df['oa_uid'].isna()]
        df['oa_uid'] = df['oa_uid'].str.upper()

        filtered_count = len(df)
        logger.info(f"✓ Filtered {initial_count - filtered_count} researchers without OpenAlex IDs")
        logger.info(f"✅ Final dataset: {filtered_count} researchers ready for analysis")
        
        # save file
        df.to_parquet(output_file)

        return MaterializeResult(
            metadata={
                "external_file": MetadataValue.path(str(dataset_url)), 
                "input_file": MetadataValue.path(str(input_file)), 
                "output_file": MetadataValue.path(str(output_file))
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to download/parse CSV: {e}")
        raise