import dagster as dg
from dagster_duckdb import DuckDBResource

@dg.asset(
        description="📋 Load UVM Professors 2023 dataset from Complex Stories FastAPI backend (now with consistent data)",
        kinds={"duckdb"},
    )
def uvm_profs_2023(duckdb: DuckDBResource) -> dg.MaterializeResult:
    
    with duckdb.get_connection() as conn:
        # Create schemas
        conn.execute("CREATE SCHEMA IF NOT EXISTS oa")
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.execute("CREATE SCHEMA IF NOT EXISTS cache")
        conn.execute("CREATE SCHEMA IF NOT EXISTS transform")

        # params
        payroll_year=2023
        ipeds_id=231174
        api_url= f"https://api.complexstories.uvm.edu/datasets/academic-research-groups?inst_iped_id={ipeds_id}&year={payroll_year}"
        # Use the exact same SQL as frontend version
        row_count = conn.execute(
            f"""
            CREATE OR REPLACE TABLE oa.raw.uvm_profs_2023 as (
                SELECT 
                    is_prof, 
                    group_size, 
                    perceived_as_male, 
                    host_dept AS department, 
                    college, 
                    has_research_group, 
                    'https://openalex.org/' || oa_uid AS ego_author_id, 
                    group_url, 
                    CAST(first_pub_year AS INTEGER) as first_pub_year,
                    payroll_name, 
                    position
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