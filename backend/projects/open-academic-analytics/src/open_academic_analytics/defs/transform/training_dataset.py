import dagster as dg
from dagster_duckdb import DuckDBResource

@dg.asset(
    kinds={"transform"},
    deps=["yearly_collaborations", "coauthor_institutions"], 
    group_name="modelling"
)
def training_dataset(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """Create training dataset by aggregating coauthor data into wide format with all required features"""
    
    with duckdb.get_connection() as conn:
        # Schemas are auto-initialized by InitDuckDBResource
        
        # Check if yearly_collaborations table exists, if not, throw helpful error
        try:
            conn.execute("SELECT COUNT(*) FROM oa.transform.yearly_collaborations LIMIT 1")
        except Exception as e:
            raise Exception(f"yearly_collaborations table not found. Please materialize the yearly_collaborations asset first. Error: {e}")
        
        # Create the main training dataset with all the required columns
        conn.execute("""
            CREATE OR REPLACE TABLE oa.transform.training_dataset AS 
            WITH coauthor_base AS (
                SELECT 
                    yc.ego_author_id as aid,
                    yc.ego_display_name as name,
                    yc.publication_year as pub_year,
                    yc.ego_age as author_age,
                    ci_uvm.primary_institution as institution,
                    
                    -- Coauthor information
                    yc.coauthor_display_name,
                    yc.coauthor_age,
                    yc.age_category,
                    yc.yearly_collabo,
                    yc.all_times_collabo,
                    yc.shared_institutions,
                    
                    -- UVM professor metadata
                    prof.is_prof,
                    prof.group_size,
                    prof.perceived_as_male,
                    prof.department as host_dept,
                    prof.college,
                    prof.has_research_group,
                    prof.group_url,
                    prof.first_pub_year,
                    prof.payroll_name,
                    prof.position,
                    prof.notes
                    
                FROM oa.transform.yearly_collaborations yc
                LEFT JOIN oa.raw.uvm_profs_2023 prof 
                    ON yc.ego_author_id = prof.ego_author_id
                LEFT JOIN oa.transform.coauthor_institutions ci_uvm 
                    ON yc.ego_author_id = ci_uvm.id
                    AND yc.publication_year = ci_uvm.publication_year
                
                -- Only include UVM professors with valid data
                WHERE prof.ego_author_id IS NOT NULL
                    AND yc.ego_display_name IS NOT NULL
                    AND yc.age_category IS NOT NULL
                    AND yc.age_category != 'unknown'
            ),
            
            -- Create wide format for age categories
            age_category_wide AS (
                SELECT 
                    aid, name, pub_year, author_age, institution,
                    is_prof, group_size, perceived_as_male, host_dept, college,
                    has_research_group, group_url, first_pub_year, payroll_name, position, notes,
                    
                    -- Age category counts
                    SUM(CASE WHEN age_category = 'older' THEN yearly_collabo ELSE 0 END) as older,
                    SUM(CASE WHEN age_category = 'same' THEN yearly_collabo ELSE 0 END) as same,
                    SUM(CASE WHEN age_category = 'younger' THEN yearly_collabo ELSE 0 END) as younger,
                    
                    -- Shared institution collaborations
                    SUM(CASE WHEN shared_institutions IS NOT NULL THEN yearly_collabo ELSE 0 END) as shared_inst_collabs
                    
                FROM coauthor_base
                GROUP BY 
                    aid, name, pub_year, author_age, institution,
                    is_prof, group_size, perceived_as_male, host_dept, college,
                    has_research_group, group_url, first_pub_year, payroll_name, position, notes
            ),
            
            -- Calculate acquaintance relationships (existing vs new collaborations)
            acquaintance_data AS (
                SELECT 
                    aid, name, pub_year,
                    SUM(CASE 
                        WHEN all_times_collabo > yearly_collabo THEN yearly_collabo 
                        ELSE 0 
                    END) as existing_collab,
                    SUM(CASE 
                        WHEN all_times_collabo = yearly_collabo THEN yearly_collabo 
                        ELSE 0 
                    END) as new_collab
                FROM coauthor_base
                GROUP BY aid, name, pub_year
            ),
            
            -- Get paper counts from paper data
            paper_counts AS (
                SELECT 
                    ego_author_id as aid,
                    ego_display_name as name,
                    publication_year as pub_year,
                    COUNT(*) as nb_papers
                FROM oa.transform.yearly_collaborations
                GROUP BY ego_author_id, ego_display_name, publication_year
            )
            
            SELECT 
                acw.*,
                
                -- Acquaintance features
                COALESCE(aq.existing_collab, 0) as existing_collab,
                COALESCE(aq.new_collab, 0) as new_collab,
                
                -- Calculated metrics
                (acw.older + acw.same + acw.younger) as counts,
                CASE 
                    WHEN (acw.older + acw.same + acw.younger) > 0 
                    THEN ROUND(acw.younger::FLOAT / (acw.older + acw.same + acw.younger), 3)
                    ELSE 0 
                END as prop_younger,
                (acw.older + acw.same + acw.younger) as total_coauth,
                
                -- Paper counts
                COALESCE(pc.nb_papers, 0) as nb_papers,
                
                -- Placeholder for density (to be calculated separately)
                0.0 as density,
                
                -- Use aid as oa_uid (they should be the same)
                acw.aid as oa_uid
                
            FROM age_category_wide acw
            LEFT JOIN acquaintance_data aq 
                ON acw.aid = aq.aid AND acw.name = aq.name AND acw.pub_year = aq.pub_year
            LEFT JOIN paper_counts pc
                ON acw.aid = pc.aid AND acw.name = pc.name AND acw.pub_year = pc.pub_year
            
            WHERE (acw.older + acw.same + acw.younger) > 0  -- Only include years with collaborations
            ORDER BY acw.name, acw.pub_year
        """)

        return dg.MaterializeResult(
            metadata={
                "description": "Training dataset with wide format collaboration data",
            }
        )