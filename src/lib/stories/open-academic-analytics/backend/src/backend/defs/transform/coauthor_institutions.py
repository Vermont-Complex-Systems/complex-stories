import dagster as dg
from dagster_duckdb import DuckDBResource


@dg.asset(
    kinds={"duckdb"},
    deps=["uvm_publications"],
    key=["target", "main", "coauthor_institutions"]
)
def coauthor_institutions(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """
    Process coauthor institution data to determine primary institution for each coauthor.
    
    Parses the JSON institution data from collaborations and finds the most frequently
    used institution for each coauthor across all their papers.
    """
    
    with duckdb.get_connection() as conn:
        # Create the yearly coauthor institutions table directly from authorships
        conn.execute("""
            CREATE OR REPLACE TABLE oa.main.coauthor_institutions AS
            WITH yearly_institution_counts AS (
                SELECT 
                    a.author_oa_id as coauthor_id,
                    a.author_display_name as coauthor_name,
                    p.publication_year,
                    CASE 
                        WHEN a.institutions IS NOT NULL 
                            AND a.institutions != '[]' 
                            AND JSON_ARRAY_LENGTH(a.institutions) > 0
                        THEN JSON_EXTRACT_STRING(a.institutions, '$[0].display_name')
                        ELSE 'Unknown'
                    END as institution_name,
                    COUNT(*) as institution_count_in_year
                FROM oa.main.authorships a
                JOIN oa.main.publications p ON a.work_id = p.id
                GROUP BY 
                    a.author_oa_id,
                    a.author_display_name,
                    p.publication_year,
                    CASE 
                        WHEN a.institutions IS NOT NULL 
                            AND a.institutions != '[]' 
                            AND JSON_ARRAY_LENGTH(a.institutions) > 0
                        THEN JSON_EXTRACT_STRING(a.institutions, '$[0].display_name')
                        ELSE 'Unknown'
                    END
            ),
            
            -- Filter to only known institutions for tie-breaking
            known_institutions AS (
                SELECT * FROM yearly_institution_counts
                WHERE institution_name != 'Unknown'
            ),
            
            max_counts AS (
                SELECT 
                    coauthor_id,
                    coauthor_name,
                    publication_year,
                    MAX(institution_count_in_year) as max_count
                FROM known_institutions
                GROUP BY coauthor_id, coauthor_name, publication_year
            ),
            
            tied_institutions AS (
                SELECT 
                    ki.coauthor_id,
                    ki.coauthor_name,
                    ki.publication_year,
                    STRING_AGG(ki.institution_name, ' & ' ORDER BY ki.institution_name) as primary_institution
                FROM known_institutions ki
                JOIN max_counts mc ON 
                    ki.coauthor_id = mc.coauthor_id 
                    AND ki.publication_year = mc.publication_year
                    AND ki.institution_count_in_year = mc.max_count
                GROUP BY ki.coauthor_id, ki.coauthor_name, ki.publication_year
            ),
            
            -- Fallback to 'Unknown' only if no known institutions exist for that author-year
            fallback_unknown AS (
                SELECT 
                    yic.coauthor_id,
                    yic.coauthor_name,
                    yic.publication_year,
                    'Unknown' as primary_institution
                FROM yearly_institution_counts yic
                WHERE yic.institution_name = 'Unknown'
                  AND NOT EXISTS (
                      SELECT 1 FROM known_institutions ki 
                      WHERE ki.coauthor_id = yic.coauthor_id 
                        AND ki.publication_year = yic.publication_year
                  )
                GROUP BY yic.coauthor_id, yic.coauthor_name, yic.publication_year
            )
            
            SELECT * FROM tied_institutions
            UNION ALL
            SELECT * FROM fallback_unknown
        """)
        
        # Get statistics
        stats = conn.execute("""
            SELECT 
                COUNT(DISTINCT (coauthor_id, publication_year)) as total_coauthor_years,
                COUNT(DISTINCT coauthor_id) as unique_coauthors,
                COUNT(DISTINCT publication_year) as years_covered,
                COUNT(CASE WHEN primary_institution != 'Unknown' THEN 1 END) as with_known_institution,
                COUNT(DISTINCT primary_institution) as unique_institutions
            FROM oa.main.coauthor_institutions
        """).fetchone()
        
        # Get examples of institution changes over time
        mobility_examples = conn.execute("""
            SELECT 
                coauthor_name,
                COUNT(DISTINCT primary_institution) as institution_changes,
                STRING_AGG(DISTINCT primary_institution, ' → ' ORDER BY primary_institution) as institutions
            FROM oa.main.coauthor_institutions
            WHERE primary_institution != 'Unknown'
            GROUP BY coauthor_id, coauthor_name
            HAVING COUNT(DISTINCT primary_institution) > 1
            ORDER BY institution_changes DESC
            LIMIT 5
        """).fetchall()
    
    return dg.MaterializeResult(
        metadata={
            "total_coauthor_years": stats[0],
            "unique_coauthors": stats[1], 
            "years_covered": stats[2],
            "with_known_institution": stats[3],
            "unknown_institution_percentage": round((stats[0] - stats[3]) / stats[0] * 100, 1) if stats[0] > 0 else 0,
            "unique_institutions": stats[4],
            
            "institution_mobility_examples": [
                f"{ex[0]}: {ex[1]} institutions ({ex[2]})" 
                for ex in mobility_examples
            ] if mobility_examples else []
        }
    )
