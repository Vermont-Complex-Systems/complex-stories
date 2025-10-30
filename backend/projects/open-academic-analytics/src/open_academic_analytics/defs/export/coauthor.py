import dagster as dg
from dagster_duckdb import DuckDBResource
from open_academic_analytics.defs.resources import ComplexStoriesAPIResource

@dg.asset(
    kinds={"duckdb"},
    deps=["yearly_collaborations", "coauthor_institutions", "coauthor_cache", "uvm_profs_2023"],
    group_name="transform"
)
def processed_coauthors(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """Aggregate and join coauthor collaboration data with first publication years and institutions"""

    with duckdb.get_connection() as conn:
        conn.execute("""
            CREATE OR REPLACE TABLE oa.transform.processed_coauthors AS (
                WITH calculated_first_years AS (
                    SELECT
                        a.author_id,
                        MIN(p.publication_year) as min_pub_year
                    FROM oa.raw.authorships a
                    JOIN oa.raw.publications p ON a.work_id = p.id
                    WHERE p.publication_year IS NOT NULL
                    GROUP BY a.author_id
                ),
                base_data AS (
                    SELECT
                        yc.*,
                        -- Use ground truth first_pub_year when available, fallback to calculated
                        COALESCE(prof.first_pub_year, ego_calc.min_pub_year) as ego_first_pub_year,
                        COALESCE(cc_coauthor.first_pub_year, prof_coauthor.first_pub_year, coauthor_calc.min_pub_year) as coauthor_first_pub_year,

                        -- Include other fields from joins
                        prof.first_pub_year as prof_first_pub_year_raw,
                        prof.department as ego_department,
                        ci_uvm.primary_institution,
                        ci_external.primary_institution as coauthor_institution

                    FROM oa.transform.yearly_collaborations yc

                    LEFT JOIN oa.raw.uvm_profs_2023 prof
                        ON yc.ego_author_id = prof.ego_author_id

                    LEFT JOIN calculated_first_years ego_calc
                        ON yc.ego_author_id = ego_calc.author_id

                    LEFT JOIN oa.cache.coauthor_cache cc_coauthor
                        ON yc.coauthor_id = cc_coauthor.id

                    LEFT JOIN oa.raw.uvm_profs_2023 prof_coauthor
                        ON yc.coauthor_id = prof_coauthor.ego_author_id

                    LEFT JOIN calculated_first_years coauthor_calc
                        ON yc.coauthor_id = coauthor_calc.author_id

                    LEFT JOIN oa.transform.coauthor_institutions ci_uvm
                        ON yc.ego_author_id = ci_uvm.id
                        AND yc.publication_year = ci_uvm.publication_year

                    LEFT JOIN oa.transform.coauthor_institutions ci_external
                        ON yc.coauthor_id = ci_external.id
                        AND yc.publication_year = ci_external.publication_year
                )
                SELECT * FROM base_data
                ORDER BY ego_author_id, coauthor_id, publication_year
            )
        """)

        # Get row count for metadata
        row_count = conn.execute("SELECT COUNT(*) FROM oa.transform.processed_coauthors").fetchone()[0]

        # Get table schema using PyArrow
        table_arrow = conn.execute("SELECT * FROM oa.transform.processed_coauthors LIMIT 0").arrow()

    return dg.MaterializeResult(
        metadata={
            "record_count": row_count,
            "table_schema": dg.MetadataValue.table_schema(
                dg.TableSchema(
                    columns=[
                        dg.TableColumn(field.name, str(field.type))
                        for field in table_arrow.schema
                    ]
                )
            )
        }
    )

@dg.asset(
    kinds={"postgres"},
    deps=["processed_coauthors"],
    group_name="export"
)
def coauthor_database_upload(duckdb: DuckDBResource, complex_stories_api: ComplexStoriesAPIResource) -> dg.MaterializeResult:
    """Export final coauthor collaboration data to database via API"""

    with duckdb.get_connection() as conn:
        # Apply final transformations to the processed_coauthors data
        result = conn.execute("""
            WITH age_calculations AS (
                SELECT
                    *,
                    CASE
                        WHEN ego_first_pub_year IS NOT NULL
                        THEN (publication_year - ego_first_pub_year)
                        ELSE NULL
                    END as ego_age,

                    CASE
                        WHEN coauthor_first_pub_year IS NOT NULL
                        THEN (publication_year - coauthor_first_pub_year)
                        ELSE NULL
                    END as coauthor_age

                FROM oa.transform.processed_coauthors
            )
            SELECT
                -- UVM professor information
                ego_author_id,
                ego_display_name,
                ego_department,
                publication_year,
                nb_coauthors,

                -- Publication info with jitter
                publication_date::DATE + INTERVAL (FLOOR(RANDOM() * 28) + 1) DAYS as publication_date,

                -- Ego author information
                ego_first_pub_year,
                ego_age,

                -- Coauthor information
                coauthor_id,
                coauthor_display_name,
                coauthor_age,
                coauthor_first_pub_year,

                -- Age difference calculations
                (ego_age - coauthor_age) as age_diff,

                CASE
                    WHEN ego_age IS NOT NULL AND coauthor_age IS NOT NULL THEN
                        CASE
                            WHEN (ego_age - coauthor_age) > 7 THEN 'younger'
                            WHEN (ego_age - coauthor_age) < -7 THEN 'older'
                            ELSE 'same'
                        END
                    ELSE 'unknown'
                END as age_category,

                -- Collaboration metrics
                yearly_collabo,
                SUM(yearly_collabo) OVER (
                    PARTITION BY ego_author_id, coauthor_id
                    ORDER BY publication_year
                    ROWS UNBOUNDED PRECEDING
                ) as all_times_collabo,

                -- Institution information
                primary_institution,
                coauthor_institution,

                CASE
                    WHEN primary_institution IS NOT NULL
                        AND coauthor_institution IS NOT NULL
                        AND primary_institution = coauthor_institution
                        THEN primary_institution
                        ELSE NULL
                END as shared_institutions

            FROM age_calculations
            ORDER BY publication_year
        """).fetchall()

        # Get column names from the query result
        column_names = [desc[0] for desc in conn.description]

        # Convert to list of dictionaries for API
        coauthor_data = []
        for row in result:
            # Create row dictionary using column names
            row_dict = dict(zip(column_names, row))
            # Create composite ID for the database
            row_dict['id'] = f"{row_dict['ego_author_id']}_{row_dict['coauthor_id']}_{row_dict['publication_year']}"
            coauthor_data.append(row_dict)

        # Clean data to ensure JSON serialization compatibility
        import json
        from datetime import date, datetime

        def clean_for_json(obj):
            try:
                json.dumps(obj)
                return obj
            except TypeError:
                if hasattr(obj, 'item'):  # numpy scalar
                    return obj.item()
                elif obj is None:
                    return None
                elif isinstance(obj, date):  # Python date objects
                    return obj.isoformat()  # YYYY-MM-DD format
                elif isinstance(obj, datetime):  # Python datetime objects
                    return obj.isoformat()  # YYYY-MM-DDTHH:MM:SS format
                elif hasattr(obj, 'strftime'):  # other datetime/timestamp objects
                    return obj.strftime('%Y-%m-%d')
                else:
                    return str(obj)

        # Apply cleanup to all records
        for record in coauthor_data:
            for key, value in record.items():
                record[key] = clean_for_json(value)

        # Save processed data to DuckDB for downstream assets
        import pandas as pd
        df_coauthors = pd.DataFrame(coauthor_data)
        conn.execute("CREATE OR REPLACE TABLE oa.transform.processed_coauthors_final AS SELECT * FROM df_coauthors")
        dg.get_dagster_logger().info(f"Saved {len(df_coauthors)} processed coauthor records to DuckDB table")

        # Debug: Log first record for troubleshooting
        if coauthor_data:
            dg.get_dagster_logger().info(f"Sample record keys: {list(coauthor_data[0].keys())}")
            dg.get_dagster_logger().info(f"Sample record: {coauthor_data[0]}")
            dg.get_dagster_logger().info(f"Total records to upload: {len(coauthor_data)}")

        # Upload to database using the API resource
        try:
            client = complex_stories_api.get_client()
            upload_result = client.bulk_upload(
                endpoint="open-academic-analytics/coauthors/bulk",
                data=coauthor_data,
                batch_size=10000
            )

            return dg.MaterializeResult(
                metadata={
                    **upload_result,
                    "upload_status": "success"
                }
            )

        except Exception as e:
            dg.get_dagster_logger().error(f"Failed to upload coauthor data: {str(e)}")
            raise


