import dagster as dg
from dagster_duckdb import DuckDBResource

def import_filtered_url_to_duckdb(url: str, duckdb: DuckDBResource, table_name: str, payroll_year: int, inst_ipeds_id: int):
    column_order = [
        'oa_display_name', 'is_prof', 'group_size', 'perceived_as_male', 
        'host_dept', 'college', 'has_research_group', 'oa_uid', 'group_url', 'first_pub_year',
        'payroll_name', 'position', 'notes'
    ]

    columns_str = ', '.join(column_order)
     
    with duckdb.get_connection() as conn:
        row_count = conn.execute(
            f"""
            CREATE OR REPLACE TABLE {table_name} as (
                SELECT {columns_str} FROM read_parquet('{url}')
                WHERE payroll_year = {payroll_year} AND inst_ipeds_id = {inst_ipeds_id} AND oa_uid IS NOT NULL
            )
            """
        ).fetchone()
        assert row_count is not None
        row_count = row_count[0]


@dg.asset(
        description="📋 Load UVM Professors 2023 dataset from Complex Stories' dataset repository",
        kinds={"duckdb"}, 
        key=["target", "main", "uvm_profs_2023"]
    )
def uvm_profs_2023(duckdb: DuckDBResource) -> None:
    import_filtered_url_to_duckdb(
        url="https://vermont-complex-systems.github.io/datasets/data/academic-research-groups.parquet",
        duckdb=duckdb,
        table_name="oa.main.uvm_profs_2023",
        payroll_year=2023,
        inst_ipeds_id=231174
    )


@dg.asset_check(
    asset=uvm_profs_2023,
    description="Check if we have data after filtering",
)
def data_exists_check(duckdb: DuckDBResource) -> dg.AssetCheckResult:
    table_name = "oa.main.uvm_profs_2023"

    with duckdb.get_connection() as conn:
        query_result = conn.execute(
            f"""
            select count(*)
            from {table_name}
            """
        ).fetchone()

        count = query_result[0] if query_result else 0
        return dg.AssetCheckResult(
            passed=count > 0, 
            metadata={"total_records": count}
        )