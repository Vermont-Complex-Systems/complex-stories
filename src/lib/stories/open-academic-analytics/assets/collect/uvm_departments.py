import requests
import pandas as pd

from dagster import asset, get_dagster_logger
from dagster import MaterializeResult, MetadataValue

from config import config

@asset(
    group_name="import",
    description="🏛️ UVM Departments to Colleges mapping for organizational analysis"
)
def uvm_departments():
    """
    Fetches UVM department-to-college mapping from Vermont Complex Systems
    """
    logger = get_dagster_logger()
    
    dataset_url = "https://vermont-complex-systems.github.io/datasets/data/academic-department.csv"
    output_file = config.data_raw_path / config.departments_file

    try:
        # Check availability
        logger.info(f"Checking availability: {dataset_url}")
        head_response = requests.head(dataset_url, timeout=10)
        
        if head_response.status_code == 200:
            file_size = head_response.headers.get('content-length', 'Unknown')
            last_modified = head_response.headers.get('last-modified', 'Unknown')
            
            logger.info(f"✓ Dataset available")
            logger.info(f"  File size: {file_size} bytes")
            logger.info(f"  Last modified: {last_modified}")
        else:
            raise Exception(f"Dataset not available. HTTP {head_response.status_code}")
    
    except Exception as e:
        logger.warning(f"Availability check failed: {e}")
        logger.info("Proceeding with download attempt...")
    
    # Download and process
    try:
        df = pd.read_csv(dataset_url)
        logger.info(f"✓ Successfully loaded {len(df)} department mappings")

        expected_columns = ['department', 'college', 'inst_ipeds_id', 'year']
        if not all(col in df.columns for col in expected_columns):
            raise Exception(f"Missing expected columns. Found: {list(df.columns)}")
        
        # Select year and UVM
        df = df[(df.inst_ipeds_id == 231174) & (df.year == 2023)]

        # Save raw copy to static
        df.to_parquet(config.data_export_path / config.departments_file)
        

        # Remove any empty rows
        initial_count = len(df)
        df = df.dropna(subset=['department', 'college'])
        final_count = len(df)
        
        if initial_count != final_count:
            logger.info(f"  Removed {initial_count - final_count} empty rows")
        
        # Normalize department and college names
        df['department'] = df['department'].str.strip()
        df['college'] = df['college'].str.strip()
        
        # Only normalize category if it exists
        if 'category' in df.columns:
            df['category'] = df['category'].str.strip()
        
        # Log unique colleges for validation
        unique_colleges = df['college'].unique()
        logger.info(f"  Departments mapped to {len(unique_colleges)} colleges:")
        for college in sorted(unique_colleges):
            dept_count = len(df[df['college'] == college])
            logger.info(f"    {college}: {dept_count} departments")
        
        # Save to file
        df.to_parquet(output_file)
        logger.info(f"✓ Saved to {output_file}")

        return MaterializeResult(
            metadata={
                "external_file": MetadataValue.path(str(dataset_url)), 
                "output_file": MetadataValue.path(str(output_file))
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to load departments mapping: {e}")
        raise