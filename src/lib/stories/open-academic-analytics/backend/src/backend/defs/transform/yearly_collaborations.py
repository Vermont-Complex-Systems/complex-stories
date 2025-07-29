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
        
        # Create the raw collaborations table
        conn.execute(f"""
            CREATE OR REPLACE TABLE oa.main.coauthor_collaborations AS
            WITH paper_data AS (
                SELECT DISTINCT 
                    work_id,
                    ego_aid,
                    name,
                    publication_year,
                    publication_date,
                    nb_coauthors
                FROM read_parquet('{paper_parquet_path}')
            )
            SELECT 
                -- Paper identifiers
                pd.work_id,
                pd.publication_year,
                pd.publication_date,
                pd.nb_coauthors,
                
                -- UVM professor info
                pd.ego_aid as uvm_professor_id,
                pd.name as uvm_professor_name,
                
                -- Coauthor info from authorships
                auth.author_oa_id as coauthor_id,
                auth.author_display_name as coauthor_name,
                auth.author_position,
                auth.is_corresponding,
                
                -- Raw institution data (we'll process this in next asset)
                auth.institutions as coauthor_institutions_json,
                auth.raw_affiliation_strings
                
            FROM paper_data pd
            JOIN oa.main.authorships auth ON pd.work_id = auth.work_id
            WHERE replace(auth.author_oa_id, 'https://openalex.org/', '') != pd.ego_aid  -- Exclude self-collaborations
        """)
        
        # Create the yearly aggregation table
        conn.execute("""
            CREATE OR REPLACE TABLE oa.main.yearly_collaborations AS
            SELECT 
                uvm_professor_id,
                uvm_professor_name,
                coauthor_id,
                coauthor_name,
                publication_year,
                MIN(publication_date) as publication_date,
                COUNT(*) as yearly_collabo,
                MAX(nb_coauthors) as nb_coauthors
            FROM oa.main.coauthor_collaborations
            GROUP BY 
                uvm_professor_id, 
                uvm_professor_name,
                coauthor_id, 
                coauthor_name,
                publication_year
        """)
    
    return dg.MaterializeResult(
        metadata={
            'input_file': paper_parquet_path            
        }
    )


