import os
import pandas as pd
import numpy as np
import arviz as az
from cmdstanpy import CmdStanModel

import dagster as dg
from dagster import MaterializeResult, MetadataValue
from config import config

@dg.asset(
    deps=["training_dataset"],
    group_name="model",
    description="🌐 Model fitting",
    # This will only run when upstream dependencies are updated
    automation_condition=dg.AutomationCondition.eager()
)
def change_point():
    input_file = config.data_processed_path / config.training_data_file
    output_file = config.data_export_path / config.training_data_file
    stan_file = config.stan_model_dir + "/change_point02.stan"
    
    dat = pd.read_parquet(input_file)

    model = CmdStanModel(stan_file=stan_file)

    out = {}
    for name in dat.name.unique():
        dat_author = dat[dat['name'] == name]
        
        nb_collabs = dat_author.younger.astype(int)
        years = dat_author.pub_year.tolist()

        fit = model.sample(data={"T": len(years), "D": nb_collabs.to_list()})
        fit_az = az.InferenceData(posterior=fit.draws_xr())
        post = fit_az.posterior
        trace = post.stack(draws=("chain", "draw"))
                
        ys = [np.exp(_[-1]) for _ in trace['lp'].to_numpy()] 
        ys = np.round(ys/np.sum(ys), 3)

        switchpoint = years[np.argmax(ys)]
        for year in years:
            idx = year < switchpoint
            out[(name, year)] = np.mean(np.where(idx, trace["e"], trace["l"]))
        
        dat['changing_rate'] = dat.apply(lambda row: out.get((row['name'], row['pub_year']), None), axis=1)

    dat.to_parquet(output_file, index=False)

    return MaterializeResult(
        metadata={
            "collaboration_relationships": MetadataValue.int(len(dat)),
            "input_file": MetadataValue.path(str(input_file)),
            "output_file": MetadataValue.path(str(output_file)),
            "dashboard_ready": MetadataValue.bool(True),
            "research_value": MetadataValue.md(
                "**Final collaboration network dataset** ready for interactive visualization. "
                "Enables exploration of mentorship patterns, career-stage effects, and "
                "institutional collaboration networks."
            )
        }
    )