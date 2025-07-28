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
                    professor_oa_uid,
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
                pd.professor_oa_uid as uvm_professor_id,
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
            WHERE auth.author_oa_id != pd.professor_oa_uid  -- Exclude self-collaborations
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


@dg.asset_check(
    asset=yearly_collaborations,
    description="Verify collaboration data makes sense",
)
def collaboration_data_check(duckdb: DuckDBResource) -> dg.AssetCheckResult:
    """Check for data quality issues in the collaboration pairs"""
    
    with duckdb.get_connection() as conn:
        # Check for potential issues
        issues = conn.execute("""
            SELECT 
                -- Basic counts
                COUNT(*) as total_records,
                COUNT(CASE WHEN coauthor_name IS NULL OR coauthor_name = '' THEN 1 END) as missing_coauthor_names,
                COUNT(CASE WHEN nb_coauthors < 2 THEN 1 END) as papers_with_too_few_coauthors,
                COUNT(CASE WHEN nb_coauthors > 50 THEN 1 END) as papers_with_many_coauthors,
                
                -- Suspicious patterns
                COUNT(CASE WHEN uvm_professor_name = coauthor_name THEN 1 END) as potential_self_collaborations,
                COUNT(CASE WHEN publication_year < 1950 OR publication_year > 2025 THEN 1 END) as suspicious_years,
                
                -- Institution data availability
                COUNT(CASE WHEN coauthor_institutions_json IS NOT NULL 
                           AND coauthor_institutions_json != '[]' THEN 1 END) as with_institution_data,
                           
                -- Check for duplicates
                COUNT(*) - COUNT(DISTINCT (work_id, uvm_professor_id, coauthor_id)) as potential_duplicates
                
            FROM oa.main.coauthor_collaborations
        """).fetchone()
        
        # Get examples of suspicious cases
        suspicious_examples = conn.execute("""
            SELECT 
                'Large collaboration' as issue_type,
                uvm_professor_name,
                coauthor_name,
                publication_year,
                nb_coauthors
            FROM oa.main.coauthor_collaborations
            WHERE nb_coauthors > 50
            
            UNION ALL
            
            SELECT 
                'Potential self-collab' as issue_type,
                uvm_professor_name,
                coauthor_name,
                publication_year,
                nb_coauthors
            FROM oa.main.coauthor_collaborations
            WHERE uvm_professor_name = coauthor_name
            
            LIMIT 10
        """).fetchall()
    
    total_records, missing_names, too_few_coauthors, many_coauthors, self_collabs, suspicious_years, with_institutions, duplicates = issues
    
    # Determine if there are serious issues
    serious_issues = (
        duplicates > 0 or
        missing_names > total_records * 0.1 or  # More than 10% missing names
        self_collabs > 0
    )
    
    return dg.AssetCheckResult(
        passed=not serious_issues,
        metadata={
            "total_records": total_records,
            "missing_coauthor_names": missing_names,
            "papers_too_few_coauthors": too_few_coauthors,
            "papers_many_coauthors": many_coauthors,
            "potential_self_collaborations": self_collabs,
            "suspicious_publication_years": suspicious_years,
            "records_with_institution_data": with_institutions,
            "institution_data_percentage": round((with_institutions / total_records) * 100, 1) if total_records > 0 else 0,
            "potential_duplicates": duplicates,
            "suspicious_examples": [
                f"{ex[0]}: {ex[1]} + {ex[2]} ({ex[3]}, {ex[4]} coauthors)"
                for ex in suspicious_examples
            ] if suspicious_examples else []
        }
    )