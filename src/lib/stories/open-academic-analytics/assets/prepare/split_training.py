import pandas as pd
import numpy as np
import json
from collections import Counter
from itertools import combinations
import dagster as dg
from dagster import MaterializeResult, MetadataValue
from config import config

def load_coauthor_data(filepath):
    """Load coauthor parquet file"""
    return pd.read_parquet(filepath)

def filter_missing_age_category(df):
    """Remove rows with missing age_category"""
    return df[~df.age_category.isna()].reset_index(drop=True)

def coarsen_age_categories(df):
    """Convert age categories to more coarse-grained categories"""
    df = df.copy()
    df['age_category'] = np.where(df.age_category == 'much_younger', 'younger', df.age_category)
    df['age_category'] = np.where(df.age_category == 'much_older', 'older', df.age_category)
    return df

def create_coauthor_wide_format(df):
    """Create wide format from coauthor data"""
    counts = df.groupby(['aid', 'name', 'age_category', 'pub_year']).size().reset_index(name='counts')
    return (counts.pivot(index=['name', 'aid', 'pub_year'], columns='age_category', values='counts')
            .fillna(0)
            .reset_index()
            .sort_values(['name', 'aid', 'pub_year']))

def add_author_metadata(df_wide, df_coauthor_clean):
    """Add author age and institution from coauthor data"""
    # Add author age
    unique_author_age = df_coauthor_clean[~df_coauthor_clean[['name', 'pub_year']].duplicated()][['name', 'pub_year', 'author_age']]
    df_wide = df_wide.merge(unique_author_age, on=['name', 'pub_year'], how='left')
    
    # Add institution
    unique_institution = df_coauthor_clean[~df_coauthor_clean[['name', 'pub_year']].duplicated()][['name', 'pub_year', 'institution']]
    df_wide = df_wide.merge(unique_institution, on=['name', 'pub_year'], how='left')
    
    return df_wide

def add_acquaintance_features(df_wide, df_coauthor_clean):
    """Add acquaintance relationship features"""
    counts_new_acq = df_coauthor_clean.groupby(['name', 'acquaintance', 'pub_year']).size().reset_index(name='counts')
    df_wide_new_acq = (counts_new_acq.pivot(index=['name', 'pub_year'], columns='acquaintance', values='counts')
                       .fillna(0)
                       .reset_index()
                       .sort_values(['name', 'pub_year']))
    return df_wide.merge(df_wide_new_acq, on=['name', 'pub_year'], how='left')

def add_shared_institution_features(df_wide, df_coauthor_clean):
    """Add shared institution features"""
    df_shared_inst = df_coauthor_clean[~df_coauthor_clean.shared_institutions.isna()]
    counts_shared_inst = df_shared_inst.groupby(['name', 'age_category', 'pub_year', 'shared_institutions']).size().reset_index(name='counts')
    return df_wide.merge(counts_shared_inst, on=['name', 'pub_year'], how='left', suffixes=('', '_shared_inst'))

def calculate_coauthor_metrics(df_wide):
    """Calculate coauthor proportions and totals"""
    df_wide = df_wide.copy()
    df_wide['prop_younger'] = df_wide.younger / (df_wide.older + df_wide.younger + df_wide.same)
    df_wide['total_coauth'] = df_wide.older + df_wide.younger + df_wide.same
    return df_wide

def add_paper_features(df_wide, df_papers):
    """Add paper count features"""
    counts_papers = df_papers[['name', 'pub_year']].groupby(['name', 'pub_year']).size().reset_index(name='nb_papers')
    return df_wide.merge(counts_papers, how="left", on=['name', 'pub_year'])

def flatten(l):
    return [item for sublist in l for item in sublist]
    
