import dagster as dg
from dagster_duckdb import DuckDBResource
import numpy as np
import arviz as az
from cmdstanpy import CmdStanModel
from pathlib import Path

@dg.asset(
    kinds={"transform"},
    deps=["training_dataset"],
    group_name="modelling"
)
def change_point_analysis(duckdb: DuckDBResource) -> dg.MaterializeResult:
    """Add Bayesian change point analysis (changing_rate) to training dataset using database data"""

    with duckdb.get_connection() as conn:
        # Get the training data from the database
        training_df = conn.execute("""
            SELECT * FROM oa.transform.training_dataset
            ORDER BY name, pub_year
        """).fetchdf()

        dg.get_dagster_logger().info(f"Processing Bayesian change point analysis for {len(training_df)} records across {training_df['name'].nunique()} authors")

        # Configure CmdStan to use conda installation
        import cmdstanpy
        cmdstanpy.set_cmdstan_path('/users/j/s/jstonge1/miniconda3/bin/cmdstan')

        # Load the Stan model
        stan_file_path = Path(__file__).parent / "stan" / "change_point02.stan"
        model = CmdStanModel(stan_file=str(stan_file_path))

        # Initialize changing_rate storage
        changing_rates = {}
        successful_analyses = 0
        failed_analyses = 0

        # Process each author individually
        for name in training_df['name'].unique():
            author_data = training_df[training_df['name'] == name].copy()

            if len(author_data) < 3:  # Need minimum data points for Bayesian analysis
                # For authors with insufficient data, use simple fallback
                for _, row in author_data.iterrows():
                    changing_rates[(name, row['pub_year'])] = float(row['prop_younger'])
                failed_analyses += 1
                continue

            try:
                # Prepare data for Stan model (following original script pattern)
                years = author_data['pub_year'].tolist()
                younger_counts = author_data['younger'].astype(int).tolist()

                # Stan model expects data in specific format
                stan_data = {
                    "T": len(years),
                    "D": younger_counts
                }

                # Run MCMC sampling
                fit = model.sample(data=stan_data, show_progress=False)
                fit_az = az.InferenceData(posterior=fit.draws_xr())
                post = fit_az.posterior
                trace = post.stack(draws=("chain", "draw"))

                # Calculate switchpoint probabilities (following original script)
                ys = [np.exp(_[-1]) for _ in trace['lp'].to_numpy()]
                ys = np.array(ys)
                ys = np.round(ys/np.sum(ys), 3)

                # Find the most likely switchpoint
                switchpoint = years[np.argmax(ys)]

                # Calculate changing rates for each year
                for year in years:
                    idx = year < switchpoint
                    changing_rate = float(np.mean(np.where(idx, trace["e"], trace["l"])))
                    changing_rates[(name, year)] = changing_rate

                successful_analyses += 1

            except Exception as e:
                # Fallback for failed Bayesian analysis
                dg.get_dagster_logger().warning(f"Bayesian analysis failed for {name}: {str(e)[:100]}. Using fallback.")
                for _, row in author_data.iterrows():
                    changing_rates[(name, row['pub_year'])] = float(row['prop_younger'])
                failed_analyses += 1

        # Apply changing rates back to the dataframe
        training_df['changing_rate'] = training_df.apply(
            lambda row: changing_rates.get((row['name'], row['pub_year']), 0.0),
            axis=1
        )

        # Round changing_rate to 3 decimal places
        training_df['changing_rate'] = training_df['changing_rate'].round(3)

        # Save the final training dataset back to DuckDB
        conn.execute("CREATE OR REPLACE TABLE oa.transform.training_final AS SELECT * FROM training_df")

        dg.get_dagster_logger().info(f"Completed Bayesian change point analysis. Final dataset has {len(training_df)} records.")
        dg.get_dagster_logger().info(f"Successful Bayesian analyses: {successful_analyses}, Failed (used fallback): {failed_analyses}")

        return dg.MaterializeResult(
            metadata={
                "record_count": int(len(training_df)),
                "unique_authors": int(training_df['name'].nunique()),
                "successful_bayesian_analyses": int(successful_analyses),
                "failed_analyses": int(failed_analyses),
                "avg_changing_rate": float(training_df['changing_rate'].mean()),
                "description": "Training dataset with Bayesian change point analysis (changing_rate) calculated from database data",
            }
        )