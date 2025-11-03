import dagster as dg
from dagster_duckdb import DuckDBResource
from open_academic_analytics.defs.resources import ComplexStoriesAPIResource

@dg.asset(
        description="📋 Load UVM Professors 2023 dataset from Complex Stories FastAPI backend (now with consistent data)",
        kinds={"duckdb"},
        group_name="import"
    )
def uvm_profs_2023(duckdb: DuckDBResource, complex_stories_api: ComplexStoriesAPIResource) -> dg.MaterializeResult:
    
    with duckdb.get_connection() as conn:
        # params
        payroll_year=2023
        ipeds_id=231174

        # Use the API client's base URL to construct the parquet URL
        client = complex_stories_api.get_client()
        api_url = f"{client.base_url}/datasets/academic-research-groups?inst_ipeds_id={ipeds_id}&year={payroll_year}&format=parquet"
        
        row_count = conn.execute(
            f"""
            CREATE OR REPLACE TABLE oa.raw.uvm_profs_2023 as (
                SELECT
                    group_size,
                    perceived_as_male,
                    host_dept AS department,
                    college,
                    has_research_group,
                    'https://openalex.org/' || oa_uid AS ego_author_id,
                    group_url,
                    CAST(first_pub_year AS INTEGER) as first_pub_year,
                    payroll_name,
                    position,
                    last_updated,
                    CASE
                        WHEN LOWER(position) LIKE '%professor%' THEN 1
                        ELSE 0
                    END AS is_prof
                FROM read_parquet('{api_url}')
                WHERE oa_uid IS NOT NULL
            )
            """
        ).fetchone()
    
    
    #####################################
    #                                   #
    # Get schema and stats for metadata #
    #                                   #
    #####################################


    with duckdb.get_connection() as conn:
        # Get table schema using PyArrow
        table_arrow = conn.execute("SELECT * FROM oa.raw.uvm_profs_2023 LIMIT 0").arrow()

    return dg.MaterializeResult(
        metadata={
            "record_count": row_count[0] if row_count else 0,
            "table_schema": dg.MetadataValue.table_schema(
                dg.TableSchema(
                    columns=[
                        dg.TableColumn(field.name, str(field.type))
                        for field in table_arrow.schema
                    ]
                )
            ),
            "source_url": api_url
        }
    )


@dg.asset_check(
    asset=uvm_profs_2023,
    description="Check if we have data after filtering",
)
def data_exists_check(duckdb: DuckDBResource) -> dg.AssetCheckResult:
    with duckdb.get_connection() as conn:
        query_result = conn.execute(
            f"""
            select count(*)
            from oa.raw.uvm_profs_2023
            """
        ).fetchone()

        count = query_result[0] if query_result else 0
        return dg.AssetCheckResult(
            passed=count > 0, 
            metadata={"total_records": count}
        )