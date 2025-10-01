import dagster as dg
from dagster_duckdb import DuckDBResource
import pandas as pd
from shared.clients.complex_stories_api import ComplexStoriesAPIResource

def import_filtered_data_to_duckdb(api_data: dict, duckdb: DuckDBResource, payroll_year: int, inst_ipeds_id: int):
    # Convert API data to DataFrame
    df = pd.DataFrame(api_data['data'])

    # Filter the data
    filtered_df = df[
        (df['payroll_year'].astype(int) == payroll_year) &
        (df['inst_ipeds_id'].astype(int) == inst_ipeds_id) &
        (df['oa_uid'].notna())
    ].copy()

    # Transform the data
    filtered_df['ego_author_id'] = 'https://openalex.org/' + filtered_df['oa_uid'].astype(str)
    filtered_df['department'] = filtered_df['host_dept']
    filtered_df['first_pub_year'] = pd.to_numeric(filtered_df['first_pub_year'], errors='coerce').astype('Int64')

    # Select and rename columns to match expected schema
    final_df = filtered_df[[
        'is_prof', 'group_size', 'perceived_as_male', 'department',
        'college', 'has_research_group', 'ego_author_id', 'group_url',
        'first_pub_year', 'payroll_name', 'position', 'notes'
    ]]

    with duckdb.get_connection() as conn:
        # Create schemas
        conn.execute("CREATE SCHEMA IF NOT EXISTS oa")
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.execute("CREATE SCHEMA IF NOT EXISTS cache")
        conn.execute("CREATE SCHEMA IF NOT EXISTS transform")

        # Insert data using pandas DataFrame
        conn.execute("CREATE OR REPLACE TABLE oa.raw.uvm_profs_2023 AS SELECT * FROM final_df")

        row_count = len(final_df)


@dg.asset(
        description="📋 Load UVM Professors 2023 dataset from Complex Stories FastAPI backend",
        kinds={"duckdb"},
    )
def uvm_profs_2023(
    duckdb: DuckDBResource,
    complex_stories_api: ComplexStoriesAPIResource
) -> dg.MaterializeResult:
    # Fetch data from FastAPI backend with filters
    api_data = complex_stories_api.get_academic_research_groups(
        year=2023,
        inst_ipeds_id=231174
    )

    # Process and load into DuckDB
    import_filtered_data_to_duckdb(
        api_data=api_data,
        duckdb=duckdb,
        payroll_year=2023,
        inst_ipeds_id=231174
    )
    
    # Get schema and stats for metadata
    with duckdb.get_connection() as conn:
        # Get record count
        count_result = conn.execute("""
            SELECT COUNT(*) FROM oa.raw.uvm_profs_2023
        """).fetchone()

        # Get sample of ego_author_id formats to verify URL prefix
        sample_ids = conn.execute("""
            SELECT ego_author_id
            FROM oa.raw.uvm_profs_2023
            LIMIT 3
        """).fetchall()

        # Get table schema using PyArrow
        table_arrow = conn.execute("SELECT * FROM oa.raw.uvm_profs_2023 LIMIT 0").arrow()

    sample_id_list = [row[0] for row in sample_ids]

    return dg.MaterializeResult(
        metadata={
            "record_count": count_result[0] if count_result else 0,
            "table_schema": dg.MetadataValue.table_schema(
                dg.TableSchema(
                    columns=[
                        dg.TableColumn(field.name, str(field.type))
                        for field in table_arrow.schema
                    ]
                )
            ),
            "sample_ego_author_ids": dg.MetadataValue.text(", ".join(sample_id_list[:3])),
            "source_url": f"{complex_stories_api.base_url}/datasets/academic-research-groups",
            "filters_applied": f"payroll_year=2023, inst_ipeds_id=231174"
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