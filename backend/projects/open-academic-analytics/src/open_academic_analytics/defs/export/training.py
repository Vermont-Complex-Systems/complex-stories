import dagster as dg
from dagster_duckdb import DuckDBResource
from pathlib import Path

# Path to your static data directory
STATIC_DATA_PATH = Path("../../../../../static/data") 

@dg.asset(
    kinds={"export"},
    deps=["change_point_analysis"], 
    group_name="export"
)
def training_parquet(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """Export final training data with all required columns matching the expected schema"""
    
    with duckdb.get_connection() as conn:
        conn.execute(f"""
            COPY (
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
        ) TO '{STATIC_DATA_PATH}/training.parquet' (FORMAT PARQUET)
        """)

        return dg.MaterializeResult(
            metadata={
                "export_path": str(STATIC_DATA_PATH / "training.parquet"),
            }
        )