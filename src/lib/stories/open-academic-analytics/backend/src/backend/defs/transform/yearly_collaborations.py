import dagster as dg
from dagster_duckdb import DuckDBResource
from pathlib import Path

# Path to your static data directory
STATIC_DATA_PATH = Path("../../../../../static/data") 

@dg.asset(
    kinds={"duckdb"},
    deps=["paper_parquet"],
    key=["target", "main", "yearly_collaborations"]
)
def yearly_collaborations(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """
    Extract collaboration pairs and aggregate them by year.
    
    Creates two tables:
    1. Raw collaboration pairs (one row per UVM professor + coauthor + paper)
    2. Yearly aggregation (one row per UVM professor + coauthor + year)
    """
    
    with duckdb.get_connection() as conn:
        
        # Get the paper parquet path
        paper_parquet_path = STATIC_DATA_PATH / "paper.parquet"
        
        conn.execute(f"""
                     CREATE OR REPLACE TABLE oa.transform.yearly_collaborations AS
WITH paper_data AS (
    SELECT DISTINCT 
        id,
        ego_author_id,
        ego_display_name,
        publication_year,
        publication_date,
        nb_coauthors
    FROM read_parquet('{paper_parquet_path}')
),
coauthor_collaborations AS (
    SELECT 
        -- Paper identifiers
        pd.id,
        pd.publication_year,
        pd.publication_date,
        pd.nb_coauthors,
        
        -- UVM professor info
        pd.ego_author_id,
        pd.ego_display_name,
        
        -- Coauthor info from authorships
        auth.author_id as coauthor_id,
        auth.author_display_name as coauthor_display_name,
        auth.author_position,
        auth.is_corresponding,
        
        -- Raw institution data
        auth.institutions as coauthor_institutions,
        auth.raw_affiliation_strings
    FROM paper_data pd 
    JOIN oa.raw.authorships auth ON pd.id = auth.work_id
    WHERE auth.author_id != pd.ego_author_id  -- Exclude self-collaborations
)
SELECT 
    ego_author_id,
    ego_display_name,
    coauthor_id,
    coauthor_display_name,
    publication_year,
    MIN(publication_date) as publication_date,
    COUNT(*) as yearly_collabo,
    MAX(nb_coauthors) as nb_coauthors
FROM coauthor_collaborations
GROUP BY 
    ego_author_id, 
    ego_display_name,
    coauthor_id, 
    coauthor_display_name,
    publication_year
                     """)
    
    return dg.MaterializeResult(
        metadata={
            'input_file': paper_parquet_path            
        }
    )


