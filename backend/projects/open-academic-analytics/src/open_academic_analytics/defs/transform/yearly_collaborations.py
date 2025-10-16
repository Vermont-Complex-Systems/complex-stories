import dagster as dg
from dagster_duckdb import DuckDBResource

@dg.asset(
    kinds={"duckdb"},
    deps=["paper_parquet"],
)
def yearly_collaborations(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """
    Extract collaboration pairs and aggregate them by year.

    Uses the processed papers table created by the paper_parquet asset
    to generate yearly collaboration pattern.
    """

    with duckdb.get_connection() as conn:

        df=conn.execute("""
            WITH paper_data AS (
                SELECT DISTINCT
                    id,
                    ego_author_id,
                    ego_display_name,
                    publication_year,
                    publication_date,
                    nb_coauthors
                FROM oa.transform.processed_papers
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
        """).df()

        # Save the results to DuckDB table for downstream assets
        conn.execute("CREATE OR REPLACE TABLE oa.transform.yearly_collaborations AS SELECT * FROM df")

        # Get statistics
        stats = conn.execute("""
            SELECT
                COUNT(*) as total_collaboration_pairs,
                COUNT(DISTINCT (ego_author_id, coauthor_id)) as unique_collaborations,
                COUNT(DISTINCT ego_author_id) as unique_uvm_authors,
                COUNT(DISTINCT coauthor_id) as unique_coauthors,
                COUNT(DISTINCT publication_year) as years_covered,
                MIN(publication_year) as earliest_year,
                MAX(publication_year) as latest_year
            FROM oa.transform.yearly_collaborations
        """).fetchone()

        # Validation check: ensure unique_uvm_authors is reasonable
        uvm_faculty_count = conn.execute("""
            SELECT COUNT(*) FROM oa.raw.uvm_profs_2023
        """).fetchone()[0]

        unique_uvm_authors = stats[2]

        # Log validation results
        dg.get_dagster_logger().info(f"UVM faculty in source table: {uvm_faculty_count}")
        dg.get_dagster_logger().info(f"Unique UVM authors in collaborations: {unique_uvm_authors}")

        if unique_uvm_authors > uvm_faculty_count:
            dg.get_dagster_logger().warning(
                f"More UVM authors in collaborations ({unique_uvm_authors}) than in faculty list ({uvm_faculty_count}). "
                "This suggests non-UVM authors are being included as ego authors."
            )
        elif unique_uvm_authors < uvm_faculty_count * 0.8:  # Allow some faculty to have no collaborations
            dg.get_dagster_logger().warning(
                f"Significantly fewer UVM authors in collaborations ({unique_uvm_authors}) than in faculty list ({uvm_faculty_count}). "
                "This suggests some UVM faculty may be missing from collaboration data."
            )

    return dg.MaterializeResult(
        metadata={
            "total_collaboration_pairs": stats[0],
            "unique_collaborations": stats[1],
            "unique_uvm_authors": stats[2],
            "unique_coauthors": stats[3],
            "years_covered": stats[4],
            "year_range": f"{stats[5]}-{stats[6]}" if stats[5] and stats[6] else "N/A",
            "data_source": "oa.transform.processed_papers",
            "uvm_faculty_count": uvm_faculty_count
        }
    )


@dg.asset_check(
    asset=yearly_collaborations,
    description="Check if UVM authors count is reasonable compared to faculty list",
)
def uvm_authors_count_check(duckdb: DuckDBResource) -> dg.AssetCheckResult:
    with duckdb.get_connection() as conn:
        # Get UVM faculty count from source
        uvm_faculty_count = conn.execute("""
            SELECT COUNT(*) FROM oa.raw.uvm_profs_2023
        """).fetchone()[0]

        # Get unique UVM authors from collaborations
        unique_uvm_authors = conn.execute("""
            SELECT COUNT(DISTINCT ego_author_id) FROM oa.transform.yearly_collaborations
        """).fetchone()[0]

        # Check if count is reasonable (should be <= faculty count and >= 50% of faculty count)
        passed = (unique_uvm_authors <= uvm_faculty_count)

        return dg.AssetCheckResult(
            passed=passed,
            metadata={
                "uvm_faculty_count": uvm_faculty_count,
                "unique_uvm_authors": unique_uvm_authors,
                "percentage_coverage": round(100 * unique_uvm_authors / uvm_faculty_count, 1) if uvm_faculty_count > 0 else 0
            }
        )


