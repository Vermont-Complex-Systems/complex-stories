import dagster as dg
from dagster_duckdb import DuckDBResource
import requests
import logging

logger = logging.getLogger(__name__)

@dg.asset(
    kinds={"export"},
    deps=["change_point_analysis"],
    group_name="export"
)
def training_database_upload(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """Export final training data to PostgreSQL database via FastAPI bulk endpoint"""

    with duckdb.get_connection() as conn:
        # Extract training data from DuckDB
        training_df = conn.execute("""
            SELECT
                name,
                aid,
                pub_year,
                older,
                same,
                younger,
                author_age,
                institution,
                existing_collab,
                new_collab,
                age_category,
                shared_institutions,
                counts,
                prop_younger,
                total_coauth,
                nb_papers,
                density,
                is_prof,
                group_size,
                perceived_as_male,
                host_dept,
                college,
                has_research_group,
                oa_uid,
                group_url,
                first_pub_year,
                payroll_name,
                position,
                notes,
                changing_rate
            FROM oa.transform.training_final
            ORDER BY name, pub_year
        """).fetchdf()

        logger.info(f"Extracted {len(training_df)} training records from DuckDB")

        # Convert DataFrame to list of dictionaries
        training_records = training_df.to_dict('records')

        # Process in batches
        batch_size = 10000
        total_batches = (len(training_records) + batch_size - 1) // batch_size
        successful_uploads = 0

        for i in range(0, len(training_records), batch_size):
            batch = training_records[i:i + batch_size]
            batch_num = (i // batch_size) + 1

            try:
                # POST to FastAPI bulk upload endpoint
                response = requests.post(
                    'http://localhost:3001/admin/open-academic-analytics/training/bulk',
                    json=batch,
                    headers={'Content-Type': 'application/json'},
                    timeout=300  # 5 minute timeout for large batches
                )

                if response.status_code == 200:
                    result = response.json()
                    successful_uploads += result.get('training_processed', 0)
                    logger.info(f"Batch {batch_num}/{total_batches}: Successfully uploaded {len(batch)} training records")
                else:
                    logger.error(f"Batch {batch_num}/{total_batches}: Failed to upload training data. Status: {response.status_code}, Response: {response.text}")

            except Exception as e:
                logger.error(f"Batch {batch_num}/{total_batches}: Error uploading training data: {str(e)}")

        logger.info(f"Training upload completed: {successful_uploads}/{len(training_records)} records uploaded successfully")

        return dg.MaterializeResult(
            metadata={
                "total_records": len(training_records),
                "successful_uploads": successful_uploads,
                "batches_processed": total_batches,
                "upload_success_rate": f"{(successful_uploads/len(training_records)*100):.1f}%" if len(training_records) > 0 else "0%"
            }
        )