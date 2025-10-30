import dagster as dg
from dagster_duckdb import DuckDBResource
import logging
from open_academic_analytics.defs.resources import ComplexStoriesAPIResource

logger = logging.getLogger(__name__)

@dg.asset(
    kinds={"export"},
    deps=["change_point_analysis"],
    group_name="export"
)
def training_database_upload(duckdb: DuckDBResource, stories_resources: ComplexStoriesAPIResource) -> dg.MaterializeResult:
    """Export final training data to PostgreSQL database via FastAPI bulk endpoint"""

    with duckdb.get_connection() as conn:
        # import duckdb
        # conn=duckdb.connect("~/oa.duckdb")
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
                -- Calculate age_category from collaboration patterns
                CASE
                    WHEN prop_younger > 0.6 THEN 'younger'
                    WHEN prop_younger > 0.3 THEN 'same'
                    ELSE 'older'
                END as age_category,
                shared_inst_collabs as shared_institutions,
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
                changing_rate
            FROM oa.transform.training_final
            ORDER BY name, pub_year
        """).fetchdf()

        logger.info(f"Extracted {len(training_df)} training records from DuckDB")

        # Clean data to handle JSON serialization issues
        import numpy as np
        def clean_for_json_serialization(df):
            """Clean data for JSON serialization - handle NaN and infinity"""
            print("Cleaning data for JSON serialization...")
            return df.replace([np.nan, np.inf, -np.inf], None)

        training_df = clean_for_json_serialization(training_df)
        
        # Convert DataFrame to list of dictionaries
        training_records = training_df.to_dict('records')

        # Upload to database using the API resource
        stories_resources = ComplexStoriesAPIResource()
        client = stories_resources.get_client()
        logger.info(f"Starting upload of {len(training_records)} training records...")

        # Debug: Check first record structure
        if training_records:
            logger.info(f"Sample record fields: {list(training_records[0].keys())}")

        upload_result = client.bulk_upload(
            endpoint="open-academic-analytics/training/bulk",
            data=training_records,
            batch_size=10000,
            timeout=300
        )
        successful_uploads = upload_result["records_uploaded"]
        batches_processed = upload_result["batches_processed"]
        logger.info(f"Training upload completed: {successful_uploads}/{len(training_records)} records uploaded successfully")

        return dg.MaterializeResult(
            metadata={
                "total_records": len(training_records),
                "successful_uploads": successful_uploads,
                "batches_processed": batches_processed,
                "upload_success_rate": f"{(successful_uploads/len(training_records)*100):.1f}%" if len(training_records) > 0 else "0%"
            }
        )