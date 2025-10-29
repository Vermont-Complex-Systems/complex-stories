import dagster as dg
from dagster_duckdb import DuckDBResource

@dg.asset(
    kinds={"transform"},
    deps=["training_dataset"], 
    group_name="modelling"
)
def change_point_analysis(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """Add change point analysis (changing_rate) to training dataset"""
    
    with duckdb.get_connection() as conn:
        # Schema is auto-initialized by InitDuckDBResource
        # For now, implement a simple trend-based changing_rate calculation
        # This can be replaced with proper Bayesian change point analysis later
        conn.execute("""
            CREATE OR REPLACE TABLE oa.transform.training_with_changepoint AS 
            SELECT 
                *,
                -- Simple changing rate: smoothed collaboration trend
                -- This is a placeholder - can be replaced with Bayesian change point analysis
                AVG(younger) OVER (
                    PARTITION BY name 
                    ORDER BY pub_year 
                    ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
                ) as changing_rate_raw,
                
                -- Add age category based on collaboration patterns
                CASE 
                    WHEN prop_younger > 0.6 THEN 'younger'
                    WHEN prop_younger > 0.3 THEN 'same'
                    ELSE 'older'
                END as age_category
                
            FROM oa.transform.training_dataset
        """)
        
        # Round the changing_rate and finalize
        conn.execute("""
            CREATE OR REPLACE TABLE oa.transform.training_final AS 
            SELECT 
                *,
                ROUND(changing_rate_raw, 3) as changing_rate
            FROM oa.transform.training_with_changepoint
        """)

        return dg.MaterializeResult(
            metadata={
                "description": "Training dataset with change point analysis (changing_rate)",
            }
        )