def calc_density(df, df_pap, df_wide):
    out = {}
    for auth in df_pap.name.unique():
        # auth='Laurent Hébert‐Dufresne'
        df_coauths_mat = df_pap.loc[df_pap.name == auth, ['wid', 'name', 'authors', 'pub_year']]\
                            .assign(authors = lambda x: x.authors.map(lambda x: x.split(", ")))\
                            .explode('authors')\
                            .sort_values('pub_year')\
                            .query(f'authors != "{auth}"')\
                            .rename(columns={'authors': 'coauth_name'})
        
        df_coauths_mat = df_coauths_mat.merge(df[['name', 'pub_year', 'coauth_name', 'age_category']], on=['name', 'pub_year', 'coauth_name'])
        
        def extract_comb_coauths(x):
            return list(combinations(df_coauths_mat.loc[df_coauths_mat.wid == x, ['wid', 'pub_year', 'coauth_name']].coauth_name, 2))
        i=0
        years = df_coauths_mat.pub_year.unique()
        while i < len(years):
            year = years[i:i+3]
            tmp_df = df_coauths_mat[(df_coauths_mat.age_category == 'younger') & (df_coauths_mat.pub_year.isin(year.tolist()))]
            uniq_younger_coauthors = tmp_df.coauth_name.unique()
            comb_auths = [extract_comb_coauths(wid) for wid in tmp_df.wid.unique()]
            count_auths = Counter(flatten(comb_auths))
            
            if len(count_auths) > 0:
                df_long = pd.DataFrame(count_auths.keys(), columns=['source', 'target']).assign(nb_collab = count_auths.values())
                # df_long = df_long[(df_long.source.isin(uniq_younger_coauthors)) | df_long.target.isin(uniq_younger_coauthors)]
                df_long = df_long[(df_long.source.isin(uniq_younger_coauthors)) & df_long.target.isin(uniq_younger_coauthors)]
                df_long[['source', 'target']] = pd.DataFrame(np.sort(df_long[['source', 'target']], axis=1))    
                aggregated_df = df_long.groupby(['source', 'target'], as_index=False)['nb_collab'].sum()
                matrix = aggregated_df.pivot_table(index='source', columns='target', values='nb_collab', fill_value=0)
                
                # calculate density
                non_zero_edges = np.count_nonzero(np.triu(matrix, k=1))
                num_nodes = matrix.shape[0]
                total_possible_edges = (num_nodes * (num_nodes - 1)) / 2
                density = np.round((non_zero_edges / total_possible_edges), 3) if total_possible_edges > 0 else 0
                for yr in year:
                    out[(auth, yr)] = density
            else:
                for yr in year:
                    out[(auth, yr)] = 0
            
            i += 3
    return df_wide.apply(lambda row: out.get((row['name'], row['pub_year']), None), axis=1)

def add_network_features(df_wide, df_coauthor_clean, df_papers):
    """Calculate network density features"""
    df_wide = df_wide.copy()
    df_wide['density'] = calc_density(df_coauthor_clean, df_papers, df_wide)
    return df_wide
    
@dg.asset(
    deps=["coauthor", "paper", "author", "uvm_profs_2023"],
    group_name="model",
    description="🌐 Prepare collaboration data for model fitting"  
)
def training_dataset():
    """Create training dataset by combining coauthor, paper, and annotation data"""
    coauthor_file = config.data_export_path / config.coauthor_output_file
    paper_file = config.data_export_path / config.paper_output_file
    researchers_file = config.data_raw_path / config.uvm_profs_2023_file
    output_file = config.data_processed_path / config.training_data_file

    # Load and clean the original coauthor data
    df_coauthor_clean = (
        load_coauthor_data(coauthor_file)
        .pipe(filter_missing_age_category)
        .pipe(coarsen_age_categories)
    )
    
    # Load paper data for later use
    df_papers = pd.read_parquet(paper_file)    

    # Execute the training dataset creation pipeline
    training_dataset = (
        df_coauthor_clean
        .pipe(create_coauthor_wide_format)
        .pipe(add_author_metadata, df_coauthor_clean)
        .pipe(add_acquaintance_features, df_coauthor_clean)
        .pipe(add_shared_institution_features, df_coauthor_clean)
        .pipe(calculate_coauthor_metrics)
        .pipe(add_paper_features, df_papers)
        .pipe(add_network_features, df_coauthor_clean, df_papers)
    )

    df_annots = pd.read_csv(researchers_file, sep="\t")
    
    # Merge with annotations (inner join - only keep researchers in annotation data)
    training_dataset = training_dataset.merge(df_annots, how="inner", left_on=['aid'], right_on=['oa_uid'])
    training_dataset = training_dataset.drop(['oa_display_name'], axis=1)
    
    training_dataset.to_parquet(output_file)


    return MaterializeResult(
        metadata={
            "input_coauthor": MetadataValue.path(str(coauthor_file)),
            "input_uvm_profs_2023": MetadataValue.path(str(researchers_file)),
            "input_paper_file": MetadataValue.path(str(paper_file)),
            "output_file": MetadataValue.path(str(output_file))
        }
    )