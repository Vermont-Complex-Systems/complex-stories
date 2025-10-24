import pandas as pd

df = pd.read_parquet("academic-research-groups.parquet")

df_new = pd.read_csv("../import/uvm_salaries_2023.csv")

# on the website, missing from the newly scrape data
# set(df.payroll_name) - set(df_new.payroll_name)

# newly scraped not on the website
# set(df_new.payroll_name) - set(df.payroll_name)

df_combined = pd.concat([df, df_new], axis=0).sort_values(["payroll_name", "id"])

df_combined = df_combined.drop_duplicates(subset=["payroll_name"]).reset_index(drop=True).drop(columns=['id'], axis=1)

df_combined = df_combined[df_new.columns]

df_combined.to_csv("../import/uvm_salaries_2023.csv", index=False)

